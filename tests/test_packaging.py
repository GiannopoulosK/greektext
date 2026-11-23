"""Packaging invariants."""

from __future__ import annotations

import greektext


def test_public_api() -> None:
    for name in greektext.__all__:
        assert hasattr(greektext, name), name
        if name != "__version__":
            assert getattr(greektext, name).__doc__, f"{name} has no docstring"
            assert ">>>" in getattr(greektext, name).__doc__, f"{name} has no doctest"


def test_only_top_level_is_public() -> None:
    # Implementation modules are private, so the public API is exactly greektext.__all__.
    import pkgutil

    modules = [m.name for m in pkgutil.iter_modules(greektext.__path__)]
    assert modules
    assert all(name.startswith("_") for name in modules), modules
    public = {n for n in dir(greektext) if not n.startswith("_")}
    assert public == set(greektext.__all__) - {"__version__"}
