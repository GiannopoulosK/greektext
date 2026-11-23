"""The ``greektext`` command line interface.

Every core function is a subcommand. With TEXT arguments they are joined with spaces and
processed once; without, stdin is read and processed line by line, so the command streams in
pipes::

    $ greektext upper "Μάιος"
    ΜΑΪΟΣ
    $ cat names.txt | greektext slug
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import TextIO

from . import __version__
from ._accents import fold, strip_accents
from ._case import lower, upper
from ._normalize import normalize
from ._phonetic import phonetic_key
from ._script import greek_ratio
from ._slug import slugify
from ._translit import SCHEMES, to_latin

__all__ = ["main"]

EXIT_OK = 0
EXIT_NOT_GREEK = 1
EXIT_USAGE = 2
EXIT_BROKEN_PIPE = 1

Transform = Callable[[str], str]


def _transform(args: argparse.Namespace) -> Transform:
    """Build the ``str -> str`` function for a (non-detect) subcommand."""
    command: str = args.command
    if command == "normalize":
        return lambda s: normalize(s, final_sigma=args.final_sigma, lookalikes=args.lookalikes)
    if command == "strip":
        return lambda s: strip_accents(s, keep_dialytika=args.dialytika)
    if command == "latin":
        return lambda s: to_latin(s, scheme=args.scheme)
    if command == "slug":
        return lambda s: slugify(s, sep=args.sep, scheme=args.scheme, max_length=args.max_length)
    simple: dict[str, Transform] = {
        "fold": fold,
        "upper": upper,
        "lower": lower,
        "key": phonetic_key,
    }
    return simple[command]


def _ratio(value: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise argparse.ArgumentTypeError(f"must be between 0 and 1, got {value}")
    return number


def _non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError(f"must be >= 0, got {number}")
    return number


def _build_parser() -> argparse.ArgumentParser:
    # --json is accepted both before and after the subcommand.
    json_flag = argparse.ArgumentParser(add_help=False)
    json_flag.add_argument(
        "--json",
        action="store_true",
        default=argparse.SUPPRESS,
        help='print one JSON object per line: {"input": ..., "output": ...}',
    )

    parser = argparse.ArgumentParser(
        prog="greektext",
        description="Compare, search, transliterate and slugify Greek text.",
        epilog="Without TEXT, each subcommand reads stdin line by line.",
        parents=[json_flag],
    )
    parser.add_argument("--version", action="version", version=f"greektext {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text, description=help_text, parents=[json_flag])
        p.add_argument("text", nargs="*", metavar="TEXT", help="text to process (default: stdin)")
        return p

    p = add("normalize", "clean up text for storage (keeps accents and case)")
    p.add_argument("--lookalikes", action="store_true", help="repair Latin/Greek homoglyphs")
    p.add_argument(
        "--no-final-sigma", dest="final_sigma", action="store_false", help="leave σ/ς as they are"
    )

    p = add("strip", "remove tonos and polytonic marks")
    p.add_argument(
        "--no-dialytika", dest="dialytika", action="store_false", help="remove the dialytika too"
    )

    add("fold", "accent- and case-insensitive search key")
    add("upper", "orthographic Greek uppercase")
    add("lower", "lowercase with correct final sigma")

    schemes = sorted(SCHEMES)
    p = add("latin", "transliterate Greek to Latin")
    p.add_argument("--scheme", choices=schemes, default="elot743")

    add("key", "phonetic key for matching Greek, Greeklish and transliterations")

    p = add("slug", "URL / filename slug")
    p.add_argument("--sep", default="-", help="separator (default: -)")
    p.add_argument("--max-length", type=_non_negative_int, default=None, metavar="N")
    p.add_argument("--scheme", choices=schemes, default="elot743")

    p = add("detect", "print 'greek' or 'not-greek'; exit 0 only if all input is Greek")
    p.add_argument(
        "--threshold", type=_ratio, default=0.5, help="minimum Greek ratio, 0 to 1 (default: 0.5)"
    )

    return parser


def _use_utf8(stream: TextIO) -> None:
    """Force UTF-8 so Windows consoles and pipes do not break Greek text."""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8", errors="surrogateescape")


def _utf8_argv(argv: Sequence[str]) -> list[str]:
    """Re-read command-line arguments as UTF-8.

    Under a non-UTF-8 POSIX locale (``LC_ALL=C``) Python decodes argv bytes with the locale
    codec and ``surrogateescape``; encoding them back gives the original bytes. On Windows argv
    is already Unicode.
    """
    if os.name == "nt":  # pragma: no cover
        return list(argv)
    fixed: list[str] = []
    for arg in argv:
        try:
            fixed.append(os.fsencode(arg).decode("utf-8", "surrogateescape"))
        except UnicodeError:  # already proper text that the locale codec cannot encode
            fixed.append(arg)
    return fixed


def _inputs(text: list[str], stdin: TextIO) -> Iterator[str]:
    if text:
        yield " ".join(text)
        return
    for line in stdin:
        yield line.rstrip("\r\n")


def _json_safe(value: object) -> object:
    """Replace undecodable input bytes (kept as surrogates) with U+FFFD, so JSON stays UTF-8.

    Plain output writes those bytes back unchanged; JSON output must be valid UTF-8 instead.
    """
    if not isinstance(value, str):
        return value
    try:
        raw = value.encode("utf-8", "surrogateescape")
    except UnicodeEncodeError:  # a surrogate that did not come from an input byte
        raw = value.encode("utf-8", "replace")
    return raw.decode("utf-8", "replace")


def _run(args: argparse.Namespace, inputs: Iterable[str], out: TextIO, as_json: bool) -> int:
    def emit(record: dict[str, object], plain: str) -> None:
        if as_json:
            safe = {key: _json_safe(value) for key, value in record.items()}
            out.write(json.dumps(safe, ensure_ascii=False) + "\n")
        else:
            out.write(plain + "\n")

    if args.command == "detect":
        total = greek = 0
        for item in inputs:
            ratio = greek_ratio(item)
            verdict = "greek" if ratio >= args.threshold else "not-greek"
            total += 1
            greek += verdict == "greek"
            emit({"input": item, "output": verdict, "ratio": ratio}, verdict)
        # Empty input is not Greek text: `if greektext detect < empty.txt` must not succeed.
        return EXIT_OK if total and greek == total else EXIT_NOT_GREEK

    transform = _transform(args)
    for item in inputs:
        result = transform(item)
        emit({"input": item, "output": result}, result)
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``greektext`` command and return its exit code.

    >>> main(["upper", "Μάιος"])
    ΜΑΪΟΣ
    0
    >>> main(["slug", "Ευάγγελος & Σία Ο.Ε."])
    evangelos-sia-o-e
    0
    """
    parser = _build_parser()
    args = parser.parse_args(_utf8_argv(sys.argv[1:]) if argv is None else argv)
    if args.command is None:
        parser.print_help(sys.stderr)
        return EXIT_USAGE

    _use_utf8(sys.stdin)
    _use_utf8(sys.stdout)
    try:
        status = _run(args, _inputs(args.text, sys.stdin), sys.stdout, getattr(args, "json", False))
        sys.stdout.flush()
    except BrokenPipeError:  # e.g. `greektext slug < big.txt | head`
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return EXIT_BROKEN_PIPE
    return status
