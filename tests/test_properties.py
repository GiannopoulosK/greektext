"""Property-based tests (hypothesis)."""

from __future__ import annotations

from collections.abc import Callable

from hypothesis import given
from hypothesis import strategies as st

from greektext import (
    fix_final_sigma,
    fix_lookalikes,
    fold,
    greek_ratio,
    is_greek,
    lower,
    normalize,
    sort_key,
    strip_accents,
    upper,
)

# Arbitrary Unicode without surrogates (which cannot be encoded and never reach str APIs
# from real input).
any_text = st.text(st.characters(codec="utf-8"))

# Greek-only text: monotonic and polytonic letters, combining marks, spaces and punctuation.
_GREEK_CHARS = (
    "αβγδεζηθικλμνξοπρσςτυφχψω"
    "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    "άέήίόύώΆΈΉΊΌΎΏϊϋΪΫΐΰ"
    "ἀἁἄἅὰᾶᾳᾠῆῶ"
    "\u0301\u0308"  # tonos, dialytika (combining)
    " ;\u00b7,.'\u2019\u037e\u0387"  # punctuation, apostrophes, Greek ; and ano teleia
)
greek_text = st.text(st.sampled_from(_GREEK_CHARS))
ascii_text = st.text(st.characters(min_codepoint=0x20, max_codepoint=0x7E))

IDEMPOTENT: list[Callable[[str], str]] = [
    fold,
    strip_accents,
    lambda s: strip_accents(s, keep_dialytika=False),
    normalize,
    lambda s: normalize(s, lookalikes=True),
    fix_final_sigma,
    fix_lookalikes,
    lower,
]


@given(any_text)
def test_idempotent_on_any_text(text: str) -> None:
    for f in IDEMPOTENT:
        once = f(text)
        assert f(once) == once, f


@given(greek_text)
def test_idempotent_on_greek_text(text: str) -> None:
    for f in [*IDEMPOTENT, upper]:
        once = f(text)
        assert f(once) == once, f


@given(greek_text)
def test_fold_ignores_case(text: str) -> None:
    assert fold(text) == fold(upper(text)) == fold(lower(text))


@given(any_text)
def test_nothing_raises(text: str) -> None:
    upper(text)
    lower(text)
    sort_key(text)
    is_greek(text)
    ratio = greek_ratio(text)
    assert 0.0 <= ratio <= 1.0
    for form in ("NFC", "NFD", "NFKC", "NFKD"):
        normalize(text, form=form, lookalikes=True)


@given(ascii_text)
def test_ascii_passes_through(text: str) -> None:
    assert strip_accents(text) == text
    assert fix_final_sigma(text) == text
    assert normalize(text) == " ".join(text.split())
