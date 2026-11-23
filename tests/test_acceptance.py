"""The acceptance table from the specification, written before the implementation.

Every row here must pass for a release.
"""

from __future__ import annotations

import pytest

from greektext import (
    fix_final_sigma,
    fix_lookalikes,
    fold,
    is_greek,
    lower,
    normalize,
    phonetic_key,
    slugify,
    strip_accents,
    to_latin,
    upper,
)


@pytest.mark.parametrize(
    ("text", "kwargs", "expected"),
    [
        ("Αθήνα", {}, "Αθηνα"),
        ("προϊόν", {}, "προϊον"),
        ("προϊόν", {"keep_dialytika": False}, "προιον"),
        ("α\u0301", {}, "α"),  # decomposed input
    ],
)
def test_strip_accents(text: str, kwargs: dict[str, bool], expected: str) -> None:
    assert strip_accents(text, **kwargs) == expected


def test_fold_makes_spellings_equal() -> None:
    assert fold("ΑΘΉΝΑ") == fold("Αθηνά") == fold("αθηνα")


def test_fold_final_sigma() -> None:
    assert fold("οδός") == "οδοσ"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("καλημέρα", "ΚΑΛΗΜΕΡΑ"),
        ("Μάιος", "ΜΑΪΟΣ"),
        ("ρολόι", "ΡΟΛΟΪ"),
        ("προϊόν", "ΠΡΟΪΟΝ"),
        ("Μάιο ή Ιούνιο", "ΜΑΪΟ Ή ΙΟΥΝΙΟ"),  # the disjunctive ή keeps its accent
    ],
)
def test_upper(text: str, expected: str) -> None:
    assert upper(text) == expected


def test_lower() -> None:
    assert lower("ΟΔΟΣ ΠΑΤΡΩΝ") == "οδος πατρων"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("οδοσ πατρων", "οδος πατρων"),
        ("σ' αγαπώ", "σ' αγαπώ"),
        ("σ\u2019 αγαπώ", "σ\u2019 αγαπώ"),
    ],
)
def test_fix_final_sigma(text: str, expected: str) -> None:
    assert fix_final_sigma(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Τι κάνεις\u037e", "Τι κάνεις;"),
        (" Πάτρα \n", "Πάτρα"),
    ],
)
def test_normalize(text: str, expected: str) -> None:
    assert normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Πάτρα", "Patra"),
        ("Θεσσαλονίκη", "Thessaloniki"),
        ("ΘΕΣΣΑΛΟΝΙΚΗ", "THESSALONIKI"),
        ("Χανιά", "Chania"),
        ("Ευάγγελος", "Evangelos"),
        ("Αύγουστος", "Avgoustos"),
        ("αυτός", "aftos"),
        ("Μπάμπης", "Bampis"),
        ("Ψυχικό", "Psychiko"),
        ("άυλος", "aylos"),
    ],
)
def test_to_latin(text: str, expected: str) -> None:
    assert to_latin(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Καλημέρα Κόσμε!", "kalimera-kosme"),
        ("Ευάγγελος & Σία Ο.Ε.", "evangelos-sia-o-e"),
    ],
)
def test_slugify(text: str, expected: str) -> None:
    assert slugify(text) == expected


@pytest.mark.parametrize(
    "spellings",
    [
        ("Κωνσταντίνος", "Konstantinos", "Kwnstantinos"),
        ("Γιώργος", "Giorgos", "giwrgos"),
        ("Αθήνα", "Athina", "A8hna"),
        ("Ευάγγελος", "Evangelos", "Euaggelos"),
    ],
)
def test_phonetic_key_collides(spellings: tuple[str, ...]) -> None:
    keys = {phonetic_key(s) for s in spellings}
    assert len(keys) == 1, keys


def test_fix_lookalikes_latin_k_in_greek_word() -> None:
    assert fix_lookalikes("Kαλημέρα") == "Καλημέρα"  # Latin K -> Greek Κ


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # The spec's example "Hello κόσμε" sits exactly on the default threshold (5 Latin and
        # 5 Greek letters, ratio 0.5), so with ``>=`` it is Greek. The intent of the row,
        # "below 0.5 is not Greek", is kept with an input that is really below it.
        ("Hello world κόσμε", False),
        ("Hello κόσμε", True),
    ],
)
def test_is_greek(text: str, expected: bool) -> None:
    assert is_greek(text) is expected
