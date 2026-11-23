"""A script-independent sound key for matching Greek, Greeklish and transliterations."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from ._chars import GREEK_LETTERS
from .accents import fold
from .translit import PHONETIC_SCHEME, transliterate

__all__ = ["phonetic_key"]

#: Greeklish spellings on the Latin side, longest match first. Digraphs that contain "h" are
#: listed so their "h" is not read as η ("ph" is φ). A υ written as u / y after α, ε, η is the
#: v of αυ, ευ, ηυ, and "oy" is ου. A "y" before i / e is γ, as in the common English-style
#: spellings "Yiannis" (Γιάννης) and "Panayiotis" (Παναγιώτης).
_LATIN_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        "th": "th",
        "ch": "x",
        "ph": "f",
        "yi": "gi",
        "ye": "ge",
        "ks": "ks",
        "ps": "ps",
        "ou": "ou",
        "oy": "ou",
        "au": "av",
        "ay": "av",
        "eu": "ev",
        "ey": "ev",
        "hu": "iv",
        "hy": "iv",
        "8": "th",
        "3": "ks",
        "w": "o",
        "h": "i",
        "c": "k",
    }
)

#: Pairs that are one sound: the pair before them never takes their first letter ("nth" is
#: n + th, not nt + h; "ayi" is a + yi, not ay + i).
_UNITS = frozenset({"th"})
_LATIN_UNITS = frozenset({"th", "yi", "ye"})

#: Spellings that sound the same, applied to both scripts until nothing changes.
_SOUNDS: Mapping[str, str] = MappingProxyType(
    {
        "th": "th",
        "ei": "i",
        "oi": "i",
        "yi": "i",
        "ai": "e",
        "af": "av",
        "au": "av",
        "ef": "ev",
        "eu": "ev",
        "if": "iv",
        "ng": "g",
        "gk": "g",
        "gg": "g",
        "nx": "gx",
        "mp": "b",
        "nt": "d",
        "ch": "x",
        "ou": "u",
        "y": "i",
        "w": "o",
    }
)


def _rewrite(text: str, table: Mapping[str, str], units: frozenset[str] = _UNITS) -> str:
    """Rewrite ``text`` with ``table``, longest match first, never splitting one of ``units``."""
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        two = text[i : i + 2]
        if len(two) == 2 and two in table and text[i + 1 : i + 3] not in units:
            out.append(table[two])
            i += 2
            continue
        ch = text[i]
        out.append(table.get(ch, ch))
        i += 1
    return "".join(out)


def _collapse(text: str) -> str:
    out: list[str] = []
    for ch in text:
        if not out or out[-1] != ch:
            out.append(ch)
    return "".join(out)


def phonetic_key(text: str) -> str:
    """Return a lowercase Latin sound key so Greek, Greeklish and transliterations collide.

    Steps: :func:`~greektext.fold`; Greek words are transliterated with ELOT 743 (ξ -> ks,
    χ -> x); Latin text gets the Greeklish aliases (w -> o, h -> i, ph -> f, 8 -> th,
    3 -> ks, c -> k, u/y after a/e -> v, y before i/e -> g); non-letters are dropped; then
    spellings that sound alike are unified (i/y/ei/oi/yi -> i, w/o -> o, ai -> e,
    af/au -> av, ef/eu -> ev, ng/gk/gg -> g, mp -> b, nt -> d, ch -> x, ou -> u) and doubled
    letters collapsed, until nothing changes. The key writes the χ sound as "x" (Greeklish
    uses x for χ). ``phonetic_key`` is idempotent.

    The key is for matching only: it is lossy, and its exact spelling may change between minor
    versions, so do not store it as a permanent identifier.

    >>> phonetic_key("Κωνσταντίνος") == phonetic_key("Konstantinos") == phonetic_key("Kwnstantinos")
    True
    >>> phonetic_key("Αθήνα"), phonetic_key("A8hna")
    ('athina', 'athina')
    >>> phonetic_key("Ευάγγελος")
    'evagelos'
    >>> phonetic_key("Παναγιώτης") == phonetic_key("Panayiotis") == phonetic_key("Panagiwtis")
    True
    """
    folded = fold(text)
    parts: list[str] = []
    start = 0
    n = len(folded)
    while start < n:
        greek = folded[start] in GREEK_LETTERS
        end = start + 1
        while end < n and (folded[end] in GREEK_LETTERS) == greek:
            end += 1
        chunk = folded[start:end]
        parts.append(
            transliterate(chunk, PHONETIC_SCHEME)
            if greek
            else _rewrite(chunk, _LATIN_ALIASES, _LATIN_UNITS)
        )
        start = end
    key = "".join(ch for ch in "".join(parts) if ch.isalpha())
    while True:
        new = _collapse(_rewrite(key, _SOUNDS))
        if new == key:
            return key
        key = new
