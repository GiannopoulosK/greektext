# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-11-23

First release on PyPI. The public API is `greektext.__all__` and the `greektext` command.

### Changed

- The implementation modules are private (`greektext._accents`, `greektext._translit`, ...);
  import everything from `greektext`. This also stops the `normalize` function from shadowing a
  module of the same name.
- `normalize(form=...)`, `to_latin(scheme=...)` and `slugify(scheme=...)` are typed as
  `Literal`s, so type checkers catch an unknown name.
- `is_greek` raises `ValueError` for a threshold outside 0 to 1, like the CLI.
- `slugify` raises `ValueError` for a separator that contains letters or digits; the CLI
  `--sep` option exits 2.
- CLI exit codes: a closed output pipe exits 141 and Ctrl-C exits 130 (both used to exit 1, the
  `detect` "not Greek" code). `detect` echoes blank lines and does not count them.
- `upper` keeps the accent on the disjunctive "ή" ("or"): `Μάιο ή Ιούνιο` becomes
  `ΜΑΪΟ Ή ΙΟΥΝΙΟ`, so it is not read as the article `Η`.
- `to_latin` writes a single capital letter next to an all-caps word in all caps:
  `Θ. ΠΑΠΑΔΟΠΟΥΛΟΣ` becomes `TH. PAPADOPOULOS` instead of `Th. PAPADOPOULOS`.
- The source distribution includes the docs, benchmark and contributing guide, so the
  documentation examples are tested from the sdist too.

### Fixed

- Invisible format characters inside a word (soft hyphen, zero-width joiners, word joiner, BOM)
  no longer split it: `lower("ΘΕΣ\u00adΣΑΛΟΝΙΚΗ")` keeps σ, `to_latin("Ευ\u00adρώπη")` is
  `Evropi`, and `fold` removes them.
- `fix_final_sigma` only counts marks on Greek letters, so decomposed and precomposed `caféσ`
  give the same result.
- `normalize(..., lookalikes=True)` returns the requested Unicode form.
- `slugify` with `max_length` is linear instead of quadratic in the number of words.
- `phonetic_key` reads Greeklish 8 and 3 as letters only inside a word; a stand-alone number
  is dropped like other digits.
- The spacing ypogegrammeni (U+037A) is read as an iota subscript instead of becoming a space
  in `to_latin`.
- The CLI drops a UTF-8 BOM at the start of stdin, reports a closed stdin as a usage error,
  and explains bad `--max-length` and `--threshold` values.
- `fix_lookalikes` no longer makes all-caps Greek words worse: a letter that only exists in one
  script now decides the word when every letter of the other script has a twin, so `AΘΗNA`
  becomes `ΑΘΗΝΑ` instead of `AΘHNA`.
- `fix_final_sigma` (and so `lower`) turns a ς with no letter before it into σ: abbreviations
  such as `Κ.Σ.` now lowercase to `κ.σ.`, not `κ.ς.`.
- `phonetic_key` matches common English-style spellings: y before i/e is γ (`Yiannis`,
  `Panayiotis`) and `ph` is φ (`Photis`).
- CLI `--json` output is always valid UTF-8: input bytes that are not UTF-8 become U+FFFD in
  JSON (plain output still passes them through unchanged).
- CLI `detect` exits 1 on empty input instead of succeeding vacuously, and `--threshold`
  must be between 0 and 1.
- `upper` drops a stray iota subscript (U+0345) that is not on a Greek letter instead of
  turning it into a capital iota.

## Development milestones

The versions below were development milestones before the first release and were not
published.

### 0.4.0

- Full README, documentation site (Greek text rules, transliteration, matching Greeklish,
  command line, recipes for Django, search and keylex, API reference).
- `benchmarks/bench.py` for `fold`, `to_latin` and friends on 1 MB of Greek text.

### 0.3.0

- `greektext` command (also `python -m greektext`) with the subcommands `normalize`, `strip`,
  `fold`, `upper`, `lower`, `latin`, `key`, `slug` and `detect`.
- Stdin streaming, global `--json` output, and exit codes 0 (success), 1 (`detect` negative)
  and 2 (usage error).
- UTF-8 input and output regardless of the console or locale encoding.

### 0.2.0

- `to_latin` with the `elot743` (checked against the published table, see the docs) and
  `simple` schemes; case follows the source word.
- `slugify` with separator, scheme, `max_length` and `lowercase` options.
- `phonetic_key`, a script-independent sound key for matching Greek, Greeklish and
  transliterations.

### 0.1.0

- `strip_accents` and `fold` (accent-, case- and final-sigma-insensitive search keys).
- `upper` with orthographic Greek rules (no tonos in capitals, dialytika where a tonos split a
  digraph), `lower` and `fix_final_sigma` with elision support.
- `normalize` for storage: Unicode form, whitespace, final sigma and lookalike repair.
- `greek_ratio`, `is_greek`, `fix_lookalikes` and `sort_key`.

### 0.0.1

- Project scaffold: src layout, packaging, ruff, mypy strict, pytest, pre-commit, CI matrix,
  release workflow and an empty docs site.
- The specification's acceptance table as (pending) parametrized tests.

[Unreleased]: https://github.com/GiannopoulosK/greektext/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/GiannopoulosK/greektext/releases/tag/v1.0.0
