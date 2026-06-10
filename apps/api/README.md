# api — backend Flask (Python)

Backend chatbota w monorepo `CHATBOT_SWPS`. Udostępnia REST API na **porcie
5001**, z którego korzysta aplikacja frontendowa `web` (Next.js). Odpowiada za
rozmowę z modelem **Claude** (Anthropic) oraz za wyszukiwanie wiedzy „na
żądanie" w **Repozytorium naukowym SWPS** (DSpace) — czyli za wzorzec **RAG**.

> Pełny, przystępny opis całego projektu (architektura, czym jest RAG, jak
> zbudować własny) znajdziesz w [README głównym](../../README.md). Ten plik
> skupia się na samym backendzie.

---

## Spis treści

- [api — backend Flask (Python)](#api--backend-flask-python)
  - [Spis treści](#spis-treści)
  - [Wymagania](#wymagania)
  - [Uruchamianie](#uruchamianie)
    - [Przez Turborepo (zalecane)](#przez-turborepo-zalecane)
    - [Bezpośrednio (bez Turbo)](#bezpośrednio-bez-turbo)
  - [Konfiguracja (zmienne środowiskowe)](#konfiguracja-zmienne-środowiskowe)
  - [Endpointy API](#endpointy-api)
    - [`POST /chat`](#post-chat)
  - [Obsługa błędów](#obsługa-błędów)
  - [Jak działa RAG / tool use](#jak-działa-rag--tool-use)
  - [Baza wiedzy](#baza-wiedzy)
  - [Struktura katalogów](#struktura-katalogów)
  - [Zależności](#zależności)
  - [Wdrożenie produkcyjne](#wdrożenie-produkcyjne)
  - [Najczęstsze problemy](#najczęstsze-problemy)

---

## Wymagania

- **Python 3.9+** dostępny w `PATH` (sprawdź: `python3 --version`; na Windows
  `python --version` lub `py --version`).
- **Klucz API Anthropic** (`ANTHROPIC_API_KEY`) — zdobądź na
  [console.anthropic.com](https://console.anthropic.com).
- Do wyszukiwania w repozytorium SWPS **nie jest** potrzebny żaden klucz ani
  dodatkowa zależność (korzysta z publicznego API i biblioteki standardowej).

---

## Uruchamianie

### Przez Turborepo (zalecane)

Z katalogu głównego repozytorium backend uruchamia się jak każda inna aplikacja:

```bash
yarn dev --filter=api    # tylko backend
yarn dev                 # backend + frontend razem
```

Skrypty `dev`/`build` (zob. [dev.mjs](dev.mjs) / [build.mjs](build.mjs)) **same**
tworzą lokalne wirtualne środowisko Pythona (`.venv`), instalują zależności z
[requirements.txt](requirements.txt) i uruchamiają serwer deweloperski Flask.
Pierwsze uruchomienie trwa dłużej (instalacja paczek), kolejne są szybkie. Są to
skrypty Node (uruchamiane przez `node`), więc działają na Windows, macOS i Linux
bez potrzeby `bash`.

### Bezpośrednio (bez Turbo)

Przydatne przy pracy nad samym backendem:

```bash
cd apps/api
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/flask --app app run --port 5001 --debug
```

Na Windows (`cmd`/PowerShell) użyj `python` zamiast `python3` oraz katalogu
`Scripts` zamiast `bin`:

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m flask --app app run --port 5001 --debug
```

> Najprościej jednak uruchamiać `yarn dev` / `yarn build` — skrypty
> [dev.mjs](dev.mjs) / [build.mjs](build.mjs) robią to wszystko automatycznie
> i wieloplatformowo.

---

## Konfiguracja (zmienne środowiskowe)

Skopiuj wzór i uzupełnij wartości:

```bash
cp .env.example .env
```

Plik `.env` jest wczytywany automatycznie przy starcie (przez `python-dotenv`)
i **jest ignorowany przez Git** — nie trafi do repozytorium.

| Zmienna | Wymagana | Domyślnie | Opis |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | **tak** | — | Klucz dostępu do API Claude. |
| `RAG_ENABLED` | nie | `true` | Włącza/wyłącza wyszukiwanie w repozytorium SWPS (RAG). Wartości: `true/false/1/0/on/off`. |
| `CORS_ORIGIN` | nie | `http://localhost:3000` | Adres, z którego przeglądarka może wołać API (frontend `web`). |
| `FLASK_ENV` | nie | `development` | Tryb pracy Flask. |

> **Włączanie/wyłączanie RAG.** Ustaw `RAG_ENABLED=false` w `.env`, aby wyłączyć
> wyszukiwanie w repozytorium — backend działa wtedy jako zwykły czat (narzędzie
> nie jest przekazywane modelowi, a prompt o nim nie wspomina). Po zmianie
> zrestartuj serwer. Domyślnie RAG jest włączony.

> ⚠️ Nigdy nie umieszczaj klucza API w kodzie ani nie wysyłaj go do GitHuba.
> Trzymaj go wyłącznie w `.env`.

---

## Endpointy API

| Metoda | Ścieżka | Opis |
|---|---|---|
| `GET` | `/health` | Kontrola stanu → `{"status": "ok"}` |
| `POST` | `/chat` | Wiadomość użytkownika → odpowiedź asystenta |

### `POST /chat`

**Żądanie** (JSON):

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `message` | `string` | tak | Treść wiadomości użytkownika (niepusta). |
| `history` | `array` | nie | Wcześniejsze tury rozmowy dla kontekstu wielowątkowego. |

Każdy element `history` to obiekt `{"role": "user" | "assistant", "content": "..."}`.
Backend pomija nieprawidłowe wpisy oraz początkowe tury asystenta (pierwsza
wiadomość musi pochodzić od użytkownika), a nową `message` dokleja na końcu.

**Odpowiedź** (JSON): `{"reply": "..."}`

**Przykłady:**

```bash
# Proste pytanie
curl -X POST http://localhost:5001/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Cześć, kim jesteś?"}'

# Z historią rozmowy (kontekst wielowątkowy)
curl -X POST http://localhost:5001/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "A co z psychologią pracy?",
    "history": [
      {"role": "user", "content": "Opowiedz o psychologii pozytywnej."},
      {"role": "assistant", "content": "Psychologia pozytywna bada dobrostan..."}
    ]
  }'
```

Logika wywołania modelu znajduje się w [app/claude.py](app/claude.py),
a obsługa endpointu w [app/routes/chat.py](app/routes/chat.py).

---

## Obsługa błędów

Błędy zwracane są jako JSON `{"error": "..."}` z odpowiednim kodem HTTP:

| Kod | Sytuacja | Treść |
|---|---|---|
| `400` | Brak/niepuste pole `message` | „Pole „message" jest wymagane i nie może być puste" |
| `429` | Przekroczono limit zapytań API Claude | komunikat o limicie |
| `502` | Błąd uwierzytelniania (zły `ANTHROPIC_API_KEY`) lub inny błąd API Claude | komunikat o błędzie |

Wyjątki biblioteki Anthropic są obsłużone w [app/routes/chat.py](app/routes/chat.py)
(`AuthenticationError`, `RateLimitError`, `APIError`). Błąd wyszukiwania w
repozytorium **nie** przerywa rozmowy — model otrzymuje komunikat o błędzie i
informuje o tym użytkownika.

---

## Jak działa RAG / tool use

Model nie dostaje całej bazy wiedzy z góry — sam decyduje, kiedy jej potrzebuje:

1. Backend wysyła do Claude prompt systemowy (instrukcje + `general.md`) wraz z
   definicją **narzędzia** `szukaj_w_repozytorium`.
2. Jeśli pytanie dotyczy publikacji/badań SWPS, model **prosi** o wywołanie
   narzędzia, podając frazę wyszukiwania.
3. Backend wykonuje wyszukiwanie w repozytorium ([app/repository.py](app/repository.py))
   i zwraca wyniki modelowi jako `tool_result`.
4. Model formułuje odpowiedź na podstawie wyników i podaje linki do źródeł.

Pętla powtarza się aż do uzyskania ostatecznej odpowiedzi (z zabezpieczeniem
`MAX_TOOL_ITERS` w [app/claude.py](app/claude.py)). Pytania ogólne (np. „stolica
Polski") nie uruchamiają wyszukiwania.

Dodatkowo:

- **Prompt caching** — stała część promptu (instrukcje + `general.md`) jest
  oznaczona jako buforowalna; buforowanie działa zauważalnie dopiero przy
  większej, stałej treści (~4096 tokenów dla Opus 4.8).
- **Model** — domyślnie `claude-opus-4-8` (stała `MODEL` w `app/claude.py`).

---

## Baza wiedzy

- **Plik główny** [knowledge/general.md](knowledge/general.md) — zawsze trafia
  do promptu systemowego. Dobre miejsce na krótkie, zawsze potrzebne fakty
  (kim jest asystent, podstawowe FAQ).
- **Wiedza szczegółowa** — doczytywana na żądanie z repozytorium SWPS przez
  narzędzie wyszukiwania (nie jest ładowana w całości do kontekstu).

Aby zmienić wiedzę stałą, edytuj `knowledge/general.md`. Aby zmienić źródło
wiedzy na żądanie, podmień [app/repository.py](app/repository.py), zachowując
funkcję `search_as_text(zapytanie)` — reszta kodu nie wymaga zmian.

---

## Struktura katalogów

```
apps/api/
├── app/
│   ├── __init__.py      # fabryka create_app(): konfiguracja CORS + rejestracja blueprintów
│   ├── claude.py        # wywołanie Claude + pętla tool-use (RAG)
│   ├── knowledge.py     # wczytanie głównego pliku wiedzy (general.md)
│   ├── repository.py    # wyszukiwanie w repozytorium SWPS (DSpace), na żądanie
│   └── routes/
│       ├── health.py    # GET /health
│       └── chat.py      # POST /chat (walidacja + obsługa błędów)
├── knowledge/
│   └── general.md       # główna wiedza (zawsze w kontekście)
├── wsgi.py              # punkt wejścia produkcyjnego (gunicorn wsgi:app)
├── requirements.txt     # zależności Pythona
├── dev.mjs / build.mjs  # skrypty Node: tworzą .venv i uruchamiają/instalują
├── scripts/venv.mjs     # wspólna logika provisioningu .venv (wieloplatformowa)
├── .env.example         # wzór konfiguracji (skopiuj do .env)
└── package.json         # podłączenie do workspace Yarn/Turbo
```

---

## Zależności

Z [requirements.txt](requirements.txt):

| Paczka | Rola |
|---|---|
| `flask` | serwer WWW / framework REST |
| `flask-cors` | nagłówki CORS (wywołania z frontendu w przeglądarce) |
| `python-dotenv` | wczytywanie zmiennych z pliku `.env` |
| `anthropic` | oficjalny klient API Claude |

Wyszukiwanie w repozytorium SWPS korzysta wyłącznie z **biblioteki
standardowej** Pythona (`urllib`), bez dodatkowych zależności.

---

## Wdrożenie produkcyjne

Serwer deweloperski Flask **nie nadaje się** na produkcję. Użyj serwera WSGI,
np. `gunicorn`, z punktem wejścia [wsgi.py](wsgi.py):

```bash
./.venv/bin/pip install gunicorn
./.venv/bin/gunicorn --bind 0.0.0.0:5001 wsgi:app
```

Pamiętaj o ustawieniu zmiennych środowiskowych (`ANTHROPIC_API_KEY`,
`CORS_ORIGIN` wskazujący na produkcyjny adres frontendu) w środowisku
docelowym, a nie w pliku `.env` w repozytorium.

---

## Najczęstsze problemy

| Objaw | Rozwiązanie |
|---|---|
| Błąd o `ANTHROPIC_API_KEY` | Skopiuj `.env.example` do `.env` i wklej klucz. |
| `Address already in use` (port 5001) | Port zajęty — zamknij inny proces lub zmień port (`--port`). |
| Wyszukiwanie repozytorium: błąd `403` | Cloudflare blokuje domyślny `User-Agent`; jest to obsłużone nagłówkiem przeglądarki w `repository.py`. |
| Pierwsze uruchomienie długo trwa | Tworzony jest `.venv` i instalowane zależności — kolejne starty są szybkie. |
| Błąd CORS w przeglądarce | Ustaw `CORS_ORIGIN` na adres frontendu (domyślnie `http://localhost:3000`). |
