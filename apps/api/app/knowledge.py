"""Wczytywanie stałej bazy wiedzy (knowledge/general.md).

Treść tego pliku jest dołączana do promptu systemowego przy KAŻDYM
pytaniu. To jest serce wersji podstawowej (ocena 4): bot "zna na pamięć"
to, co tu wpiszesz.
"""
import os
from functools import lru_cache

# Katalog .../apps/api/knowledge
_KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge",
)


@lru_cache(maxsize=1)
def load_general_knowledge() -> str:
    """Zwraca zawartość general.md jako tekst. Wynik jest cache'owany."""
    path = os.path.join(_KNOWLEDGE_DIR, "general.md")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
