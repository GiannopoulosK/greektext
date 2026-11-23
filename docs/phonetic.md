# Matching Greeklish

People type Greek names in Greek, in Greeklish (`Kwnstantinos`, `8essalonikh`) and in
transliteration (`Konstantinos`, `Thessaloniki`). Converting Greeklish back to Greek is
ambiguous (`i` may be η, ι, υ, ει or οι), so greektext does not try. Instead, `phonetic_key`
maps every spelling to one lowercase Latin sound key, and you compare keys:

```python
>>> from greektext import phonetic_key
>>> phonetic_key("Κωνσταντίνος") == phonetic_key("Konstantinos") == phonetic_key("Kwnstantinos")
True
>>> {phonetic_key(s) for s in ["Αθήνα", "Athina", "A8hna"]}
{'athina'}
>>> phonetic_key("Ευάγγελος") == phonetic_key("Evangelos") == phonetic_key("Euaggelos")
True

```

Store the key next to the name (or compute it on the fly) and look names up by key. The key is
lossy by design and its exact spelling may change between minor versions, so do not use it as a
permanent identifier.

## How the key is built

1. `fold`: no accents, no case, ς → σ.
2. Greek words: ELOT 743 transliteration with ξ → `ks` and χ → `x`, and a nasal γ before ξ or χ
   written `g`.
3. Latin text: Greeklish aliases. w → o, h → i (except in th and ch), 8 → th, 3 → ks, c → k,
   ch → x, u/y after a, e or h → v (αυ, ευ, ηυ), oy → ou.
4. Drop everything that is not a letter.
5. Repeat until nothing changes: i/y/ei/oi/yi → i, w → o, ai → e, af/au → av, ef/eu → ev,
   if → iv, ng/gk/gg → g, nx → gx, mp → b, nt → d, ch → x, ou → u, collapse doubled letters.

Repeating step 5 until it is stable makes the key idempotent:
`phonetic_key(phonetic_key(x)) == phonetic_key(x)`.

The key writes the χ sound as `x`, the way Greeklish spells it. Writing it as `h` would not be
stable, because a Latin `h` on its own is read as η.

## Known limitations

- `th` is always θ: `Panagiwths` (Παναγιώτης, written with `th` for τη) gets a different key
  from `Panagiotis`.
- A Latin `x` is χ, as in Greeklish. ELOT 743 also writes ξ as `x` (`Xanthi`), so
  ELOT-transliterated words with ξ do not match their Greek spelling; `Ksanthi` does.
- The dialytika is dropped by `fold`, so `αϋπνία` is keyed like `αυπνία`.
- A lone Latin `b` is the μπ sound (`Bampis` matches `Μπάμπης`), not β.
- Unrelated words can share a key (`Bory` and `μπορεί`). Use the key to find candidates, not as
  proof that two names are the same.
