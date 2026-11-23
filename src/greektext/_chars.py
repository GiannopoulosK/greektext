"""Character data shared by the greektext modules.

Everything in here is data, built once at import time. Logic lives in the other modules and
only looks things up here.
"""

from __future__ import annotations

import unicodedata

# --------------------------------------------------------------------------- combining marks

TONOS = "\u0301"  # COMBINING ACUTE ACCENT, what NFD turns the tonos / oxia into
DIALYTIKA = "\u0308"  # COMBINING DIAERESIS
YPOGEGRAMMENI = "\u0345"  # COMBINING GREEK YPOGEGRAMMENI (iota subscript)

#: The spacing GREEK YPOGEGRAMMENI (U+037A) is an older way to write the iota subscript after
#: a letter ("αͺ" for "ᾳ"). Reading it as the combining mark lets it be handled like one.
SPACING_YPOGEGRAMMENI: dict[int, str] = {0x037A: YPOGEGRAMMENI}

#: Ranges of combining *diacritical* marks. ``fold`` deletes all of them; other combining
#: characters (Indic vowel signs and the like) are part of their letters and are kept.
DIACRITIC_RANGES: tuple[tuple[int, int], ...] = (
    (0x0300, 0x036F),  # Combining Diacritical Marks (includes all Greek polytonic marks)
    (0x1AB0, 0x1AFF),  # Combining Diacritical Marks Extended
    (0x1DC0, 0x1DFF),  # Combining Diacritical Marks Supplement
    (0x20D0, 0x20FF),  # Combining Diacritical Marks for Symbols
    (0xFE20, 0xFE2F),  # Combining Half Marks
)

DIACRITICS: frozenset[str] = frozenset(
    chr(cp) for lo, hi in DIACRITIC_RANGES for cp in range(lo, hi + 1)
)

#: ``str.translate`` table deleting every diacritical mark.
DELETE_DIACRITICS: dict[int, None] = dict.fromkeys(map(ord, DIACRITICS))

#: Invisible format characters that can sit inside a word without ending it: SOFT HYPHEN, ZERO
#: WIDTH NON-JOINER, ZERO WIDTH JOINER, WORD JOINER and ZERO WIDTH NO-BREAK SPACE (the BOM).
#: They come with text copied from web pages, PDFs and word processors. (ZERO WIDTH SPACE is a
#: word break by definition and is not included.)
INVISIBLE = "\u00ad\u200c\u200d\u2060\ufeff"
DELETE_INVISIBLE: dict[int, None] = dict.fromkeys(map(ord, INVISIBLE))

# --------------------------------------------------------------------------- Greek letters

#: Unicode blocks holding Greek letters. Coptic letters (U+03E2-U+03EF) share the first block but
#: are not Greek and are excluded below.
GREEK_BLOCKS: tuple[tuple[int, int], ...] = ((0x0370, 0x03FF), (0x1F00, 0x1FFF))
_COPTIC = range(0x03E2, 0x03F0)


def _greek_letters() -> frozenset[str]:
    letters = set()
    for lo, hi in GREEK_BLOCKS:
        for cp in range(lo, hi + 1):
            ch = chr(cp)
            if cp not in _COPTIC and ch.isalpha():
                letters.add(ch)
    return frozenset(letters)


#: Every alphabetic character in the Greek and Greek Extended blocks (Coptic excluded).
GREEK_LETTERS: frozenset[str] = _greek_letters()


def _latin_letters() -> frozenset[str]:
    letters = set()
    for cp in range(0x0250):  # Basic Latin to Latin Extended-B
        ch = chr(cp)
        if ch.isalpha() and unicodedata.name(ch, "").startswith("LATIN"):
            letters.add(ch)
    for cp in range(0x1E00, 0x1F00):  # Latin Extended Additional
        ch = chr(cp)
        if ch.isalpha():
            letters.add(ch)
    return frozenset(letters)


#: Latin letters, used to take a per-word script majority vote.
LATIN_LETTERS: frozenset[str] = _latin_letters()


