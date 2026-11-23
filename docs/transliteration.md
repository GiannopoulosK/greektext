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
checked row by row on 2026-11-23 against the Modern Greek comparison table in
[Romanization of Greek](https://en.wikipedia.org/wiki/Romanization_of_Greek) (Wikipedia, ELOT 743 /
UN columns):

| Row | Result |
|---|---|
| Single letters | match (η → i, υ → y, χ → ch, ω → o; ELOT uses no macrons, unlike the UN column) |
| αι ει οι ου υι | match |
| αυ ευ ηυ | match: v "before vowels or voiced consonants", f "before voiceless consonants and word-finally" |
| γγ γξ γχ | match (ng, nx, nch) |
| γκ | **differs**: the Wikipedia table lists *gk* word-initially and *ng* word-medially, while other summaries of ELOT 743 give *gk* in every position. greektext follows the specification and always writes *gk* (`αγκάθι` → `agkathi`). This row should be re-checked against the ELOT 743 standard text itself. |
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
