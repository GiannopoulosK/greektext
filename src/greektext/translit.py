"""Greek to Latin transliteration."""

from __future__ import annotations

__all__ = ["to_latin"]


def to_latin(text: str, *, scheme: str = "elot743") -> str:
    """Transliterate Greek to Latin."""
    raise NotImplementedError
