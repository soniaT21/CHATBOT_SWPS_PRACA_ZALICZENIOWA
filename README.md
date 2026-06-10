# CHATBOT SWPS

To projekt-zabawka (ale na serio) dla studentów **psychologii** i
**informatyki** SWPS. Pokażemy Ci, jak zbudować własnego **chatbota AI**, który
gada po polsku i potrafi **sam doszukiwać sobie wiedzy** — u nas z
[Repozytorium naukowego SWPS](https://share.swps.edu.pl). Ta sztuczka nazywa się
**RAG** i za chwilę wyjaśnimy, o co w niej chodzi.

Projekt jest celowo prosty, żebyś mógł(a) go odpalić, zrozumieć i **przerobić na
swój temat**. Nie musisz być doświadczonym programistą — przeprowadzimy Cię krok po kroku.

> Coś jest niejasne? Zajrzyj do [Słowniczka](#słowniczek-pojęć) na końcu — bez
> żargonu, po ludzku.

---

## Spis treści

- [CHATBOT SWPS](#chatbot-swps)
  - [Spis treści](#spis-treści)
  - [Co właściwie zbudujemy](#co-właściwie-zbudujemy)
  - [Co dostajesz na jaką ocenę](#co-dostajesz-na-jaką-ocenę)
  - [Czego potrzebujesz na start](#czego-potrzebujesz-na-start)
  - [Jak zacząć (fork i praca w grupie)](#jak-zacząć-fork-i-praca-w-grupie)
  - [Odpalamy](#odpalamy)
  - [Jak to jest poskładane (architektura)](#jak-to-jest-poskładane-architektura)
  - [RAG — czyli skąd bot bierze wiedzę](#rag--czyli-skąd-bot-bierze-wiedzę)
  - [Co siedzi w środku czatu](#co-siedzi-w-środku-czatu)
  - [Co gdzie leży (struktura plików)](#co-gdzie-leży-struktura-plików)
  - [Zrób własnego bota na inny temat](#zrób-własnego-bota-na-inny-temat)
  - [Coś nie działa?](#coś-nie-działa)
  - [Co można dorzucić później](#co-można-dorzucić-później)
  - [Słowniczek pojęć](#słowniczek-pojęć)

---

## Co właściwie zbudujemy

Stronę z okienkiem czatu. Piszesz pytanie, bot odpowiada po polsku. A jeśli
pytanie dotyczy publikacji albo badań SWPS, bot **sam** zagląda do repozytorium,
znajduje pasujące pozycje i odpowiada na ich podstawie — z linkiem do źródła.

Mniej więcej tak:

> **Ty:** Podaj jakąś publikację SWPS o psychologii pozytywnej.
> **Bot:** „Pozytywna psychologia pracy i organizacji" (2026), red. Paweł
> Fortuna, Agnieszka Czerw — podręcznik o psychologii pozytywnej w pracy.
> Link: https://share.swps.edu.pl/handle/swps/2351

Pod maską są dwie współpracujące części:

- **Frontend** — to, co widzisz w przeglądarce. Zrobione w **Next.js** (React)
  i ostylowane **Bootstrapem**.
- **Backend** — mózg działający na serwerze. Napisany w **Pythonie** (**Flask**),
  rozmawia z modelem **Claude** i z repozytorium SWPS.

---

## Co dostajesz na jaką ocenę

Projekt możesz oddać w dwóch wariantach — wybierz, jak daleko chcesz zajść:

| Wariant | Co robisz | Ocena |
|---|---|:---:|
| **Podstawowy** | Czat oparty **tylko na własnej bazie wiedzy** w plikach `.md` (wiedza wjeżdża prosto do promptu). | **4** |
| **Rozszerzony** | Czat sięgający do **zewnętrznej bazy / repozytorium** (np. API SWPS) i doszukujący wiedzy na żądanie — czyli **RAG**. | **5** |

Dobra wiadomość: ten projekt pokazuje **oba** warianty, więc możesz zacząć od
prostszego i spokojnie go rozbudować:

- Wiedza w [knowledge/general.md](apps/api/knowledge/general.md) → to Twoja **4**.
- Wyszukiwanie w repozytorium SWPS (RAG) → to Twoja **5**.

W pliku [apps/api/.env](apps/api/.env.example) jest przełącznik `RAG_ENABLED` —
ustawiasz `true` albo `false`. Możesz więc najpierw oddać wersję z samą bazą
`.md`, a potem dokleić zewnętrzne źródło.

**Które pliki edytujesz w ramach projektu** (resztą nie musisz się przejmować):

| Plik | Co tu zmieniasz | Przydatne do |
|---|---|---|
| [apps/api/knowledge/general.md](apps/api/knowledge/general.md) | Twoja baza wiedzy (treść, którą bot zna na pamięć) | ocena **4** i **5** |
| [apps/api/app/claude.py](apps/api/app/claude.py) | charakter bota (`_INSTRUCTIONS_BASE`) i opis narzędzia (`_TOOLS`) | ocena **4** i **5** |
| [apps/api/app/repository.py](apps/api/app/repository.py) | zewnętrzne źródło wiedzy (repozytorium / inne API) | ocena **5** |
| [apps/api/.env](apps/api/.env.example) | konfiguracja: klucz API, `RAG_ENABLED` | obie |
| [apps/web/app/chat.tsx](apps/web/app/chat.tsx) | interfejs czatu: powitanie, teksty, wygląd | obie |
| [apps/web/app/page.tsx](apps/web/app/page.tsx) | tytuł i układ strony głównej | obie |

> Pozostałych plików (np. `__init__.py`, `routes/`, konfiguracji monorepo)
> zwykle nie trzeba ruszać — działają „z pudełka".

> I tak czy siak liczy się jakość: czy bot trafnie odpowiada, czy prompt jest
> dobrze napisany, czy interfejs jest czytelny i czy wiedza ma sens.

---

## Czego potrzebujesz na start

Zainstaluj sobie to:

| Co | Wersja | Po co | Sprawdzisz tak |
|---|---|---|---|
| **Git** | dowolna | pobranie kodu (fork + clone) | `git --version` |
| **Node.js** | 18+ | uruchamia frontend i narzędzia | `node --version` |
| **Python** | 3.9+ | uruchamia backend | `python3 --version` (Windows: `python --version` lub `py --version`) |
| **Yarn (Corepack)** | Yarn 4 | menedżer paczek | `corepack enable` (raz) |
| **Klucz API Anthropic** | — | dostęp do Claude | weź na [console.anthropic.com](https://console.anthropic.com) |

> **Klucz API to jak hasło do Claude** — jest płatny od zużycia. Dlatego
> **nigdy go nie wklejaj do kodu ani nie wrzucaj na GitHuba.** Trzymamy go w
> pliku `.env`, którego Git i tak nie zapisuje.
>
> Uwaga!!! Na potrzeby tego projektu dzielę się własnym kluczem API do Claude. Budżet powinien wystarczyć dla wszystkich, gdyby jednak pojawiła się informacja o wyczerpanym limicie dajcie prosze znać: mkieruzel@swps.edu.pl

---

## Jak zacząć (fork i praca w grupie)

**Możecie pracować w grupach 2-3 osobowych** (albo solo — jak wolisz). Przy
pracy zespołowej najprościej tak: jedna osoba robi forka, a pozostałe dołącza
jako współpracowników.

**Krok 1 — zrób forka.** Wejdź na repozytorium projektu i kliknij **Fork**
(prawy górny róg). Powstanie Twoja własna kopia na Twoim koncie GitHub:

> https://github.com/marcinkieruzel/CHATBOT_SWPS_PRACA_ZALICZENIOWA

**Krok 2 — sklonuj forka na swój komputer** (podmień `TWOJA-NAZWA` na swoją
nazwę użytkownika GitHub):

```bash
git clone https://github.com/TWOJA-NAZWA/CHATBOT_SWPS_PRACA_ZALICZENIOWA.git
cd CHATBOT_SWPS_PRACA_ZALICZENIOWA
```

**Krok 3 — dodaj resztę zespołu** (przy pracy w grupie). Na GitHubie w swoim
forku: **Settings → Collaborators → Add people** i wpisz nazwy kolegów/koleżanek.
Od tej pory pracujecie na jednym repozytorium.

> Wskazówka: żeby nie wchodzić sobie w drogę, dobrze jest pracować na osobnych
> gałęziach (`git checkout -b moja-czesc`) i łączyć zmiany przez *pull requesty*.

Gdy masz już kod u siebie — przejdź do [Odpalamy](#odpalamy).

---

## Odpalamy

```bash
# 1. Zainstaluj zależności
yarn install

# 2. Ustaw swój klucz API
cp apps/api/.env.example apps/api/.env
#    otwórz apps/api/.env i wklej klucz:
#    ANTHROPIC_API_KEY=sk-ant-...

# 3. Odpal wszystko naraz (frontend + backend)
yarn dev
```

Teraz wejdź na **http://localhost:3000** i gadaj.

Co się dzieje w tle:

- frontend rusza na porcie **3000**,
- backend na porcie **5000** — przy **pierwszym** odpaleniu sam zakłada wirtualne
  środowisko Pythona (`.venv`) i instaluje paczki. To chwilę trwa, ale tylko za
  pierwszym razem. Spokojnie.

Kilka przydatnych komend:

```bash
yarn dev --filter=web    # sam frontend
yarn dev --filter=api    # sam backend
yarn build               # wersja produkcyjna
```

Chcesz sprawdzić backend bez przeglądarki?

```bash
curl -X POST http://localhost:5001/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Cześć, kim jesteś?"}'
```

---

## Jak to jest poskładane (architektura)

Całość to **monorepo** (jedno repo z kilkoma aplikacjami) ogarniane przez
[Turborepo](https://turborepo.dev). Obrazek wart tysiąca słów:

```
┌──────────────────────────────────────────────────────────────────┐
│  TWOJA PRZEGLĄDARKA                                                │
│  apps/web — Next.js + React + Bootstrap        http://localhost:3000
│  Okno czatu: apps/web/app/chat.tsx                                │
└───────────────────────────┬──────────────────────────────────────┘
                            │  POST /chat { message, history }   (fetch)
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  BACKEND — Flask (Python)                      http://localhost:5001
│  routes/chat.py  →  claude.py                                     │
│   • prompt + knowledge/general.md                                 │
│   • pętla „tool use" (bot sam decyduje, czy szukać)              │
└───────────┬───────────────────────────────────┬──────────────────┘
            │                                   │
            ▼                                   ▼
┌────────────────────────────┐   ┌─────────────────────────────────────┐
│  Claude (Anthropic)        │   │  Repozytorium SWPS (DSpace)         │
│  model: claude-opus-4-8    │   │  share.swps.edu.pl/server/api       │
│  rozumie i pisze tekst     │   │  wyszukiwanie publikacji (to „R"    │
│                            │   │  w RAG)                             │
└────────────────────────────┘   └─────────────────────────────────────┘
```

Kto za co odpowiada:

| Warstwa | Technologia | Gdzie | Robota |
|---|---|---|---|
| Frontend | Next.js, React, Bootstrap | [apps/web](apps/web) | okno czatu, wysyłanie pytań |
| Backend | Python, Flask | [apps/api](apps/api) | logika, rozmowa z Claude i repozytorium |
| Model | Claude (Anthropic) | chmura | rozumie pytanie, pisze odpowiedź |
| Wiedza | DSpace (SWPS) | chmura | podaje fakty/publikacje na żądanie |
| Wspólne paczki | TypeScript | [packages/](packages) | wspólna konfiguracja i komponenty |

A tak wygląda droga jednego pytania:

1. Piszesz wiadomość w czacie ([apps/web/app/chat.tsx](apps/web/app/chat.tsx)).
2. Frontend wysyła ją (`POST /chat`) razem z historią rozmowy do backendu.
3. Backend ([routes/chat.py](apps/api/app/routes/chat.py)) przekazuje ją do
   [claude.py](apps/api/app/claude.py), który pyta Claude.
4. Claude decyduje: odpowiedzieć od razu czy **najpierw poszukać** w
   repozytorium (wtedy woła narzędzie `szukaj_w_repozytorium`).
5. Backend wykonuje wyszukiwanie ([repository.py](apps/api/app/repository.py)) i
   oddaje wyniki Claude, a ten układa końcową odpowiedź.
6. Backend odsyła `{"reply": "..."}`, a frontend dorysowuje dymek. Gotowe!

---

## RAG — czyli skąd bot bierze wiedzę

**RAG = Retrieval-Augmented Generation** (generowanie wspomagane wyszukiwaniem).
Brzmi groźnie, jest proste.

Model jak Claude wie mnóstwo, ale ma trzy słabości:

- **nie zna** Twoich lokalnych danych (np. wewnętrznych dokumentów),
- jego wiedza ma **datę graniczną** (nie zna najnowszych publikacji),
- czasem **zmyśla** z pełną pewnością siebie (tzw. *halucynacje*).

RAG to lekarstwo — w trzech krokach:

1. **R — szukamy** w wiarygodnym źródle fragmentów pasujących do pytania (u nas:
   publikacje z repozytorium SWPS).
2. **A — doklejamy** te fragmenty do zapytania do modelu.
3. **G — generujemy** odpowiedź **opartą na nich**, z podaniem źródła.

Efekt? Odpowiedzi są **aktualne, oparte na faktach i sprawdzalne** (jest link).

W tym projekcie wiedza działa na dwóch poziomach:

- **Wiedza stała** — plik [knowledge/general.md](apps/api/knowledge/general.md)
  jest dołączany zawsze. Idealny na krótkie, zawsze potrzebne info (kim jest bot,
  podstawowe FAQ).
- **Wiedza na żądanie** — szczegółów bot **nie nosi ze sobą**. Dopiero gdy
  trzeba, woła narzędzie wyszukiwania w repozytorium. To właśnie „R" z RAG-a.

Takie doszukiwanie na żądanie (po angielsku *tool use* / *function calling*) jest
oszczędne: do modelu trafia tylko to, co naprawdę potrzebne, a nie cała baza.

> **Na większą skalę** używa się **embeddingów** (wyszukiwanie po znaczeniu, nie
> po słowach) — o tym w [pomysłach na później](#co-można-dorzucić-później).

---

## Co siedzi w środku czatu

Najważniejsze pliki backendu:

| Plik | Za co odpowiada |
|---|---|
| [routes/chat.py](apps/api/app/routes/chat.py) | endpoint `POST /chat`: sprawdza dane, łapie błędy |
| [claude.py](apps/api/app/claude.py) | rozmowa z Claude + **pętla tool-use** |
| [knowledge.py](apps/api/app/knowledge.py) | wczytuje główny plik wiedzy (`general.md`) |
| [repository.py](apps/api/app/repository.py) | wyszukuje w repozytorium SWPS |
| [routes/health.py](apps/api/app/routes/health.py) | `GET /health` — czy backend żyje |

Parę pojęć, które warto kojarzyć:

- **Prompt systemowy** — instrukcja dla bota („jesteś asystentem SWPS, mów po
  polsku…"). Siedzi w [claude.py](apps/api/app/claude.py).
- **Prompt caching** — stałą część promptu oznaczamy jako „buforowalną", żeby
  kolejne pytania były tańsze i szybsze (działa zauważalnie przy większej,
  niezmiennej treści).
- **Historia rozmowy** — frontend dosyła wcześniejsze wiadomości, dzięki czemu
  bot „pamięta" kontekst.
- **Pętla tool-use** — jeśli bot poprosi o wyszukanie, backend je robi i oddaje
  wynik, aż bot wyda finalną odpowiedź.

---

## Co gdzie leży (struktura plików)

```
CHATBOT_SWPS/
├── apps/
│   ├── web/                      # FRONTEND — Next.js (okno czatu)
│   │   └── app/
│   │       ├── page.tsx          # strona główna z czatem
│   │       ├── chat.tsx          # komponent czatu (wysyła pytania do API)
│   │       └── layout.tsx        # układ + Bootstrap
│   ├── api/                      # BACKEND — Flask (Python)
│   │   ├── app/
│   │   │   ├── __init__.py        # fabryka aplikacji Flask + CORS
│   │   │   ├── claude.py          # rozmowa z Claude + pętla tool-use
│   │   │   ├── knowledge.py       # wczytanie general.md
│   │   │   ├── repository.py      # wyszukiwarka repozytorium SWPS
│   │   │   └── routes/
│   │   │       ├── chat.py        # POST /chat
│   │   │       └── health.py      # GET /health
│   │   ├── knowledge/
│   │   │   └── general.md         # główna wiedza (zawsze w kontekście)
│   │   ├── requirements.txt       # paczki Pythona
│   │   ├── dev.mjs / build.mjs     # skrypty Node (venv + Flask, wieloplatformowe)
│   │   ├── .env.example            # wzór konfiguracji (skopiuj do .env)
│   │   └── README.md               # szczegóły backendu
│   └── docs/                      # druga, przykładowa apka Next.js (opcjonalna)
├── packages/                     # wspólne paczki (UI, konfiguracje)
├── turbo.json                    # konfiguracja zadań Turborepo
└── package.json                  # skrypty i workspaces monorepo
```

---

## Zrób własnego bota na inny temat

Najfajniejsze: ten projekt to gotowy **szablon**. Chcesz bota o czymś innym
(„asystent zdrowia psychicznego", „przewodnik po lekturach", „pomoc dla
pierwszego roku")? Lecimy:

**1. Zmień charakter bota.** W [claude.py](apps/api/app/claude.py) edytuj
`_INSTRUCTIONS_BASE` — napisz, kim jest, jakim tonem mówi i w jakim języku.

**2. Podmień wiedzę stałą.** Wrzuć swoją treść do
[knowledge/general.md](apps/api/knowledge/general.md) (FAQ, regulamin, opis
tematu). To trafia do bota przy każdym pytaniu.

**3. Wybierz źródło wiedzy „na żądanie".** Masz opcje:

- **Najprościej:** niech narzędzie czyta wybrane pliki `.md`/`.txt` z dysku.
- **Inne API:** podmień [repository.py](apps/api/app/repository.py) na klienta
  innego serwisu (biblioteka, pogoda, Twój własny endpoint). Zostaw funkcję
  `search_as_text(zapytanie)` — reszta kodu się nie zmienia.
- **Po znaczeniu (embeddingi):** dla dużych zbiorów — patrz
  [pomysły na później](#co-można-dorzucić-później).

**4. Dostrój narzędzie.** W [claude.py](apps/api/app/claude.py) zmień opis
narzędzia w `_TOOLS` i instrukcję, **kiedy** bot ma go używać. Opis to instrukcja
dla modelu — pisz konkretnie.

**5. Ubierz to ładnie.** W [chat.tsx](apps/web/app/chat.tsx) i
[page.tsx](apps/web/app/page.tsx) zmień tytuł, powitanie, teksty przycisków i
kolory (klasy Bootstrap).

**6. Sprawdź.** Odpal `yarn dev`, zadaj pytanie „z tematu" (powinno odpalić
wyszukiwanie) i „ogólne" (nie powinno). Zobacz, czy odpowiedzi mają źródła.

> **Psychologia + informatyka = dobry duet.** Osoby z psychologii świetnie
> zaprojektują *prompt*, dobór wiedzy i ton (to realna umiejętność — *prompt
> engineering*), a osoby z informatyki ogarną źródło danych i interfejs.

**Pomysły na temat:**

- Bot tłumaczący pojęcia z psychologii na podstawie publikacji SWPS.
- Przewodnik po ofercie kierunku / sylabusach (wiedza z plików).
- Bot odpowiadający na pytania o konkretne badanie lub artykuł.
- Asystent „pierwszej pomocy" ze statystyki / metodologii.

---

## Coś nie działa?

| Co widzisz | Co zrobić |
|---|---|
| Błąd o `ANTHROPIC_API_KEY` | Brak klucza. Skopiuj `apps/api/.env.example` do `apps/api/.env` i wklej klucz. |
| `Address already in use` (port 3000/5000) | Port zajęty. Zamknij to, co go trzyma, albo zmień port. |
| Wyszukiwanie repozytorium zwraca błąd 403 | Cloudflare blokuje zapytania bez nagłówka przeglądarki — w projekcie jest to już ogarnięte w `repository.py`. |
| `yarn dev` nie widzi Pythona | Zainstaluj Python 3.9+ i sprawdź, że `python3` działa w terminalu (na Windows: `python` lub `py`). |
| Pierwsze odpalenie backendu trwa wieki | Spokojnie — zakłada się `.venv` i instalują paczki. Kolejne starty są szybkie. |
| Dziwny błąd o „workspace root"/Turbopack | Projekt używa linkera `node-modules` (plik `.yarnrc.yml`). Odpal `yarn install` jeszcze raz. |

---

## Co można dorzucić później

- **Streaming** — odpowiedź pojawia się „na żywo", literka po literce.
- **Embeddingi + baza wektorowa** — wyszukiwanie po znaczeniu zamiast po słowach
  (świetne przy dużej liczbie dokumentów).
- **Pełne PDF-y** — analiza całych publikacji, nie tylko abstraktów.
- **Pamięć między sesjami** — zapamiętywanie rozmów użytkownika.
- **Cytowania i przypisy** — ładne, ustrukturyzowane odnośniki do źródeł.
- **Logowanie / role** — kto ma dostęp, statystyki użycia.

---

## Słowniczek pojęć

| Pojęcie | Po ludzku |
|---|---|
| **API** | Sposób, w jaki programy gadają ze sobą przez sieć. |
| **Endpoint** | Konkretny „adres" w API, np. `/chat`, który coś robi. |
| **Frontend / Backend** | Część w przeglądarce / część na serwerze. |
| **LLM (model językowy)** | Model AI, który rozumie i pisze tekst (tu: Claude). |
| **Prompt** | Instrukcja/zapytanie wysyłane do modelu. |
| **Prompt systemowy** | Stała instrukcja mówiąca, kim jest i jak ma się zachowywać bot. |
| **Token** | Najmniejszy kawałek tekstu, w którym model „liczy" wejście/wyjście. |
| **RAG** | Generowanie wspomagane wyszukiwaniem (opisane [wyżej](#rag--czyli-skąd-bot-bierze-wiedzę)). |
| **Tool use / function calling** | Model prosi program o zrobienie czegoś (np. wyszukania). |
| **Halucynacja** | Gdy model pewnie podaje nieprawdę. |
| **Monorepo** | Jedno repo z wieloma aplikacjami/paczkami. |
| **venv** | Wirtualne środowisko Pythona — odizolowane paczki projektu. |
| **CORS** | Pozwala przeglądarce wołać API z innego adresu/portu. |
| **DSpace** | Oprogramowanie repozytoriów naukowych; u nas źródło wiedzy SWPS. |

---

Tyle! Klucz API i `apps/api/.env` zostają u Ciebie (Git ich nie zapisuje).
Szczegóły techniczne backendu są w [apps/api/README.md](apps/api/README.md).

Powodzenia — i baw się dobrze przy budowaniu własnego bota!
