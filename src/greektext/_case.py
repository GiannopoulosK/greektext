"""Greek-aware casing and final sigma."""

from __future__ import annotations

import re
import unicodedata

from ._chars import (
    DIACRITICS,
    DIALYTIKA,
    DIGRAPHS,
    ELISION_MARKS,
    FINAL_SIGMA,
    GREEK_LETTERS,
    INVISIBLE,
    SIGMA,
    TONOS,
    UPPER_DROPS,
    YPOGEGRAMMENI,
)

__all__ = ["fix_final_sigma", "lower", "upper"]

#: Accents that mark a stressed vowel: tonos/oxia, varia, perispomeni.
_ACCENTS = frozenset("\u0301\u0300\u0342")

_SIGMAS = re.compile(f"[{SIGMA}{FINAL_SIGMA}]")


def _greek_letter_before(text: str, i: int) -> bool:
    """Is the character before ``text[i]``, skipping marks and invisible characters, Greek?"""
    i -= 1
    while i >= 0 and (text[i] in DIACRITICS or text[i] in INVISIBLE):
        i -= 1
    return i >= 0 and text[i] in GREEK_LETTERS


def fix_final_sigma(text: str) -> str:
    """Use ς at the end of Greek words and σ everywhere else.

    - σ at the end of a Greek word becomes ς;
    - ς followed by a Greek letter becomes σ;
    - σ before an elision mark (``'``, ``’``, ``ʼ``) stays σ: "σ' αγαπώ";
    - a sigma with no letter before it (a lone "σ", an initial in "κ.σ.") is σ.

    >>> fix_final_sigma("οδοσ πατρων")
    'οδος πατρων'
    >>> fix_final_sigma("ςοφος")
    'σοφος'
    >>> fix_final_sigma("σ' αγαπώ")
    "σ' αγαπώ"
    >>> fix_final_sigma("ΚΑΙ σ")
    'ΚΑΙ σ'
    >>> fix_final_sigma("κ.ς.")
    'κ.σ.'
    """
    if SIGMA not in text and FINAL_SIGMA not in text:
        return text

    def fix(match: re.Match[str]) -> str:
        sigma, i, j = match.group(), match.start(), match.end()
        while j < len(text) and text[j] in INVISIBLE:  # a soft hyphen does not end the word
            j += 1
        after = text[j] if j < len(text) else ""
        if not _greek_letter_before(text, i):
            return SIGMA
        if sigma == SIGMA:
            in_word = after.isalnum() or after == "_" or after in DIACRITICS
            elided = after != "" and after in ELISION_MARKS
            return SIGMA if in_word or elided else FINAL_SIGMA
        return SIGMA if after in GREEK_LETTERS else FINAL_SIGMA

    return _SIGMAS.sub(fix, text)


def lower(text: str) -> str:
    """Lowercase, then fix final sigma, so all-caps input gets a correct ς.

    >>> lower("ΟΔΟΣ ΠΑΤΡΩΝ")
    'οδος πατρων'
    >>> lower("Κ.Σ. ΚΑΙ Α.Ε.Σ")  # str.lower() gives "κ.ς. και α.ε.ς"
    'κ.σ. και α.ε.σ'
    >>> lower("Σ' ΑΓΑΠΩ")
    "σ' αγαπω"
    """
    return fix_final_sigma(text.lower())


def upper(text: str) -> str:
    """Orthographic Greek uppercase.

    Greek capitals are written without accents, so the tonos (and any polytonic mark) is
    dropped while the dialytika is kept. When a tonos on the first vowel of a would-be digraph
    (αι ει οι υι αυ ευ ηυ ου) is what keeps the two vowels apart, the capital form shows it
    with a dialytika on the second vowel instead. The one word that keeps its accent is the
    disjunctive "ή" ("or"), written "Ή" so it is not read as the article "Η". Non-Greek
    characters use ``str.upper()``. Returns NFC.

    >>> upper("καλημέρα")
    'ΚΑΛΗΜΕΡΑ'
    >>> upper("Μάιος")
    'ΜΑΪΟΣ'
    >>> upper("ρολόι")
    'ΡΟΛΟΪ'
    >>> upper("προϊόν")
    'ΠΡΟΪΟΝ'
    >>> upper("Hello κόσμε")
    'HELLO ΚΟΣΜΕ'
    >>> upper("Τον Μάιο ή τον Ιούνιο, η θάλασσα")
    'ΤΟΝ ΜΑΪΟ Ή ΤΟΝ ΙΟΥΝΙΟ, Η ΘΑΛΑΣΣΑ'
    """
    out: list[str] = []
    # The previous Greek base letter (lowercase) and whether it carried a tonos.
    prev_base = ""
    prev_tonos = False
    prev_letter = False  # whether the previous character was a letter (of any script)
    decomposed = unicodedata.normalize("NFD", text)
    i, n = 0, len(decomposed)
    while i < n:
        base = decomposed[i]
        j = i + 1
        while j < n and decomposed[j] in DIACRITICS:
            j += 1
        marks = decomposed[i + 1 : j]
        i = j
        if base in INVISIBLE:  # a soft hyphen or joiner inside a word: keep it, keep the state
            out.append(base + marks)
            continue
        if base not in GREEK_LETTERS:
            # str.upper() turns a stray iota subscript into a capital iota (U+0345 -> U+0399);
            # it only belongs to Greek letters, so drop it like every other Greek capital does.
            cluster = (base + marks).replace(YPOGEGRAMMENI, "")
            out.append(unicodedata.normalize("NFC", cluster).upper())
            prev_base, prev_tonos, prev_letter = "", False, base.isalpha()
            continue
        low = base.lower()
        has_tonos = TONOS in marks
        has_dialytika = DIALYTIKA in marks
        kept = "".join(m for m in marks if m not in UPPER_DROPS)
        if (
            prev_tonos
            and not has_dialytika
            and not has_tonos
            and low in DIGRAPHS.get(prev_base, ())
        ):
            kept += DIALYTIKA
        elif (
            low == "η"
            and not _ACCENTS.isdisjoint(marks)
            and not prev_letter
            and not (i < n and decomposed[i].isalpha())
        ):
            kept += TONOS  # the disjunctive ή on its own: Ή, not the article Η
        out.append(base.upper() + kept)
        prev_base, prev_tonos, prev_letter = low, has_tonos, True
    return unicodedata.normalize("NFC", "".join(out))
