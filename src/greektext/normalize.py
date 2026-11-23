"""General cleanup for storage."""

from __future__ import annotations

import unicodedata
from typing import Literal, cast

from .case import fix_final_sigma
from .script import fix_lookalikes

__all__ = ["normalize"]

UnicodeForm = Literal["NFC", "NFD", "NFKC", "NFKD"]

_FORMS: tuple[str, ...] = ("NFC", "NFD", "NFKC", "NFKD")


def normalize(
    text: str,
    *,
    form: str = "NFC",
    whitespace: bool = True,
    final_sigma: bool = True,
    lookalikes: bool = False,
) -> str:
    """Clean up text for storage, keeping accents and case.

    Every Unicode form also maps the Greek question mark (U+037E) and ano teleia (U+0387) to
    ";" and "·", so Greek punctuation always comes out in its standard form.

    Args:
        text: Any text.
        form: Unicode normalization form: ``"NFC"`` (default), ``"NFD"``, ``"NFKC"`` or
            ``"NFKD"``.
        whitespace: Collapse runs of whitespace (including newlines) to one space and strip
            the ends.
        final_sigma: Apply :func:`~greektext.fix_final_sigma`.
        lookalikes: Apply :func:`~greektext.fix_lookalikes`.

    >>> normalize("Τι κάνεις\\u037e")
    'Τι κάνεις;'
    >>> normalize("  οδοσ \\n  Πατρών ")
    'οδος Πατρών'
    >>> normalize("Kαλημέρα", lookalikes=True) == "Καλημέρα"  # Latin K -> Greek Κ
    True
    """
    if form not in _FORMS:
        raise ValueError(f"form must be one of {_FORMS}, got {form!r}")
    text = unicodedata.normalize(cast(UnicodeForm, form), text)
    if whitespace:
        text = " ".join(text.split())
    if lookalikes:
        text = fix_lookalikes(text)
    if final_sigma:
        text = fix_final_sigma(text)
    return text
