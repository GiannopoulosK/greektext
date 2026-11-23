"""Property-based tests (hypothesis)."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from typing import Literal

from hypothesis import example, given
from hypothesis import strategies as st

from greektext import (
    fix_final_sigma,
    fix_lookalikes,
    fold,
    greek_ratio,
    is_greek,
    lower,
    normalize,
    phonetic_key,
    slugify,
    sort_key,
    strip_accents,
    to_latin,
    upper,
)
from greektext._chars import GREEK_LETTERS

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


@given(any_text, st.sampled_from(["NFC", "NFD", "NFKC", "NFKD"]), st.booleans())
@example("\u03a1\u0301u", "NFC", True)  # Greek Ρ + acute becomes Latin P + acute = Ṕ
def test_normalize_returns_the_requested_form(
    text: str, form: Literal["NFC", "NFD", "NFKC", "NFKD"], lookalikes: bool
) -> None:
    out = normalize(text, form=form, lookalikes=lookalikes)
    assert unicodedata.is_normalized(form, out)


@given(ascii_text)
def test_ascii_passes_through(text: str) -> None:
    assert strip_accents(text) == text
    assert fix_final_sigma(text) == text
    assert normalize(text) == " ".join(text.split())


# --------------------------------------------------------------------------- transliteration

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@given(any_text)
def test_phonetic_key_idempotent(text: str) -> None:
    key = phonetic_key(text)
    assert phonetic_key(key) == key


@given(greek_text)
def test_phonetic_key_idempotent_on_greek(text: str) -> None:
    key = phonetic_key(text)
    assert phonetic_key(key) == key


@given(any_text)
def test_slug_shape(text: str) -> None:
    slug = slugify(text)
    assert slug == "" or SLUG_RE.match(slug), slug


@given(greek_text)
def test_slug_shape_greek(text: str) -> None:
    slug = slugify(text, scheme="simple", max_length=12)
    assert slug == "" or SLUG_RE.match(slug), slug
    assert len(slug) <= 12


@given(any_text)
def test_translit_never_raises(text: str) -> None:
    to_latin(text)
    to_latin(text, scheme="simple")
    phonetic_key(text)


# --------------------------------------------------------------------------- invariants


@given(greek_text)
def test_to_latin_leaves_no_greek_letters(text: str) -> None:
    for scheme in ("elot743", "simple"):
        assert GREEK_LETTERS.isdisjoint(to_latin(text, scheme=scheme))


@given(any_text, st.integers(min_value=0, max_value=40))
def test_slug_respects_max_length(text: str, max_length: int) -> None:
    slug = slugify(text, max_length=max_length)
    assert len(slug) <= max_length
    assert slug == "" or SLUG_RE.match(slug), slug


@given(greek_text)
def test_final_sigma_only_ends_words(text: str) -> None:
    fixed = fix_final_sigma(text)
    for i, ch in enumerate(fixed):
        if ch == "ς":
            after = fixed[i + 1 : i + 2]
            assert after not in GREEK_LETTERS or after == "", fixed
            assert i > 0, fixed


@given(greek_text)
def test_upper_drops_accents_except_disjunctive_eta(text: str) -> None:
    out = unicodedata.normalize("NFD", upper(text))
    for i, ch in enumerate(out):
        if ch in "̀́͂̓̔ͅ" and i > 0 and out[i - 1] in GREEK_LETTERS:
            # Only a stand-alone Ή keeps a mark.
            assert ch == "́", out
            assert out[i - 1] == "Η", out
            assert i < 2 or not out[i - 2].isalpha(), out


@given(greek_text)
def test_phonetic_key_ignores_case_and_accents(text: str) -> None:
    key = phonetic_key(text)
    assert phonetic_key(upper(text)) == key
    assert phonetic_key(strip_accents(text, keep_dialytika=False)) == key


@given(any_text)
def test_fix_lookalikes_only_swaps_letters(text: str) -> None:
    fixed = fix_lookalikes(text)
    assert len(fixed) == len(text)
    assert all(a == b or (a.isalpha() and b.isalpha()) for a, b in zip(text, fixed, strict=True))
