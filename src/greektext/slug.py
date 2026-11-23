"""Greek-aware slugify."""

from __future__ import annotations

import re
import unicodedata

from ._chars import DELETE_DIACRITICS, ELISION_MARKS
from .translit import to_latin

__all__ = ["slugify"]

_DROP_APOSTROPHES = dict.fromkeys(map(ord, ELISION_MARKS))
_NON_ALNUM = re.compile(r"[^a-zA-Z0-9]+")


def slugify(
    text: str,
    *,
    sep: str = "-",
    scheme: str = "elot743",
    max_length: int | None = None,
    lowercase: bool = True,
) -> str:
    """Turn text into a URL / filename slug.

    Greek is transliterated with ``scheme`` (see :func:`~greektext.to_latin`), accents on
    Latin letters are dropped, apostrophes are removed ("Τ'αστέρια" -> "tasteria"), and every
    other run of characters outside ``[a-z0-9]`` becomes one ``sep``. With ``max_length`` the
    slug is cut at the last separator that fits; a single word longer than ``max_length`` is
    cut at ``max_length``.

    >>> slugify("Καλημέρα Κόσμε!")
    'kalimera-kosme'
    >>> slugify("Ευάγγελος & Σία Ο.Ε.")
    'evangelos-sia-o-e'
    >>> slugify("Θεσσαλονίκη, Ελλάδα", sep="_", lowercase=False)
    'Thessaloniki_Ellada'
    >>> slugify("Ταχυδρομικός κώδικας 54624", max_length=24)
    'tachydromikos-kodikas'
    >>> slugify("Ταχυδρομικός κώδικας 54624", max_length=5)
    'tachy'
    """
    if max_length is not None and max_length < 0:
        raise ValueError(f"max_length must be >= 0, got {max_length}")
    latin = to_latin(text.translate(_DROP_APOSTROPHES), scheme=scheme)
    latin = unicodedata.normalize("NFKD", latin).translate(DELETE_DIACRITICS)
    if lowercase:
        latin = latin.lower()
    words = [w for w in _NON_ALNUM.split(latin) if w]
    slug = sep.join(words)
    if max_length is None or len(slug) <= max_length:
        return slug
    cut = ""
    for word in words:
        candidate = f"{cut}{sep}{word}" if cut else word
        if len(candidate) > max_length:
            break
        cut = candidate
    return cut or words[0][:max_length]
