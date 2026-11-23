"""Unit tests for the core text functions, beyond the acceptance table."""

from __future__ import annotations

import unicodedata

import pytest

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


def NFD(text: str) -> str:
    return unicodedata.normalize("NFD", text)


class TestStripAccents:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("ΐ", "ϊ"),
            ("ΰ", "ϋ"),
            ("Άννα Έλενα Ήρα Ίρις Όλγα Ύδρα Ώρα", "Αννα Ελενα Ηρα Ιρις Ολγα Υδρα Ωρα"),
            ("\u1f71", "α"),  # ά with oxia (Greek Extended)
            ("ἄνθρωπος", "ανθρωπος"),
            ("ᾠδή", "ωδη"),  # breathing, iota subscript, oxia
            ("τῆς", "της"),  # perispomeni
            ("ὁ", "ο"),
        ],
    )
    def test_greek_marks(self, text: str, expected: str) -> None:
        assert strip_accents(text) == expected
        assert strip_accents(NFD(text)) == expected

    def test_without_dialytika(self) -> None:
        assert strip_accents("ΐ Ϊ ϋ", keep_dialytika=False) == "ι Ι υ"

    def test_latin_marks_are_kept(self) -> None:
        assert strip_accents("naïve café") == "naïve café"

    def test_returns_nfc(self) -> None:
        out = strip_accents(NFD("προϊόν café"))
        assert unicodedata.is_normalized("NFC", out)

    def test_mark_stack_with_no_precomposed_form(self) -> None:
        # α + tonos + macron does not compose into one code point.
        assert strip_accents("α\u0301\u0304β") == "αβ"
        assert strip_accents("ι\u0304\u0308", keep_dialytika=True) == "ϊ"
        assert strip_accents("e\u0304\u0301") == unicodedata.normalize("NFC", "e\u0304\u0301")


class TestFold:
    def test_strips_latin_accents(self) -> None:
        assert fold("Café NAÏVE") == "cafe naive"

    def test_punctuation_and_apostrophes(self) -> None:
        assert fold("σ\u2019 αγαπώ\u037e") == "σ' αγαπω;"
        assert fold("α\u0387β") == "α\u00b7β"

    def test_whitespace(self) -> None:
        assert fold("  ΚΑΛΗ\n\tΜΕΡΑ ") == "καλη μερα"

    def test_casefold_marks(self) -> None:
        assert fold("İstanbul") == "istanbul"
        assert fold("ΐ") == "ι"

    def test_empty(self) -> None:
        assert fold("") == ""


class TestUpper:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("άυλος", "ΑΫΛΟΣ"),
            ("γάιδαρος", "ΓΑΪΔΑΡΟΣ"),
            ("κέικ", "ΚΕΪΚ"),
            ("Ταΰγετος", "ΤΑΫΓΕΤΟΣ"),  # dialytika already present
            ("καΐκι", "ΚΑΪΚΙ"),
            ("αίμα", "ΑΙΜΑ"),  # tonos on the second vowel: a real digraph
            ("ευχή", "ΕΥΧΗ"),
            ("Ἀθῆναι", "ΑΘΗΝΑΙ"),
            ("ᾠδή", "ΩΔΗ"),
            ("ΆΙ", "ΑΪ"),
            ("άα", "ΑΑ"),  # not a digraph pair
            ("straße", "STRASSE"),
            ("ü", "Ü"),
            ("", ""),
        ],
    )
    def test_cases(self, text: str, expected: str) -> None:
        assert upper(text) == expected
        assert upper(NFD(text)) == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("ή", "Ή"),
            ("Ή", "Ή"),
            ("ή,", "Ή,"),
            ("(ή)", "(Ή)"),
            ("ἤ ἢ", "Ή Ή"),  # polytonic
            ("η", "Η"),  # the article
            ("ήταν", "ΗΤΑΝ"),  # ή inside a word
            ("ήx", "ΗX"),  # followed by a letter: not a word on its own
            ("xή", "XΗ"),
        ],
    )
    def test_disjunctive_eta(self, text: str, expected: str) -> None:
        assert upper(text) == expected
        assert upper(NFD(text)) == expected

    def test_tonos_does_not_leak_across_words(self) -> None:
        assert upper("πά ιδέα") == "ΠΑ ΙΔΕΑ"

    @pytest.mark.parametrize("text", ["\u0345", "A\u0345", " \u0345x"])
    def test_stray_iota_subscript_is_dropped(self, text: str) -> None:
        assert "\u0399" not in upper(text)  # not turned into a capital iota
        assert fold(upper(text)) == fold(text)

    def test_tonos_does_not_leak_across_non_greek(self) -> None:
        assert upper("ά-ι") == "Α-Ι"


