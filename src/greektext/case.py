"""Greek-aware casing and final sigma."""

from __future__ import annotations

__all__ = ["fix_final_sigma", "lower", "upper"]


def upper(text: str) -> str:
    """Orthographic Greek uppercase."""
    raise NotImplementedError


def lower(text: str) -> str:
    """Lowercase with correct final sigma."""
    raise NotImplementedError


def fix_final_sigma(text: str) -> str:
    """Use ς at the end of Greek words and σ everywhere else."""
    raise NotImplementedError
