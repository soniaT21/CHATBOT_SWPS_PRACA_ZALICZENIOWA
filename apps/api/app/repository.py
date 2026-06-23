"""Wyszukiwarka repozytorium SWPS (DSpace / SHARE).

UWAGA: To jest element wersji ROZSZERZONEJ (ocena 5 / RAG).
W wersji podstawowej (ocena 4) plik nie jest używany, bo w .env
mamy RAG_ENABLED=false i bot nie dostaje narzędzia do wyszukiwania.

Interfejs, na którym opiera się reszta kodu, to funkcja
``search_as_text(zapytanie)`` -> str. Jeśli kiedyś zechcesz podmienić
źródło wiedzy (inne API, biblioteka, własny endpoint), wystarczy że
zachowasz tę funkcję, a `claude.py` nie wymaga zmian.
"""
import requests

_SEARCH_URL = "https://share.swps.edu.pl/server/api/discover/search/objects"

# Cloudflare potrafi blokować zapytania bez nagłówka przeglądarki (błąd 403),
# dlatego podszywamy się pod zwykłą przeglądarkę.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def search_as_text(zapytanie: str, limit: int = 3) -> str:
    """Szuka publikacji w repozytorium SWPS i zwraca wynik jako tekst.

    Zwracany tekst jest gotowy do wklejenia w odpowiedzi narzędzia dla
    modelu (tytuł, autorzy, rok, link). Gdy nic nie znajdzie lub wystąpi
    błąd sieci, zwraca czytelny komunikat.
    """
    zapytanie = (zapytanie or "").strip()
    if not zapytanie:
        return "Puste zapytanie — nie ma czego szukać."

    params = {"query": zapytanie, "size": limit}
    try:
        resp = requests.get(_SEARCH_URL, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        return f"Nie udało się połączyć z repozytorium SWPS: {exc}"
    except ValueError:
        return "Repozytorium zwróciło odpowiedź w nieoczekiwanym formacie."

    objects = (
        data.get("_embedded", {})
        .get("searchResult", {})
        .get("_embedded", {})
        .get("objects", [])
    )
    if not objects:
        return f"Brak wyników w repozytorium SWPS dla zapytania: {zapytanie}"

    wpisy = []
    for obj in objects[:limit]:
        item = obj.get("_embedded", {}).get("indexableObject", {})
        meta = item.get("metadata", {})

        def _pierwsza(klucz: str) -> str:
            wartosci = meta.get(klucz, [])
            return wartosci[0].get("value", "") if wartosci else ""

        tytul = _pierwsza("dc.title") or "(bez tytułu)"
        autor = _pierwsza("dc.contributor.author") or "(brak autora)"
        rok = _pierwsza("dc.date.issued")
        uuid = item.get("uuid", "")
        link = f"https://share.swps.edu.pl/items/{uuid}" if uuid else ""

        wiersz = f"- {tytul} ({rok}), {autor}"
        if link:
            wiersz += f" — {link}"
        wpisy.append(wiersz)

    return "Znalezione publikacje w repozytorium SWPS:\n" + "\n".join(wpisy)
