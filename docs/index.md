# greektext

**Greek text made easy to compare, search, transliterate and slugify.**

greektext is a small, zero-dependency Python library and CLI for the everyday problems of Greek
text: accents breaking search, a wrong final sigma, all-caps headings that keep the tonos,
Greeklish user input and URL slugs.

```bash
pip install greektext
```

```python
>>> from greektext import fold, upper, to_latin, slugify, phonetic_key
>>> fold("ΑΘΉΝΑ") == fold("Αθηνά") == fold("αθηνα")
True
>>> upper("Μάιος")
'ΜΑΪΟΣ'
>>> to_latin("Θεσσαλονίκη")
'Thessaloniki'
>>> slugify("Ευάγγελος & Σία Ο.Ε.")
'evangelos-sia-o-e'
>>> phonetic_key("Κωνσταντίνος") == phonetic_key("Kwnstantinos")
True

```

## Where to go next

- [Greek text rules](rules.md): the language rules every function follows, and the core
  functions that apply them (`fold`, `strip_accents`, `upper`, `lower`, `fix_final_sigma`,
  `normalize`, `fix_lookalikes`, `is_greek`, `sort_key`).
- [Transliteration](transliteration.md): `to_latin`, the ELOT 743 and `simple` schemes, and how
  the table was verified.
- [Matching Greeklish](phonetic.md): `phonetic_key` and its limits.
- [Command line](cli.md)
- [Recipes](recipes.md): Django templates and slugs, keyword matching.
- [API reference](api.md)

## Non-goals

Stemming, lemmatization, spell-checking or NLP models; Greeklish → Greek conversion (it is
ambiguous, so greektext matches Greeklish with `phonetic_key` instead); restoring missing
accents; generating polytonic text; database-level search features (PostgreSQL `unaccent`,
collations); framework integrations (see [Recipes](recipes.md)).
