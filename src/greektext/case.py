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
    GREEK_LETTER_CLASS,
    GREEK_LETTERS,
    SIGMA,
    TONOS,
    UPPER_DROPS,
    YPOGEGRAMMENI,
)

__all__ = ["fix_final_sigma", "lower", "upper"]

# σ that ends a Greek word: after a Greek letter (or a mark on one), and not followed by another
# word character, a mark, or an elision apostrophe.
_SIGMA_AT_END = re.compile(
    rf"(?<=[{GREEK_LETTER_CLASS}\u0300-\u036f]){SIGMA}(?![\w\u0300-\u036f{ELISION_MARKS}])"
)
# ς that does not end a word: followed by a Greek letter, or with no Greek letter before it
# (a lone "ς", or an abbreviation such as "Κ.Σ." lowercased by str.lower() to "κ.ς.").
_FINAL_SIGMA_MISPLACED = re.compile(
    rf"{FINAL_SIGMA}(?=[{GREEK_LETTER_CLASS}])|(?<![{GREEK_LETTER_CLASS}\u0300-\u036f]){FINAL_SIGMA}"
)


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
    text = _SIGMA_AT_END.sub(FINAL_SIGMA, text)
    return _FINAL_SIGMA_MISPLACED.sub(SIGMA, text)


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
    with a dialytika on the second vowel instead. Non-Greek characters use ``str.upper()``.
    Returns NFC.

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
    """
    out: list[str] = []
    # The previous Greek base letter (lowercase) and whether it carried a tonos.
    prev_base = ""
    prev_tonos = False
    decomposed = unicodedata.normalize("NFD", text)
    i, n = 0, len(decomposed)
    while i < n:
        base = decomposed[i]
        j = i + 1
        while j < n and decomposed[j] in DIACRITICS:
            j += 1
        marks = decomposed[i + 1 : j]
        i = j
        if base not in GREEK_LETTERS:
            # str.upper() turns a stray iota subscript into a capital iota (U+0345 -> U+0399);
            # it only belongs to Greek letters, so drop it like every other Greek capital does.
            cluster = (base + marks).replace(YPOGEGRAMMENI, "")
            out.append(unicodedata.normalize("NFC", cluster).upper())
            prev_base, prev_tonos = "", False
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
        out.append(base.upper() + kept)
        prev_base, prev_tonos = low, has_tonos
    return unicodedata.normalize("NFC", "".join(out))
