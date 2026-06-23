"""Rozmowa z modelem Claude.

Tu mieszka "charakter" bota (_INSTRUCTIONS_BASE), opis narzędzia (_TOOLS)
oraz logika rozmowy:

* WERSJA PODSTAWOWA (ocena 4, RAG_ENABLED=false):
  do promptu systemowego dołączamy całą bazę wiedzy z general.md
  i bot odpowiada wyłącznie na jej podstawie. Bez wyszukiwania.

* WERSJA ROZSZERZONA (ocena 5, RAG_ENABLED=true):
  dodatkowo dajemy botowi narzędzie `szukaj_w_repozytorium`. Bot sam
  decyduje, czy go użyć, a my w pętli wykonujemy wyszukiwanie i oddajemy
  mu wynik (klasyczny "tool use").
"""
import os

from anthropic import Anthropic

from .knowledge import load_general_knowledge
from .repository import search_as_text

# ----------------------------------------------------------------------------
# Konfiguracja (z pliku .env)
# ----------------------------------------------------------------------------
MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
RAG_ENABLED = os.getenv("RAG_ENABLED", "false").strip().lower() == "true"

_client = None


def _get_client() -> Anthropic:
    """Leniwie tworzy klienta Anthropic (dopiero przy pierwszym pytaniu)."""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Brak ANTHROPIC_API_KEY. Skopiuj apps/api/.env.example do "
                "apps/api/.env i wklej swój klucz API."
            )
        _client = Anthropic(api_key=api_key)
    return _client


# ----------------------------------------------------------------------------
# Charakter bota (prompt systemowy)
# ----------------------------------------------------------------------------
_INSTRUCTIONS_BASE = """\
Jesteś Asystentem SWPS — pomocnym, rzeczowym chatbotem Uniwersytetu SWPS.

Twoje zasady:
1. Odpowiadasz ZAWSZE po polsku, prostym i przyjaznym językiem.
2. Opierasz się przede wszystkim na sekcji "Baza wiedzy" poniżej. To jest
   Twoje główne źródło prawdy.
3. Jeśli pytanie dotyczy publikacji albo badań SWPS, a w bazie wiedzy
   znajdziesz pasującą pozycję — podaj jej tytuł, rok, autorów i link.
4. Jeśli czegoś nie wiesz lub nie ma tego w bazie wiedzy, powiedz to wprost.
   NIE zmyślaj tytułów, autorów ani linków.
5. Odpowiadasz zwięźle i konkretnie. Bez lania wody.
6. Gdy podajesz publikację, formatuj ją czytelnie: tytuł w cudzysłowie,
   rok, autorzy/redakcja oraz link do źródła, jeśli jest dostępny.

Jeśli masz dostępne narzędzie wyszukiwania w repozytorium, użyj go tylko
wtedy, gdy pytanie dotyczy konkretnych publikacji/badań SWPS, których nie
ma w bazie wiedzy. Do pytań ogólnych (np. "kim jesteś?") narzędzia nie używaj.\
"""

# Opis narzędzia dla modelu (używany TYLKO gdy RAG_ENABLED=true).
_TOOLS = [
    {
        "name": "szukaj_w_repozytorium",
        "description": (
            "Wyszukuje publikacje naukowe w repozytorium Uniwersytetu SWPS "
            "(SHARE / DSpace). Używaj, gdy użytkownik pyta o konkretne "
            "publikacje, artykuły, książki lub badania SWPS, a odpowiedzi nie "
            "ma w bazie wiedzy. Zwraca tytuły, autorów, rok i linki."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "zapytanie": {
                    "type": "string",
                    "description": (
                        "Słowa kluczowe do wyszukania, np. 'psychologia "
                        "pozytywna' albo 'wypalenie zawodowe'."
                    ),
                }
            },
            "required": ["zapytanie"],
        },
    }
]


def _build_system():
    """Buduje prompt systemowy: charakter bota + cała baza wiedzy.

    Stałą część oznaczamy jako "buforowalną" (prompt caching), żeby kolejne
    pytania były tańsze i szybsze.
    """
    knowledge = load_general_knowledge()
    text = _INSTRUCTIONS_BASE
    if knowledge:
        text += "\n\n# Baza wiedzy\n\n" + knowledge
    return [
        {
            "type": "text",
            "text": text,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def _sanitize_history(history):
    """Zamienia historię z frontendu na poprawną listę wiadomości.

    Anthropic wymaga, by rozmowa zaczynała się od roli 'user' i by role
    się przeplatały. Odrzucamy więc ewentualne wiadomości powitalne bota
    z początku oraz puste/niepoprawne wpisy.
    """
    czyste = []
    for turn in history or []:
        if not isinstance(turn, dict):
            continue
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            czyste.append({"role": role, "content": content})

    # Usuwamy wiodące wiadomości asystenta (np. powitanie).
    while czyste and czyste[0]["role"] == "assistant":
        czyste.pop(0)
    return czyste


def get_reply(message: str, history=None) -> str:
    """Zwraca odpowiedź bota na wiadomość użytkownika.

    message  – aktualne pytanie użytkownika
    history  – wcześniejsze wiadomości [{role, content}, ...]
    """
    client = _get_client()
    system = _build_system()

    messages = _sanitize_history(history)
    messages.append({"role": "user", "content": message})

    # Pętla tool-use: powtarzamy, dopóki model prosi o użycie narzędzia.
    while True:
        kwargs = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "system": system,
            "messages": messages,
        }
        if RAG_ENABLED:
            kwargs["tools"] = _TOOLS

        response = client.messages.create(**kwargs)

        # Jeśli model chce użyć narzędzia — wykonujemy je i wracamy do pętli.
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name == "szukaj_w_repozytorium":
                    zapytanie = (block.input or {}).get("zapytanie", "")
                    wynik = search_as_text(zapytanie)
                else:
                    wynik = f"Nieznane narzędzie: {block.name}"
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": wynik,
                    }
                )
            messages.append({"role": "user", "content": tool_results})
            continue

        # Odpowiedź końcowa: sklejamy bloki tekstowe.
        teksty = [b.text for b in response.content if b.type == "text"]
        return "\n".join(teksty).strip()
