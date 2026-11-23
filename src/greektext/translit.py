"""Greek to Latin transliteration.

The ``elot743`` scheme follows ELOT 743 (2nd edition, type 2 transcription, the same system as
the UN 1987 and ISO 843 transcriptions). Sources and the per-row check are listed in
``docs/transliteration.md``.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import NamedTuple

from ._chars import DIACRITICS, DIALYTIKA, GREEK_LETTERS

__all__ = ["SCHEMES", "Scheme", "to_latin"]

# --------------------------------------------------------------------------- scheme tables


@dataclass(frozen=True)
class Scheme:
    """A Greek -> Latin transliteration table. Keys are lowercase, unaccented Greek."""

    #: Single letters.
    letters: Mapping[str, str]
    #: Vowel digraphs: αι ει οι ου υι.
    vowel_digraphs: Mapping[str, str]
    #: αυ ευ ηυ -> (form before a vowel or voiced consonant, form before a voiceless consonant
    #: or at the end of the word).
    u_digraphs: Mapping[str, tuple[str, str]]
    #: Consonant digraphs: γγ γκ γξ γχ.
    consonant_digraphs: Mapping[str, str]
    #: Overrides for consonant digraphs at the start of a word.
    initial_digraphs: Mapping[str, str] = field(default_factory=dict)
    #: μπ -> (at the start or end of a word, inside a word).
    mp: tuple[str, str] = ("b", "mp")


_ELOT743 = Scheme(
    letters=MappingProxyType(
        {
            "α": "a",
            "β": "v",
            "γ": "g",
            "δ": "d",
            "ε": "e",
            "ζ": "z",
            "η": "i",
            "θ": "th",
            "ι": "i",
            "κ": "k",
            "λ": "l",
            "μ": "m",
            "ν": "n",
            "ξ": "x",
            "ο": "o",
            "π": "p",
            "ρ": "r",
            "σ": "s",
            "ς": "s",
            "τ": "t",
            "υ": "y",
            "φ": "f",
            "χ": "ch",
            "ψ": "ps",
            "ω": "o",
        }
    ),
    vowel_digraphs=MappingProxyType({"αι": "ai", "ει": "ei", "οι": "oi", "ου": "ou", "υι": "yi"}),
    u_digraphs=MappingProxyType({"αυ": ("av", "af"), "ευ": ("ev", "ef"), "ηυ": ("iv", "if")}),
    consonant_digraphs=MappingProxyType({"γγ": "ng", "γκ": "gk", "γξ": "nx", "γχ": "nch"}),
)

_SIMPLE = replace(
    _ELOT743,
    letters=MappingProxyType({**_ELOT743.letters, "η": "i", "ι": "i", "υ": "i", "ξ": "ks"}),
    vowel_digraphs=MappingProxyType({**_ELOT743.vowel_digraphs, "ει": "i", "οι": "i", "υι": "i"}),
    u_digraphs=MappingProxyType({**_ELOT743.u_digraphs, "αυ": ("av", "av"), "ευ": ("ev", "ev")}),
    initial_digraphs=MappingProxyType({"γκ": "g"}),
)

#: Used by :func:`greektext.phonetic_key`: ELOT 743 with ξ -> ks and χ -> x (the key's symbol
#: for the χ sound, which Greeklish also writes as "x"), and a nasal γ written as g.
PHONETIC_SCHEME = replace(
    _ELOT743,
    letters=MappingProxyType({**_ELOT743.letters, "ξ": "ks", "χ": "x"}),
    consonant_digraphs=MappingProxyType({**_ELOT743.consonant_digraphs, "γξ": "gks", "γχ": "gx"}),
)

#: The public transliteration schemes by name.
SCHEMES: Mapping[str, Scheme] = MappingProxyType({"elot743": _ELOT743, "simple": _SIMPLE})

#: After αυ / ευ / ηυ, these letters give the v form; anything else (voiceless consonant, end of
#: word) gives the f form.
_VOICED_AFTER_U = frozenset("αεηιοωυβγδζλμνρ")

#: Accents that mark the first vowel of a pair as stressed, which splits the digraph.
_ACCENTS = frozenset("\u0301\u0300\u0342")  # tonos/oxia, varia, perispomeni


def _base_letters() -> Mapping[str, str]:
    """Each Greek letter -> its lowercase unaccented base (ϐ -> β, Ά -> α, ἅ -> α ...)."""
    table: dict[str, str] = {}
    for ch in GREEK_LETTERS:
        base = unicodedata.normalize("NFKD", ch)[0].lower()
        table[ch] = base
    return MappingProxyType(table)


_BASE = _base_letters()

# --------------------------------------------------------------------------- Greek -> Latin


class _Letter(NamedTuple):
    base: str  # lowercase, unaccented
    original: str  # NFC of the letter with its marks
    upper: bool
    accent: bool
    dialytika: bool


def _tokenize(text: str) -> list[_Letter | str]:
    """Split text into Greek letters (with their marks) and runs of anything else."""
    items: list[_Letter | str] = []
    raw: list[str] = []
    decomposed = unicodedata.normalize("NFD", text)
    i, n = 0, len(decomposed)
    while i < n:
        ch = decomposed[i]
        j = i + 1
        while j < n and decomposed[j] in DIACRITICS:
            j += 1
        if ch in GREEK_LETTERS:
            if raw:
                items.append(unicodedata.normalize("NFC", "".join(raw)))
                raw = []
            marks = decomposed[i + 1 : j]
            items.append(
                _Letter(
                    base=_BASE[ch],
                    original=unicodedata.normalize("NFC", ch + marks),
                    upper=ch.isupper(),
                    accent=not _ACCENTS.isdisjoint(marks),
                    dialytika=DIALYTIKA in marks,
                )
            )
        else:
            raw.append(decomposed[i:j])
        i = j
    if raw:
        items.append(unicodedata.normalize("NFC", "".join(raw)))
    return items


def _word_to_latin(word: list[_Letter], scheme: Scheme) -> str:
    pieces: list[tuple[str, bool]] = []  # (latin, source letter was a capital)
    n = len(word)
    i = 0
    while i < n:
        letter = word[i]
        b0 = letter.base
        nxt = word[i + 1] if i + 1 < n else None
        if nxt is not None:
            pair = b0 + nxt.base
            # A tonos on the first vowel or a dialytika on the second splits a vowel digraph.
            split = letter.accent or nxt.dialytika
            out: str | None = None
            if pair in scheme.u_digraphs and not split:
                after = word[i + 2].base if i + 2 < n else ""
                voiced, voiceless = scheme.u_digraphs[pair]
                out = voiced if after in _VOICED_AFTER_U else voiceless
            elif pair in scheme.vowel_digraphs and not split:
                out = scheme.vowel_digraphs[pair]
            elif pair == "μπ":
                at_edge = i == 0 or i + 2 == n
                out = scheme.mp[0] if at_edge else scheme.mp[1]
            elif pair in scheme.consonant_digraphs:
                if i == 0 and pair in scheme.initial_digraphs:
                    out = scheme.initial_digraphs[pair]
                else:
                    out = scheme.consonant_digraphs[pair]
            if out is not None:
                pieces.append((out, letter.upper))
                i += 2
                continue
        single = scheme.letters.get(b0)
        if single is None:  # archaic letters (ϝ, ϙ, ϡ ...) pass through without marks
            pieces.append((unicodedata.normalize("NFC", b0), letter.upper))
        else:
            pieces.append((single, letter.upper))
        i += 1

    if n >= 2 and all(letter.upper for letter in word):
        return "".join(latin for latin, _ in pieces).upper()
    return "".join(latin[:1].upper() + latin[1:] if cap else latin for latin, cap in pieces)


def transliterate(text: str, scheme: Scheme) -> str:
    """Transliterate the Greek words in ``text`` with ``scheme``; everything else passes through."""
    out: list[str] = []
    word: list[_Letter] = []
    for item in _tokenize(text):
        if isinstance(item, _Letter):
            word.append(item)
            continue
        if word:
            out.append(_word_to_latin(word, scheme))
            word = []
        out.append(item)
    if word:
        out.append(_word_to_latin(word, scheme))
    return "".join(out)


def to_latin(text: str, *, scheme: str = "elot743") -> str:
    """Transliterate Greek to Latin.

    Schemes:

    - ``"elot743"`` (default): the Greek standard ELOT 743 (= UN / ISO 843 transcription).
      Digraphs are applied longest match first; a tonos on the first vowel or a dialytika on
      the second keeps two vowels apart ("άυλος" -> "aylos", "αϋπνία" -> "aypnia").
    - ``"simple"``: for slugs and casual display. Like ``elot743`` but η, ι, υ, ει, οι, υι
      all become "i", ξ becomes "ks", αυ / ευ are always "av" / "ev", and γκ at the start of a
      word is "g".

    Case follows the source word: an all-caps word (two or more letters) gives all caps,
    otherwise a capital letter capitalizes only the first Latin letter of its output.
    Non-Greek text passes through unchanged.

    >>> to_latin("Θεσσαλονίκη")
    'Thessaloniki'
    >>> to_latin("ΘΕΣΣΑΛΟΝΙΚΗ")
    'THESSALONIKI'
    >>> to_latin("Ευάγγελος Μπάμπης, αυτός")
    'Evangelos Bampis, aftos'
    >>> to_latin("Ψυχικό", scheme="simple")
    'Psichiko'
    """
    try:
        table = SCHEMES[scheme]
    except KeyError:
        raise ValueError(f"Unknown scheme {scheme!r}; expected one of {sorted(SCHEMES)}") from None
    return transliterate(text, table)
