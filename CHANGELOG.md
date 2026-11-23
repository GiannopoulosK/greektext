# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- `upper` keeps the accent on the disjunctive "ή" ("or"): `Μάιο ή Ιούνιο` becomes
  `ΜΑΪΟ Ή ΙΟΥΝΙΟ`, so it is not read as the article `Η`.

### Fixed

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

## [0.4.0] - 2026-11-23

### Added

- Full README, documentation site (Greek text rules, transliteration, matching Greeklish,
  command line, recipes for Django, search and keylex, API reference).
- `benchmarks/bench.py` for `fold`, `to_latin` and friends on 1 MB of Greek text.

## [0.3.0] - 2026-11-23

### Added

- `greektext` command (also `python -m greektext`) with the subcommands `normalize`, `strip`,
  `fold`, `upper`, `lower`, `latin`, `key`, `slug` and `detect`.
- Stdin streaming, global `--json` output, and exit codes 0 (success), 1 (`detect` negative)
  and 2 (usage error).
- UTF-8 input and output regardless of the console or locale encoding.

## [0.2.0] - 2026-11-23

### Added

- `to_latin` with the `elot743` (checked against the published table, see the docs) and
  `simple` schemes; case follows the source word.
- `slugify` with separator, scheme, `max_length` and `lowercase` options.
- `phonetic_key`, a script-independent sound key for matching Greek, Greeklish and
  transliterations.

## [0.1.0] - 2026-11-23

### Added

- `strip_accents` and `fold` (accent-, case- and final-sigma-insensitive search keys).
- `upper` with orthographic Greek rules (no tonos in capitals, dialytika where a tonos split a
  digraph), `lower` and `fix_final_sigma` with elision support.
- `normalize` for storage: Unicode form, whitespace, final sigma and lookalike repair.
- `greek_ratio`, `is_greek`, `fix_lookalikes` and `sort_key`.

## [0.0.1] - 2026-11-23

### Added

- Project scaffold: src layout, packaging, ruff, mypy strict, pytest, pre-commit, CI matrix,
  release workflow and an empty docs site.
- The specification's acceptance table as (pending) parametrized tests.

[Unreleased]: https://github.com/GiannopoulosK/greektext/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/GiannopoulosK/greektext/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/GiannopoulosK/greektext/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/GiannopoulosK/greektext/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/GiannopoulosK/greektext/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/GiannopoulosK/greektext/releases/tag/v0.0.1
