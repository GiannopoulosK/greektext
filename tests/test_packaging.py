"""Packaging invariants."""

from __future__ import annotations

import greektext


def test_public_api() -> None:
    for name in greektext.__all__:
        assert hasattr(greektext, name), name
        if name != "__version__":
            assert getattr(greektext, name).__doc__, f"{name} has no docstring"
            assert ">>>" in getattr(greektext, name).__doc__, f"{name} has no doctest"
