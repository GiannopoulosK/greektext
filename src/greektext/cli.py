"""The ``greektext`` command line interface."""

from __future__ import annotations

from collections.abc import Sequence

__all__ = ["main"]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the exit code."""
    raise NotImplementedError
