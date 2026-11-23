# greektext

[![CI](https://github.com/GiannopoulosK/greektext/actions/workflows/ci.yml/badge.svg)](https://github.com/GiannopoulosK/greektext/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/greektext.svg)](https://pypi.org/project/greektext/)
[![Python](https://img.shields.io/pypi/pyversions/greektext.svg)](https://pypi.org/project/greektext/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/GiannopoulosK/greektext/blob/main/LICENSE)
[![Typed](https://img.shields.io/badge/typing-mypy%20strict-informational.svg)](https://mypy.readthedocs.io/)

**Greek text made easy to compare, search, transliterate and slugify.** Accent-insensitive
search keys, correct capitals and final sigma, ELOT 743 transliteration, Greeklish matching and
URL slugs: the small things every Greek project ends up writing by hand, done correctly.

**Documentation:** <https://giannopoulosk.github.io/greektext/>

```bash
pip install greektext
```

Requires Python 3.10+. Pure Python, zero runtime dependencies, fully typed (`mypy --strict`),
tested on Linux, macOS and Windows with Python 3.10 to 3.14.

## 30-second tour

```python
>>> from greektext import fold, upper, lower, to_latin, slugify, phonetic_key

>>> fold("ΑΘΉΝΑ") == fold("Αθηνά") == fold("αθηνα")      # search keys
True
>>> upper("Μάιος"), upper("ρολόι")                       # real Greek capitals
('ΜΑΪΟΣ', 'ΡΟΛΟΪ')
>>> lower("ΟΔΟΣ ΠΑΤΡΩΝ")                                # correct final sigma
'οδος πατρων'
>>> to_latin("Θεσσαλονίκη"), to_latin("ΘΕΣΣΑΛΟΝΙΚΗ")    # ELOT 743
('Thessaloniki', 'THESSALONIKI')
>>> slugify("Ευάγγελος & Σία Ο.Ε.")
'evangelos-sia-o-e'
>>> phonetic_key("Κωνσταντίνος") == phonetic_key("Kwnstantinos") == phonetic_key("Konstantinos")
True

```

### Why greektext?

| Problem | The usual trick | What goes wrong | greektext |
|---|---|---|---|
| Accent-insensitive search | `unicodedata` NFD + drop combining marks | ς ≠ σ, case, Greek ";" and "·", decomposed vs precomposed input, polytonic marks | `fold("Οδός") == fold("ΟΔΟΣ")` |
| All-caps headings | `str.upper()` / CSS `text-transform` | keeps the tonos: `"Μάιος".upper() == "ΜΆΙΟΣ"` | `upper("Μάιος") == "ΜΑΪΟΣ"` |
| Lowercasing all caps | `str.lower()` | fine, until σ' elision or σ/ς typed wrong | `fix_final_sigma`, `lower` |
| URL slugs | Django `slugify` | deletes Greek letters: `slugify("Καλημέρα") == ""` | `slugify("Καλημέρα") == "kalimera"` |
| Transliteration | hand-written dict | αυ/ευ (av or af?), μπ (b or mp?), γγ, broken digraphs, case | `to_latin`, ELOT 743 |
| Greeklish input | ignore it | "8essalonikh", "Kwnstantinos" never match | `phonetic_key` |
| Mixed keyboards | ignore it | Latin "K" in "Kαλημέρα" breaks equality | `fix_lookalikes` |

## Comparing and searching

`fold` returns a key that ignores accents (tonos, dialytika, polytonic marks), case and final
sigma, normalizes Greek punctuation and collapses whitespace. It is idempotent.

```python
>>> from greektext import fold, strip_accents, sort_key
>>> fold("  Προϊόν   ΟΔΟΣ ")
'προιον οδοσ'
>>> strip_accents("Αθήνα προϊόν")                        # keeps the dialytika by default
'Αθηνα προϊον'
>>> strip_accents("προϊόν", keep_dialytika=False)
'προιον'
>>> sorted(["Ωραιόκαστρο", "άλφα", "Ζάκυνθος", "Έδεσσα"], key=sort_key)
['άλφα', 'Έδεσσα', 'Ζάκυνθος', 'Ωραιόκαστρο']

```

## Casing and final sigma

Greek capitals carry no tonos. When a tonos is what kept two vowels apart (`Μάιος`, not the
digraph αι), the capital form shows a dialytika instead.

```python
>>> from greektext import upper, lower, fix_final_sigma
>>> upper("καλημέρα"), upper("προϊόν"), upper("άυλος")
('ΚΑΛΗΜΕΡΑ', 'ΠΡΟΪΟΝ', 'ΑΫΛΟΣ')
>>> fix_final_sigma("οδοσ πατρων")
'οδος πατρων'
>>> fix_final_sigma("σ' αγαπώ")                         # elision: σ stays σ
"σ' αγαπώ"

```

## Cleaning up text for storage

```python
>>> from greektext import normalize, fix_lookalikes, is_greek
>>> normalize("  Τι κάνεις\u037e \n  οδοσ ")             # Greek question mark -> ";"
'Τι κάνεις; οδος'
>>> fix_lookalikes("Kαλημέρα") == "Καλημέρα"             # Latin K -> Greek Κ
True
>>> is_greek("Καλημέρα κόσμε"), is_greek("Hello world κόσμε")
(True, False)

```

## Transliteration and slugs

`to_latin` follows ELOT 743 (the Greek standard, equivalent to the UN and ISO 843
transcriptions); the `simple` scheme is friendlier for slugs. Case follows the source word.

```python
>>> from greektext import to_latin, slugify
>>> to_latin("Ευάγγελος, Αύγουστος, αυτός, Μπάμπης, Ψυχικό")
'Evangelos, Avgoustos, aftos, Bampis, Psychiko'
>>> to_latin("Ψυχικό", scheme="simple")
'Psichiko'
>>> slugify("Καλημέρα Κόσμε!"), slugify("Καλημέρα Κόσμε!", sep="_", max_length=10)
('kalimera-kosme', 'kalimera')

```

See the [transliteration guide](https://giannopoulosk.github.io/greektext/transliteration/) for
the full table and how it was verified.

## Matching Greeklish

Greeklish cannot be converted back to Greek reliably (`i` may be η, ι, υ, ει or οι), so
greektext matches it instead: `phonetic_key` maps Greek, Greeklish and transliterated spellings
of a word to the same key.

```python
>>> from greektext import phonetic_key
>>> {phonetic_key(s) for s in ["Γιώργος", "Giorgos", "giwrgos"]}
{'giorgos'}
>>> phonetic_key("Ευάγγελος") == phonetic_key("Euaggelos") == phonetic_key("Evangelos")
True

```

## Command line

```console
$ greektext upper "Μάιος"
ΜΑΪΟΣ
$ greektext slug "Ευάγγελος & Σία Ο.Ε."
evangelos-sia-o-e
$ greektext latin "ΘΕΣΣΑΛΟΝΙΚΗ"
THESSALONIKI
$ cat names.txt | greektext slug          # streams stdin line by line
$ greektext --json key Kwnstantinos
{"input": "Kwnstantinos", "output": "konstadinos"}
$ greektext detect "Hello" || echo "not Greek"
not-greek
not Greek
```

Subcommands: `normalize`, `strip`, `fold`, `upper`, `lower`, `latin`, `greek`, `key`, `slug`,
`detect`. Exit codes: 0 success, 1 `detect` negative, 2 usage error.

## Django, search and keyword matching

greektext has no framework integrations to install: every function is a plain `str -> str`
callable. The [recipes](https://giannopoulosk.github.io/greektext/recipes/) show how to use it
for Django slugs and template filters (`{{ title|greek_upper }}`), accent-insensitive search
columns and keylex keyword matching.

## Performance

Pure Python, all tables precompiled at import. On 1 MB of mixed Greek text
(`python benchmarks/bench.py`, Python 3.12, Linux x86_64):

| Function | Time (1 MB) | Throughput |
|---|---:|---:|
| `strip_accents` | 0.04 s | 23 MB/s |
| `fold` | 0.15 s | 6.5 MB/s |
| `upper` | 0.31 s | 3.2 MB/s |
| `to_latin` | 0.62 s | 1.6 MB/s |
| `slugify` | 0.69 s | 1.4 MB/s |
| `phonetic_key` | 1.01 s | 1.0 MB/s |

## Versioning

greektext follows [Semantic Versioning](https://semver.org/). The public API is everything in
`greektext.__all__` and the `greektext` command; the `greektext._*` modules are private. A
change in output that fixes a wrong result (a misspelled transliteration, a missed final sigma)
can come in a minor release and is listed in the [changelog](https://github.com/GiannopoulosK/greektext/blob/main/CHANGELOG.md); other changes to
existing output wait for a major release. The exact spelling of `phonetic_key` keys is not part
of the API: compare keys, do not store them.

## License

MIT
