"""Script detection, homoglyph repair and Greek sorting."""

from __future__ import annotations

__all__ = ["fix_lookalikes", "greek_ratio", "is_greek", "sort_key"]


def greek_ratio(text: str) -> float:
    """Share of alphabetic characters that are Greek."""
    raise NotImplementedError


def is_greek(text: str, *, threshold: float = 0.5) -> bool:
    """True when ``greek_ratio(text) >= threshold``."""
    raise NotImplementedError


def fix_lookalikes(text: str) -> str:
    """Repair Latin/Greek homoglyphs inside words."""
    raise NotImplementedError


def sort_key(text: str) -> tuple[str, str]:
    """Key for ``sorted()`` in Greek alphabetical order."""
    raise NotImplementedError
