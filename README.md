# Chatbot SWPS — wersja podstawowa (ocena 4)

Czat z botem, który odpowiada po polsku na pytania o publikacje i badania
Uniwersytetu SWPS. W tej wersji wiedza bota pochodzi w całości z pliku
`apps/api/knowledge/general.md` i jest wstrzykiwana do promptu przy każdym
pytaniu (`RAG_ENABLED=false`).

- **Frontend:** Next.js + React + Bootstrap (`apps/web`) — port 3000
- **Backend:** Python + Flask (`apps/api`) — port 5001, rozmawia z Claude

## Wymagania

| Narzędzie | Wersja | Sprawdzisz |
|-----------|--------|------------|
| Node.js   | 18+    | `node --version` |
| Python    | 3.9+   | `python3 --version` (Windows: `python` lub `py`) |
| Yarn 4    | —      | `corepack enable` (raz) |
| Klucz API Anthropic | — | z `console.anthropic.com` |

## Uruchomienie

```bash
# 1. Zależności frontendu / monorepo
yarn install

# 2. Klucz API
cp apps/api/.env.example apps/api/.env
#    otwórz apps/api/.env i wklej swój klucz:
#    ANTHROPIC_API_KEY=sk-ant-...

# 3. Wszystko naraz (frontend + backend)
yarn dev
```

Następnie wejdź na http://localhost:3000 i pisz.

> Przy pierwszym starcie backend sam zakłada wirtualne środowisko Pythona
> (`.venv`) i instaluje paczki — to chwilę trwa, ale tylko raz.

### Przydatne komendy

```bash
yarn dev --filter=web    # sam frontend
yarn dev --filter=api    # sam backend
yarn build               # wersja produkcyjna
```

### Test backendu bez przeglądarki

```bash
curl -X POST http://localhost:5001/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Cześć, kim jesteś?"}'
```

## Co edytujesz w tym projekcie

| Plik | Co tu zmieniasz |
|------|-----------------|
| `apps/api/knowledge/general.md` | baza wiedzy bota |
| `apps/api/app/claude.py` | charakter bota (`_INSTRUCTIONS_BASE`) i opis narzędzia (`_TOOLS`) |
| `apps/api/.env` | klucz API, `RAG_ENABLED` |
| `apps/web/app/chat.tsx` | wygląd i teksty czatu |
| `apps/web/app/page.tsx` | tytuł i układ strony |

## Wersja rozszerzona (ocena 5 — RAG)

Wystarczy w `apps/api/.env` ustawić `RAG_ENABLED=true`. Bot dostanie wtedy
narzędzie `szukaj_w_repozytorium` i będzie sam doszukiwać publikacje w
repozytorium SWPS (`apps/api/app/repository.py`).

## Oszczędzanie budżetu API

Domyślny model to `claude-opus-4-8`. Aby zużywać mniej, w `apps/api/.env`
ustaw np. `CLAUDE_MODEL=claude-sonnet-4-6` lub `claude-haiku-4-5-20251001`.

## Problemy

| Co widzisz | Co zrobić |
|------------|-----------|
| Błąd o `ANTHROPIC_API_KEY` | Brak klucza — uzupełnij `apps/api/.env`. |
| `Address already in use` | Port zajęty — zamknij to, co go trzyma, lub zmień `PORT`. |
| `yarn dev` nie widzi Pythona | Zainstaluj Python 3.9+ (`python3`/`python`/`py`). |
| Pierwszy start trwa długo | To zakładanie `.venv` — kolejne starty są szybkie. |
