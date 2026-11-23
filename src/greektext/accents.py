"""Accent stripping and search folding."""

from __future__ import annotations

__all__ = ["fold", "strip_accents"]


def strip_accents(text: str, *, keep_dialytika: bool = True) -> str:
    """Remove tonos and polytonic marks from Greek letters."""
    raise NotImplementedError


def fold(text: str) -> str:
    """Return an accent-, case- and final-sigma-insensitive search key."""
    raise NotImplementedError