class TestFinalSigma:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("ο δρομοσ, ο κοσμοσ.", "ο δρομος, ο κοσμος."),
            ("ςας", "σας"),
            ("ΟΔΟσ", "ΟΔΟς"),
            ("σ", "σ"),
            ("σ'", "σ'"),
            ("κ.σ.", "κ.σ."),
            ("κ.ς.", "κ.σ."),  # an initial is not the end of a word
            ("ς", "σ"),
            (" ς", " σ"),
            ("α.ε.ς", "α.ε.σ"),
            ("εσ' ", "εσ' "),
            ("πασ\u02bc", "πασ\u02bc"),
            ("οδοσ2", "οδοσ2"),  # digits continue the word
            ("abσ", "abσ"),  # not a Greek word
            ("οδο\u0301σ", "οδο\u0301ς"),  # decomposed accent before σ
            ("hello", "hello"),
        ],
    )
    def test_cases(self, text: str, expected: str) -> None:
        assert fix_final_sigma(text) == expected

    def test_lower(self) -> None:
        assert lower("ΚΑΛΗΣΠΕΡΑ ΣΑΣ") == "καλησπερα σας"
        assert lower("ΣΑΣ'") == "σας'"
        assert lower("Σ.Τ.Ε. Κ.Σ.") == "σ.τ.ε. κ.σ."


class TestNormalize:
    def test_forms(self) -> None:
        assert normalize("ά", form="NFD") == "α\u0301"
        assert normalize("ﬁ", form="NFKC") == "fi"
        with pytest.raises(ValueError, match="form"):
            normalize("x", form="NFX")

    def test_flags(self) -> None:
        assert normalize(" οδοσ ", whitespace=False, final_sigma=False) == " οδοσ "
        assert normalize("Kαλημέρα", lookalikes=True) == "Καλημέρα"
        assert normalize("Kαλημέρα") == "Kαλημέρα"

    def test_ascii_untouched(self) -> None:
        assert normalize("Hello, world!") == "Hello, world!"


class TestScript:
    def test_ratio(self) -> None:
        assert greek_ratio("") == 0.0
        assert greek_ratio("αβγ d") == 0.75
        assert greek_ratio("ϢϣϤ") == 0.0  # Coptic is not Greek

    def test_is_greek_threshold(self) -> None:
        assert is_greek("Hello κόσμε") is True  # exactly 0.5
        assert is_greek("", threshold=0.0) is True
        assert is_greek("abc", threshold=0.01) is False

    def test_lookalikes(self) -> None:
        assert fix_lookalikes("TAXI") == "TAXI"
        assert fix_lookalikes("ΑB") == "ΑB"  # one each: no majority
        assert fix_lookalikes("ΚAΦΕ") == "ΚΑΦΕ"
        assert fix_lookalikes("Bοok") == "Book"
        assert fix_lookalikes("123 Kαι") == "123 Και"
        assert fix_lookalikes(NFD("Kαλημέρα")) == NFD("Καλημέρα")

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("AΘΗNA", "ΑΘΗΝΑ"),  # 3 Latin vs 2 Greek, but Θ is Greek-only
            ("AΘHNA", "ΑΘΗΝΑ"),  # only Θ is Greek
            ("ΚAΦE", "ΚΑΦΕ"),  # tie, Φ decides
            ("ΤΑXΙ", "ΤΑΧΙ"),  # no Greek-only letter: majority
            ("HΟTΕL", "HOTEL"),  # L is Latin-only
            ("Tαxi", "Tαxi"),  # α and x have no twins: majority Latin, α left alone
            ("ΑB", "ΑB"),  # all twins, tie
        ],
    )
    def test_lookalikes_letters_without_twin_decide(self, text: str, expected: str) -> None:
        assert fix_lookalikes(text) == expected

    def test_sort_key(self) -> None:
        words = ["σύκο", "Σάμος", "ρόδι", "ωμέγα", "Άλφα", "ΒΗΤΑ", "ς"]
        assert sorted(words, key=sort_key) == [
            "Άλφα",
            "ΒΗΤΑ",
            "ρόδι",
            "ς",
            "Σάμος",
            "σύκο",
            "ωμέγα",
        ]
        assert sort_key("Α") < sort_key("α")  # deterministic tie-break
