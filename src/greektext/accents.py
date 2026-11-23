"""Accent stripping and search folding."""

from __future__ import annotations

import unicodedata

from ._chars import (
    APOSTROPHES,
    DELETE_DIACRITICS,
    DIACRITICS,
    DIALYTIKA,
    GREEK_LETTERS,
    STRIP_ALL,
    STRIP_KEEP_DIALYTIKA,
)

__all__ = ["fold", "strip_accents"]


def strip_accents(text: str, *, keep_dialytika: bool = True) -> str:
    """Remove the tonos and polytonic marks from Greek letters.

    The dialytika is kept by default because it changes pronunciation ("προϊόν" is not
    "προιόν"); pass ``keep_dialytika=False`` to remove it too. Marks on non-Greek letters are
    left alone (use :func:`fold` for a key that ignores every diacritic). Input may be
    precomposed or decomposed; the result is NFC.

    >>> strip_accents("Αθήνα")
    'Αθηνα'
    >>> strip_accents("προϊόν")
    'προϊον'
    >>> strip_accents("προϊόν", keep_dialytika=False)
    'προιον'
    >>> strip_accents("ἀλήθεια ᾄδω")
    'αληθεια αδω'
    >>> strip_accents("café Αθήνα")
    'café Αθηνα'
    """
    table = STRIP_KEEP_DIALYTIKA if keep_dialytika else STRIP_ALL
    text = unicodedata.normalize("NFC", text).translate(table)
    if not DIACRITICS.isdisjoint(text):
        # Marks NFC could not compose onto a Greek letter (rare stacks such as "ά" + U+0304).
        text = _strip_loose_marks(text, keep_dialytika)
    return text


def _strip_loose_marks(text: str, keep_dialytika: bool) -> str:
    out: list[str] = []
    greek_base = False
    for ch in unicodedata.normalize("NFD", text):
        if ch in DIACRITICS:
            if greek_base and not (keep_dialytika and ch == DIALYTIKA):
                continue
        else:
            greek_base = ch in GREEK_LETTERS
        out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


def fold(text: str) -> str:
    """Return a search / comparison key that ignores accents, case and final sigma.

    Steps: NFD, remove every diacritic (tonos, dialytika, polytonic marks, and accents on
    Latin letters too), ``casefold()`` (which also maps ς to σ), map typographic
    apostrophes to "'", collapse whitespace. Greek punctuation (U+037E, U+0387) becomes ";"
    and "·" through the Unicode normalization. ``fold`` is idempotent.

    >>> fold("ΑΘΉΝΑ") == fold("Αθηνά") == fold("αθηνα") == "αθηνα"
    True
    >>> fold("οδός")
    'οδοσ'
    >>> fold("  Προϊόν   ΠΡΟΪΟΝ ")
    'προιον προιον'
    """
    text = unicodedata.normalize("NFD", text).translate(DELETE_DIACRITICS).casefold()
    # casefold can produce new marks ("ΐ" stays decomposed, "İ" -> "i" + U+0307).
    text = unicodedata.normalize("NFD", text).translate(DELETE_DIACRITICS)
    text = unicodedata.normalize("NFC", text).translate(APOSTROPHES)
    return " ".join(text.split())
