# Contributing to greektext

Thanks for helping! Bug reports with a concrete Greek example are the most useful thing you can send.

## Development setup

```bash
git clone https://github.com/GiannopoulosK/greektext
cd greektext
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Checks

```bash
ruff check . && ruff format --check .
mypy
pytest --cov
```

CI runs the same commands on Linux, macOS and Windows with Python 3.10 to 3.14, and requires
at least 95% coverage of `src/greektext`.

## Ground rules

- greektext has **no runtime dependencies** and no framework integrations: functions are plain
  `str -> str` callables, and framework usage belongs in `docs/recipes.md`.
- Character tables are data: they belong in `_chars.py` or the scheme tables in `translit.py`,
  never inline in logic.
- Every public function has full type hints, a docstring with at least one doctest, and an entry
  in `__all__`.
- When a Greek-language rule is unclear, write a test for the case and raise it in the pull
  request rather than inventing a rule.
- Update `CHANGELOG.md` under *Unreleased*.

## Releasing

1. Set `__version__` in `src/greektext/__init__.py`, move the *Unreleased* entries in
   `CHANGELOG.md` under the new version with today's date, and update the compare links.
2. Commit as "Release X.Y.Z", then tag and push: `git tag vX.Y.Z && git push origin main vX.Y.Z`.
3. The release workflow checks that the tag matches `__version__`, builds the sdist and wheel,
   runs the test suite from them, publishes to PyPI through trusted publishing (the `pypi`
   environment) and creates the GitHub release.
