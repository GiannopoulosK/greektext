"""Tests for transliteration, phonetic keys and slugs."""

from __future__ import annotations

import unicodedata

import pytest

from greektext import phonetic_key, slugify, to_latin

# Worked examples of the ELOT 743 / BGN-PCGN 1996 table (UK government "Romanization of Greek",
# checked October 2017). The official romanization marks stress and dieresis; greektext writes
# plain ASCII, so the expected values are compared without them.
_ELOT743_OFFICIAL = """
Άρτα Árta | Ακταίο Aktaío | Νεράϊδα Neráïda | Μαυροβούνι Mavrovoúni | Ναύπλιο Náfplio
Βόλος Vólos | Γαράζο Garázo | Γουριά Gouriá | Άγναντα Ágnanta | Γλυφάδα Glyfáda
Αγχίαλος Anchíalos | Λόγγος Lóngos | Λαγκάδα Lagkáda | Δένδρα Déndra | Ερέτρια Erétria
Ηράκλειο Irákleio | Μαρινέϊκα Marinéïka | Ρεύματα Révmata | Λευκάδα Lefkáda | Ζεμενό Zemenó
Θεσπιές Thespiés | Ίρια Íria | Καλαμάκι Kalamáki | Λίμνη Límni | Μαραθώνας Marathónas
Μπέχρος Béchros | Τέμπη Témpi | Νεστάνη Nestáni | Ντία Ntía | Ξάνθη Xánthi | Όθος Óthos
Δελφοί Delfoí | Δοϊράνι Doïráni | Βούναργο Voúnargo | Παύλος Pávlos | Μερόπι Merópi
Άσσος Ássos | Σάμος Sámos | Τίρυνθα Tíryntha | Υλίκη Ylíki | Φιλοθέη Filothéi
Χαραυγή Charavgí | Ψαρά Psará | Ωρωπός Oropós | Αθήνα Athína | Οινούσσες Oinoússes
Οίτη Oíti | Αύρα Ávra | Γαύριο Gávrio | Καλλιπεύκα Kallipéfka
"""


def _plain(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


@pytest.mark.parametrize(
    ("greek", "official"),
    [
        tuple(pair.split())
        for line in _ELOT743_OFFICIAL.strip().splitlines()
        for pair in line.split(" | ")
    ],
)
def test_elot743_official_examples(greek: str, official: str) -> None:
    assert to_latin(greek) == _plain(official)


def test_elot743_official_example_with_two_words() -> None:
    assert to_latin("Πέντε Βρύσες") == "Pente Vryses"


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
            # a single capital letter takes the case of an all-caps neighbour
            ("Θ. ΠΑΠΑΔΟΠΟΥΛΟΣ", "TH. PAPADOPOULOS"),
            ("ΠΑΠΑΔΟΠΟΥΛΟΣ Θ.", "PAPADOPOULOS TH."),
            ("Θ. Smith ΠΑΠΑ", "Th. Smith PAPA"),  # other letters stop the search
            ("Ψ Θ", "Ps Th"),
            ("Η ΘΕΣΗ ΤΟΥ Χ", "I THESI TOU CH"),
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
    def test_digits_are_letters_only_inside_words(self) -> None:
        assert phonetic_key("A8hna") == phonetic_key("Αθήνα")
        assert phonetic_key("3ypnhsa") == phonetic_key("Ξύπνησα")
        assert phonetic_key("Οδός Ερμού 38") == phonetic_key("Οδός Ερμού")
        assert phonetic_key("2023") == phonetic_key("1999") == ""

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

    @pytest.mark.parametrize("sep", ["a", "-1-", "Z"])
    def test_alphanumeric_separator(self, sep: str) -> None:
        with pytest.raises(ValueError, match="sep"):
            slugify("Ά-ή", sep=sep)

    def test_empty_and_unicode_separators(self) -> None:
        assert slugify("Καλημέρα Κόσμε", sep="") == "kalimerakosme"
        assert slugify("Καλημέρα Κόσμε", sep="·") == "kalimera·kosme"

    def test_negative_max_length(self) -> None:
        with pytest.raises(ValueError, match="max_length"):
            slugify("α", max_length=-1)
