"""A script-independent sound key for matching Greek, Greeklish and transliterations."""

from __future__ import annotations

__all__ = ["phonetic_key"]


def phonetic_key(text: str) -> str:
    """Return a lowercase Latin sound key."""
    raise NotImplementedError