def _regex_class(chars: frozenset[str]) -> str:
    """A regex character class body (without brackets) for ``chars``, as compact ranges."""
    cps = sorted(map(ord, chars))
    parts: list[str] = []
    start = prev = cps[0]
    for cp in [*cps[1:], -1]:
        if cp == prev + 1:
            prev = cp
            continue
        parts.append(f"\\u{start:04x}" if start == prev else f"\\u{start:04x}-\\u{prev:04x}")
        start = prev = cp
    return "".join(parts)


#: Regex class body matching any Greek letter.
GREEK_LETTER_CLASS: str = _regex_class(GREEK_LETTERS)

# --------------------------------------------------------------------------- accent stripping


def _strip_table(keep_dialytika: bool) -> dict[int, str]:
    """Map each precomposed Greek letter with marks to its NFC form without them."""
    table: dict[int, str] = {}
    for ch in GREEK_LETTERS:
        decomposed = unicodedata.normalize("NFD", ch)
        if len(decomposed) == 1:
            continue
        kept = "".join(c for c in decomposed[1:] if keep_dialytika and c == DIALYTIKA)
        stripped = unicodedata.normalize("NFC", decomposed[0] + kept)
        if stripped != ch:
            table[ord(ch)] = stripped
    return table


#: ``str.translate`` tables for NFC text: Greek letter with marks -> letter without them.
STRIP_KEEP_DIALYTIKA: dict[int, str] = _strip_table(keep_dialytika=True)
STRIP_ALL: dict[int, str] = _strip_table(keep_dialytika=False)

# --------------------------------------------------------------------------- casing

#: Marks that Greek all-caps drops. Everything combining except the dialytika: tonos/oxia,
#: varia, perispomeni, breathings, iota subscript, macron, breve...
UPPER_DROPS: frozenset[str] = DIACRITICS - {DIALYTIKA}

#: First vowel -> the second vowels that make a digraph with it (αι ει οι υι αυ ευ ηυ ου).
DIGRAPHS: dict[str, frozenset[str]] = {
    "α": frozenset("ιυ"),
    "ε": frozenset("ιυ"),
    "ο": frozenset("ιυ"),
    "υ": frozenset("ι"),
    "η": frozenset("υ"),
}

# --------------------------------------------------------------------------- sigma / elision

SIGMA = "σ"
FINAL_SIGMA = "ς"

#: An apostrophe after σ marks elision ("σ' αγαπώ"): the σ must stay σ.
#: APOSTROPHE, RIGHT SINGLE QUOTATION MARK, MODIFIER LETTER APOSTROPHE.
ELISION_MARKS = "'\u2019\u02bc"

#: Elision marks / apostrophes unified to U+0027 in search keys.
APOSTROPHES: dict[int, str] = {ord(c): "'" for c in ELISION_MARKS[1:]}

# --------------------------------------------------------------------------- lookalikes

#: Latin letters that are visually identical to Greek ones (in common fonts) and their
#: Greek twin. Kept deliberately conservative: pairs that merely look similar (v/ν, u/υ,
#: a/α, k/κ) are not homoglyphs and are left alone.
LATIN_TO_GREEK_HOMOGLYPHS: dict[str, str] = {
    "A": "Α",
    "B": "Β",
    "E": "Ε",
    "Z": "Ζ",
    "H": "Η",
    "I": "Ι",
    "K": "Κ",
    "M": "Μ",
    "N": "Ν",
    "O": "Ο",
    "P": "Ρ",
    "T": "Τ",
    "X": "Χ",
    "Y": "Υ",
    "o": "ο",
}

#: Letters that have a twin in the other script.
LATIN_HOMOGLYPHS: frozenset[str] = frozenset(LATIN_TO_GREEK_HOMOGLYPHS)
GREEK_HOMOGLYPHS: frozenset[str] = frozenset(LATIN_TO_GREEK_HOMOGLYPHS.values())

LATIN_TO_GREEK: dict[int, str] = str.maketrans(LATIN_TO_GREEK_HOMOGLYPHS)
GREEK_TO_LATIN: dict[int, str] = str.maketrans(
    {greek: latin for latin, greek in LATIN_TO_GREEK_HOMOGLYPHS.items()}
)
