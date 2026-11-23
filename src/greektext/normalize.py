"""General cleanup for storage."""

from __future__ import annotations

__all__ = ["normalize"]


def normalize(
    text: str,
    *,
    form: str = "NFC",
    whitespace: bool = True,
    final_sigma: bool = True,
    lookalikes: bool = False,
) -> str:
    """Clean up Greek text for storage."""
    raise NotImplementedError
