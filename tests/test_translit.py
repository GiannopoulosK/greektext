"""Tests for transliteration, phonetic keys and slugs."""

from __future__ import annotations

import unicodedata

import pytest

from greektext import phonetic_key, slugify, to_latin


class TestElot743:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            # single letters
            ("αβγδεζηθικλμνξοπρστυφχψω", "avgdezithiklmnxoprstyfchpso"),
            ("ς", "s"),
            # vowel digraphs
            ("αι ει οι ου υι", "ai ei oi ou yi"),
            # αυ ευ ηυ: v before vowels and voiced consonants, f before voiceless / at the end
            ("αυγό", "avgo"),
            ("Ευρώπη", "Evropi"),
            ("ηύρα", "ivra"),
            ("αυτός", "aftos"),
            ("ευχή", "efchi"),
            ("ταυ", "taf"),
            ("ευθύνη", "efthyni"),
            # broken digraphs
            ("αϋπνία", "aypnia"),
            ("άυλος", "aylos"),
            ("Μάιος", "Maios"),
            ("ρολόι", "roloi"),
            ("προϊόν", "proion"),
            ("ΑΫΠΝΙΑ", "AYPNIA"),
            # consonant digraphs
            ("Άγγελος", "Angelos"),
            ("αγκάθι", "agkathi"),
            ("Αγκίστρι", "Agkistri"),
            ("σφίγξ", "sfinx"),
            ("Αγχίαλος", "Anchialos"),
            ("Ντίνος", "Ntinos"),
            # μπ
            ("μπαμπάς", "bampas"),
            ("Λάμπ", "Lab"),
            ("κάμπος", "kampos"),
            # polytonic
            ("ἁγία Σοφία", "agia Sofia"),
            ("ᾠδή", "odi"),
            # case handling
            ("ΘΕΣΣΑΛΟΝΙΚΗ", "THESSALONIKI"),
            ("Θ. Παπαδόπουλος", "Th. Papadopoulos"),
            ("ΨΗΦΟΣ", "PSIFOS"),
            ("ΧΑΝΙΑ Χανιά", "CHANIA Chania"),
            ("ΜΠΑΜΠΗΣ", "BAMPIS"),
            ("Ο", "O"),
            ("ΟΙ", "OI"),
            ("Ψ", "Ps"),
            # pass-through
            ("Hello, κόσμε! 123", "Hello, kosme! 123"),
            ("ϝ", "ϝ"),  # archaic letters have no mapping
            ("", ""),
        ],
    )
    def test_cases(self, text: str, expected: str) -> None:
        assert to_latin(text) == expected

    def test_decomposed_input(self) -> None:
        assert to_latin(unicodedata.normalize("NFD", "άυλος Αύγουστος")) == "aylos Avgoustos"

    def test_unknown_scheme(self) -> None:
        with pytest.raises(ValueError, match="scheme"):
            to_latin("α", scheme="iso")


class TestSimple:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Ψυχικό", "Psichiko"),
            ("ει οι υι η ι υ", "i i i i i i"),
            ("Ξάνθη", "Ksanthi"),
            ("αυτός ευχή", "avtos evchi"),
            ("ηυ", "if"),
            ("γκρεμός αγκάθι", "gremos agkathi"),
            ("Γκρεμός", "Gremos"),
        ],
    )
    def test_cases(self, text: str, expected: str) -> None:
        assert to_latin(text, scheme="simple") == expected


class TestPhoneticKey:
    @pytest.mark.parametrize(
        "spellings",
        [
            ("Θεσσαλονίκη", "Thessaloniki", "8essalonikh", "Thesaloniki"),
            ("Χανιά", "Xania", "Chania"),
            ("Αυτοκίνητο", "aftokinito", "autokinhto", "aytokinito"),
            ("Μπάμπης", "Bampis", "Mpampis", "Babis"),
            ("Ντίνος", "Dinos", "Ntinos"),
            ("Παναγιώτης", "Panagiotis", "Panagiwtis"),
            ("Ξάνθη", "Ksanthi", "3anthi"),
            ("Αιγαίο", "Egeo", "Aigaio"),
            ("ουρανός", "uranos", "ouranos"),
            ("Γιάννης", "Giannis", "Yiannis", "Giannhs"),
            ("Παναγιώτης", "Panayiotis", "Panagiotis"),
            ("Γεώργιος", "Georgios", "Yeorgios"),
            ("Φώτης", "Fotis", "Photis", "Fwtis"),
            ("Χρήστος", "Christos", "Xristos", "Xrhstos"),
        ],
    )
    def test_collides(self, spellings: tuple[str, ...]) -> None:
        keys = {phonetic_key(s) for s in spellings}
        assert len(keys) == 1, keys

    def test_distinct_words_stay_distinct(self) -> None:
        assert phonetic_key("Αθήνα") != phonetic_key("Πάτρα")

    def test_drops_non_letters(self) -> None:
        assert phonetic_key("Α.Θ.Η.Ν.Α. 2024!") == phonetic_key("Αθηνα")
        assert phonetic_key("") == ""

    def test_nth_is_n_plus_th(self) -> None:
        assert phonetic_key("Ανθή") == "anthi"

    def test_y_before_i_is_gamma_not_upsilon(self) -> None:
        # "ay" is αυ (av) before a consonant, but "ayi" is a + γι.
        assert phonetic_key("aytos") == phonetic_key("αυτός")
        assert phonetic_key("Panayiotis") != phonetic_key("Panaviotis")


class TestSlugify:
    @pytest.mark.parametrize(
        ("text", "kwargs", "expected"),
        [
            ("Καλημέρα Κόσμε!", {}, "kalimera-kosme"),
            ("  --Γειά σου--  ", {}, "geia-sou"),
            ("Τ'αστέρια", {}, "tasteria"),
            ("Café Ζυθοποιία", {}, "cafe-zythopoiia"),
            ("Ψυχικό 2024", {"scheme": "simple"}, "psichiko-2024"),
            ("Καλημέρα Κόσμε", {"sep": "_"}, "kalimera_kosme"),
            ("Καλημέρα Κόσμε", {"lowercase": False}, "Kalimera-Kosme"),
            ("Καλημέρα Κόσμε", {"max_length": 8}, "kalimera"),
            ("Καλημέρα Κόσμε", {"max_length": 13}, "kalimera"),
            ("Καλημέρα Κόσμε", {"max_length": 14}, "kalimera-kosme"),
            ("Καλημέρα Κόσμε", {"max_length": 4}, "kali"),
            ("Καλημέρα", {"max_length": 0}, ""),
            ("!!!", {}, ""),
            ("😀 ☃", {}, ""),
        ],
    )
    def test_cases(self, text: str, kwargs: dict[str, object], expected: str) -> None:
        assert slugify(text, **kwargs) == expected  # type: ignore[arg-type]

    def test_negative_max_length(self) -> None:
        with pytest.raises(ValueError, match="max_length"):
            slugify("α", max_length=-1)
