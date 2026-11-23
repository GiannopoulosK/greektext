"""Execute the Python examples in the README and docs, so documentation cannot drift."""

from __future__ import annotations

import doctest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]


@pytest.mark.parametrize("path", DOCUMENTS, ids=lambda p: p.name)
def test_examples(path: Path) -> None:
    result = doctest.testfile(
        str(path),
        module_relative=False,
        optionflags=doctest.NORMALIZE_WHITESPACE,
        encoding="utf-8",
    )
    assert result.failed == 0


def test_readme_has_examples() -> None:
    parser = doctest.DocTestParser()
    examples = parser.get_examples((ROOT / "README.md").read_text(encoding="utf-8"))
    assert len(examples) > 20
