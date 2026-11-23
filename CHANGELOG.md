# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/GiannopoulosK/greektext/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/GiannopoulosK/greektext/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/GiannopoulosK/greektext/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/GiannopoulosK/greektext/releases/tag/v0.0.1
