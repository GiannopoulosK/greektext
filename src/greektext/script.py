"""Script detection, homoglyph repair and Greek sorting."""

from __future__ import annotations

import re

from ._chars import GREEK_LETTERS, GREEK_TO_LATIN, LATIN_LETTERS, LATIN_TO_GREEK
from .accents import fold

__all__ = ["fix_lookalikes", "greek_ratio", "is_greek", "sort_key"]

# A word: letters, possibly carrying combining marks (for decomposed input).
_WORD = re.compile(r"[^\W\d_](?:[^\W\d_]|[\u0300-\u036f])*")


def greek_ratio(text: str) -> float:
    """Return the share of alphabetic characters that are Greek (0.0 when there are none).

    >>> greek_ratio("Αθήνα")
    1.0
    >>> greek_ratio("Hello κόσμε")
    0.5
    >>> greek_ratio("1234 !")
    0.0
    """
    letters = greek = 0
    for ch in text:
        if ch.isalpha():
            letters += 1
            if ch in GREEK_LETTERS:
                greek += 1
    return greek / letters if letters else 0.0


def is_greek(text: str, *, threshold: float = 0.5) -> bool:
    """Return True when ``greek_ratio(text) >= threshold``.

    >>> is_greek("Καλημέρα κόσμε")
    True
    >>> is_greek("Hello world κόσμε")
    False
    >>> is_greek("Hello κόσμε", threshold=0.6)
    False
    """
    return greek_ratio(text) >= threshold


def _fix_word(match: re.Match[str]) -> str:
    word = match.group()
    greek = latin = 0
    for ch in word:
        if ch in GREEK_LETTERS:
            greek += 1
        elif ch in LATIN_LETTERS:
            latin += 1
    if not (greek and latin):
        return word
    if greek > latin:
        return word.translate(LATIN_TO_GREEK)
    if latin > greek:
        return word.translate(GREEK_TO_LATIN)
    return word


def fix_lookalikes(text: str) -> str:
    """Repair Latin/Greek homoglyphs that mixed keyboards leave inside words.

    Each word votes: if most of its letters are Greek, Latin letters that look identical to a
    Greek one (A B E Z H I K M N O P T X Y o) become Greek; if most are Latin, the Greek
    twins become Latin. Words with no majority, and words in a single script, are left alone.

    >>> fix_lookalikes("Kαλημέρα") == "Καλημέρα"  # Latin K -> Greek Κ
    True
    >>> fix_lookalikes("NΕΑ ΤΑΞΙ") == "ΝΕΑ ΤΑΞΙ"  # Latin N in a Greek word
    True
    >>> fix_lookalikes("H\u039fTEL") == "HOTEL"  # Greek Ο in a Latin word
    True
    >>> fix_lookalikes("TAXI ΤΑΞΙ")  # single-script words are never touched
    'TAXI ΤΑΞΙ'
    """
    return _WORD.sub(_fix_word, text)


def sort_key(text: str) -> tuple[str, str]:
    """Return a key for ``sorted()`` that orders by the Greek alphabet, ignoring accents and case.

    The first element is :func:`fold` of the text; the original text breaks ties so the
    order is stable and deterministic.

    >>> sorted(["Ωραιόκαστρο", "άλφα", "Ζάκυνθος", "αλφα", "Έδεσσα"], key=sort_key)
    ['άλφα', 'αλφα', 'Έδεσσα', 'Ζάκυνθος', 'Ωραιόκαστρο']
    """
    return fold(text), text
