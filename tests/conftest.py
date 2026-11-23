"""Shared test configuration."""

from __future__ import annotations

import os

from hypothesis import settings

# CI runners (especially Windows and macOS) are slow and noisy: never fail a property test on
# timing alone, and try more examples there than locally.
settings.register_profile("ci", deadline=None, max_examples=300)
settings.register_profile("dev", deadline=None)
settings.load_profile("ci" if os.environ.get("CI") else "dev")
