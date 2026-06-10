"""Cienka warstwa pośrednia nad API Anthropic Claude dla endpointu czatu."""

import os

import anthropic

from app.knowledge import MAIN_KNOWLEDGE
from app.repository import search_as_text

MODEL = "claude-opus-4-8"
MAX_TOKENS = 2048
# Zabezpieczenie przed nieskończoną pętlą wywołań narzędzia.
MAX_TOOL_ITERS = 4


def _env_flag(name: str, default: bool = True) -> bool:
    """Czyta flagę typu prawda/fałsz ze zmiennej środowiskowej."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on", "tak")


# Włącznik RAG: gdy False, wyszukiwanie w repozytorium SWPS jest wyłączone —
# narzędzie nie jest przekazywane modelowi, a prompt o nim nie wspomina.
# Sterowane zmienną RAG_ENABLED w pliku .env (domyślnie włączone).
RAG_ENABLED = _env_flag("RAG_ENABLED", True)

# Część wspólna instrukcji (niezależna od RAG).
_INSTRUCTIONS_BASE = (
    "You are the CHATBOT SWPS assistant, a helpful and concise chatbot. "
    "Always respond in Polish, regardless of the language the user writes in. "
    "Answer the user directly and clearly. Respond with your final answer "
    "only — do not include exploratory reasoning or meta-commentary. "
    "Prefer information from the knowledge base below when it is relevant. "
    "Use the gangsta like language style of the 1990s Polish hip-hop, but keep it appropriate and respectful. "
)

# Dodatek instrukcji aktywny tylko, gdy RAG jest włączony.
_INSTRUCTIONS_RAG = (
    "When the question concerns SWPS research, publications, authors or "
    "academic topics, first call the `szukaj_w_repozytorium` tool to fetch "
    "matching publications, then answer based on the results and cite the "
    "source links. "
)

_INSTRUCTIONS_TAIL = (
    "If the answer is not available, answer from general knowledge and say so."
)

_INSTRUCTIONS = _INSTRUCTIONS_BASE + (_INSTRUCTIONS_RAG if RAG_ENABLED else "") + _INSTRUCTIONS_TAIL

# Narzędzie udostępniane modelowi: wyszukiwanie w repozytorium SWPS na żądanie.
# Stabilne między zapytaniami, więc nie psuje prompt cache.
_TOOLS = [
    {
        "name": "szukaj_w_repozytorium",
        "description": (
            "Przeszukuje repozytorium naukowe SWPS (DSpace) i zwraca pasujące "
            "publikacje: tytuł, autorów, rok, słowa kluczowe, abstrakt i link. "
            "Wywołaj, gdy pytanie dotyczy publikacji, badań, autorów lub tematów "
            "naukowych SWPS — zanim udzielisz odpowiedzi."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "zapytanie": {
                    "type": "string",
                    "description": "Słowa kluczowe do wyszukania (temat, autor, tytuł).",
                }
            },
            "required": ["zapytanie"],
        },
    }
]


def _build_system_prompt() -> list[dict]:
    """Instrukcje + główna baza wiedzy jako stabilny, buforowany blok promptu.

    Treść jest identyczna bajt po bajcie między zapytaniami, dzięki czemu
    prefiks może być buforowany (prompt caching). Wiedza szczegółowa nie jest
    tu wstawiana — model doczytuje ją na żądanie narzędziem wyszukiwania.
    """
    text = _INSTRUCTIONS
    if MAIN_KNOWLEDGE:
        text += f"\n\n# Baza wiedzy\n\n{MAIN_KNOWLEDGE}"
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


SYSTEM_PROMPT = _build_system_prompt()

# Jeden współdzielony klient dla wszystkich zapytań. Czyta ANTHROPIC_API_KEY ze środowiska.
_client = anthropic.Anthropic()


def generate_reply(message: str, history: list[dict] | None = None) -> str:
    """Wysyła rozmowę do Claude i zwraca tekst odpowiedzi asystenta.

    Obsługuje pętlę wywołań narzędzia: jeśli model poprosi o wyszukanie w
    repozytorium, wykonujemy je i zwracamy wynik, aż model udzieli ostatecznej
    odpowiedzi. Gdy RAG jest wyłączony (RAG_ENABLED=False), pomijamy narzędzie
    i wykonujemy zwykłe pojedyncze zapytanie. `history` to opcjonalna lista
    wcześniejszych tur jako słowniki {"role", "content"} (role "user" / "assistant").
    """
    messages = _build_messages(message, history)

    # RAG wyłączony — zwykły czat bez narzędzia wyszukiwania.
    if not RAG_ENABLED:
        response = _client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT, messages=messages
        )
        return _text(response)

    for _ in range(MAX_TOOL_ITERS):
        response = _client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=_TOOLS,
        )

        if response.stop_reason != "tool_use":
            return _text(response)

        # Wykonaj żądane wyszukiwania i dołącz wyniki jako tool_result.
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "szukaj_w_repozytorium":
                query = (block.input or {}).get("zapytanie", "")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": search_as_text(query),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    # Limit iteracji wyczerpany — wymuś odpowiedź końcową bez narzędzi.
    final = _client.messages.create(
        model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT, messages=messages
    )
    return _text(final)


def _text(response) -> str:
    """Skleja tekstowe bloki odpowiedzi w jeden ciąg."""
    return "".join(block.text for block in response.content if block.type == "text")


def _build_messages(message: str, history: list[dict] | None) -> list[dict]:
    """Normalizuje historię do poprawnej tablicy wiadomości Anthropic.

    Pomija wszystko, co nie jest turą user/assistant, oraz usuwa początkowe
    tury asystenta (pierwsza wiadomość musi pochodzić od użytkownika).
    """
    messages: list[dict] = []
    for turn in history or []:
        role = turn.get("role")
        content = turn.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            continue
        if not messages and role != "user":
            continue  # pomiń początkowe tury asystenta (np. wstępne powitanie)
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})
    return messages
