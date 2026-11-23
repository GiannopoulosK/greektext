"""Benchmark fold and to_latin on 1 MB of Greek text.

Usage::

    python benchmarks/bench.py [--size-mb 1] [--repeat 5]

Prints the best-of-N time and throughput for each function. The text is a mix of monotonic
prose, names, all-caps headings and some polytonic words, repeated to the requested size.
"""

from __future__ import annotations

import argparse
import platform
import timeit

import greektext

SAMPLE = """\
Η Θεσσαλονίκη είναι η δεύτερη μεγαλύτερη πόλη της Ελλάδας. Ο Ευάγγελος και ο Κωνσταντίνος
ζουν στην οδό Αγίας Σοφίας και τον Μάιο πηγαίνουν στα Χανιά με το πλοίο. ΑΥΤΟΚΙΝΗΤΑ, ΠΡΟΪΟΝΤΑ
ΚΑΙ ΥΠΗΡΕΣΙΕΣ Α.Ε. Το προϊόν παραδίδεται αυθημερόν· τι κάνεις; Ἐν ἀρχῇ ἦν ὁ λόγος.
Ο Μπάμπης αγόρασε ένα ρολόι, ένα καΐκι και ένα αυτοκίνητο από τον Γιώργο στο Ψυχικό.
"""


def make_text(size_mb: float) -> str:
    target = int(size_mb * 1_000_000)
    unit = SAMPLE.encode("utf-8")
    copies = target // len(unit) + 1
    return (SAMPLE * copies).encode("utf-8")[:target].decode("utf-8", "ignore")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--size-mb", type=float, default=1.0)
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args()

    text = make_text(args.size_mb)
    size = len(text.encode("utf-8")) / 1_000_000
    print(
        f"greektext {greektext.__version__}, Python {platform.python_version()}, "
        f"{platform.system()} {platform.machine()}"
    )
    print(f"input: {size:.2f} MB UTF-8, {len(text):,} characters\n")
    print(f"{'function':<28}{'best (s)':>10}{'MB/s':>10}")
    cases = {
        "fold": greektext.fold,
        "to_latin (elot743)": greektext.to_latin,
        "to_latin (simple)": lambda s: greektext.to_latin(s, scheme="simple"),
        "strip_accents": greektext.strip_accents,
        "upper": greektext.upper,
        "slugify": greektext.slugify,
        "phonetic_key": greektext.phonetic_key,
    }
    for name, func in cases.items():
        best = min(timeit.repeat(lambda f=func: f(text), number=1, repeat=args.repeat))
        print(f"{name:<28}{best:>10.3f}{size / best:>10.1f}")


if __name__ == "__main__":
    main()
