"""Greek-aware slugify."""

from __future__ import annotations

__all__ = ["slugify"]


def slugify(
    text: str,
    *,
    sep: str = "-",
    scheme: str = "elot743",
    max_length: int | None = None,
    lowercase: bool = True,
) -> str:
    """Turn text into a URL / filename slug."""
    raise NotImplementedError
