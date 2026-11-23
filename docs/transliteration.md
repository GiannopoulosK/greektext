# Transliteration

`to_latin` converts Greek to Latin. It is deterministic and follows **ELOT 743** by default.

## Scheme `elot743`

Rules are applied longest match first on the unaccented letters. The original accents are still
used to spot *broken* digraphs: a tonos on the first vowel or a dialytika on the second keeps the
two vowels apart (`άυλος` → `aylos`, `αϋπνία` → `aypnia`, `ρολόι` → `roloi`).

| Greek | Latin | Notes |
|---|---|---|
| α β γ δ ε ζ | a v g d e z | |
| η θ ι κ λ μ | i th i k l m | |
| ν ξ ο π ρ σ/ς | n x o p r s | |
| τ υ φ χ ψ ω | t y f ch ps o | |
| αι ει οι ου υι | ai ei oi ou yi | |
| αυ ευ ηυ | av ev iv / af ef if | v before a vowel or β γ δ ζ λ μ ν ρ; f before θ κ ξ π σ τ φ χ ψ or at the end of a word |
| γγ γκ γξ γχ | ng gk nx nch | |
| μπ | b / mp | b at the start or end of a word, mp inside |
| ντ | nt | |

### Source and verification

ELOT 743 (2nd edition, 2001) type 2 *transcription* is the system also published by the UN
(1987) and as ISO 843:1997 transcription; they are essentially equivalent. The table above was
checked row by row on 2026-11-23 against the primary sources: the UNGEGN Working Group on
Romanization Systems [report on Greek](https://unstats.un.org/unsd/ungegn/working_groups/wg5/documents/wgrr4greek.pdf)
(the UN system, "based on the ELOT 743 conversion system") and the UK government
[Romanization of Greek](https://assets.publishing.service.gov.uk/media/5ab4df04e5274a1aa2d41460/ROMANIZATION_OF_GREEK.pdf)
(ELOT 743, BGN/PCGN 1996 agreement), whose worked examples are part of the test suite:

| Row | Result |
|---|---|
| Single letters | match (η → i, υ → y, χ → ch, ω → o; ELOT uses no macrons, unlike the UN column) |
| αι ει οι ου υι | match |
| αυ ευ ηυ | match: v "before vowels or voiced consonants", f "before voiceless consonants and word-finally" |
| γγ γξ γχ | match (ng, nx, nch) |
| γκ | match: *gk* in every position, "converted according to the conversion rules of each character" (`Λαγκάδα` → `Lagkada`). The *ng* for a medial γκ found in some summaries comes from the older BGN/PCGN 1962 system, which ELOT 743 replaced in 1996. |
| μπ | match: b word-initially and word-finally, mp inside |
| ντ | match: nt in every position |
| Broken digraphs | match: "an accent over the first letter of the pair indicates vowels which should be taken (and romanized) separately"; a diaeresis on the second letter does the same |

The first-edition ELOT 743 and the UN system additionally put a diaeresis on the Latin vowel of a
broken digraph (`aÿlos`); greektext does not, so its output stays plain ASCII.

## Scheme `simple`

For slugs and casual display. Same as `elot743` except:

- η, ι, υ, ει, οι, υι → `i`
- ξ → `ks`
- αυ / ευ → `av` / `ev` always
- γκ → `g` at the start of a word

## Case

Case follows the source word. A Greek word in all caps (two or more letters) gives all caps:
`ΘΕΣΣΑΛΟΝΙΚΗ` → `THESSALONIKI`. Otherwise a capital Greek letter capitalizes only the first Latin
letter of its output: `Θεσσαλονίκη` → `Thessaloniki`, `Χανιά` → `Chania`, `Ψ` → `Ps`.

A single capital letter is ambiguous, so it follows its nearest Greek neighbour: next to an
all-caps word it is part of an all-caps line (`Θ. ΠΑΠΑΔΟΠΟΥΛΟΣ` → `TH. PAPADOPOULOS`),
otherwise it is a capital (`Θ. Παπαδόπουλος` → `Th. Papadopoulos`).
