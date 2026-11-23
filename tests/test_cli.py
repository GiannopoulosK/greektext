"""CLI tests: in-process for coverage, and through subprocess for real stdin/stdout bytes."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys

import pytest

from greektext import __version__, slugify
from greektext._cli import main

# --------------------------------------------------------------------------- in-process


def run(
    argv: list[str],
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    stdin: str = "",
) -> tuple[int, str]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
    code = main(argv)
    return code, capsys.readouterr().out


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["upper", "Μάιος"], "ΜΑΪΟΣ\n"),
        (["lower", "ΟΔΟΣ", "ΠΑΤΡΩΝ"], "οδος πατρων\n"),
        (["fold", "ΑΘΉΝΑ"], "αθηνα\n"),
        (["strip", "προϊόν"], "προϊον\n"),
        (["strip", "--no-dialytika", "προϊόν"], "προιον\n"),
        (["normalize", "  οδοσ  "], "οδος\n"),
        (["normalize", "--no-final-sigma", "οδοσ"], "οδοσ\n"),
        (["normalize", "--lookalikes", "Kαλημέρα"], "Καλημέρα\n"),
        (["latin", "ΘΕΣΣΑΛΟΝΙΚΗ"], "THESSALONIKI\n"),
        (["latin", "--scheme", "simple", "Ψυχικό"], "Psichiko\n"),
        (["key", "Kwnstantinos"], "konstadinos\n"),
        (["slug", "Ευάγγελος & Σία Ο.Ε."], "evangelos-sia-o-e\n"),
        (["slug", "--sep", "_", "--max-length", "9", "Καλημέρα Κόσμε"], "kalimera\n"),
        (["detect", "Καλημέρα"], "greek\n"),
    ],
)
def test_commands(
    argv: list[str],
    expected: str,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code, out = run(argv, capsys, monkeypatch)
    assert code == 0
    assert out == expected


def test_stdin_line_by_line(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    code, out = run(["slug"], capsys, monkeypatch, stdin="Καλημέρα Κόσμε\r\nΧανιά\n\n")
    assert code == 0
    assert out == "kalimera-kosme\nchania\n\n"


def test_json(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    for argv in (["--json", "upper", "Μάιος"], ["upper", "--json", "Μάιος"]):
        code, out = run(argv, capsys, monkeypatch)
        assert code == 0
        assert json.loads(out) == {"input": "Μάιος", "output": "ΜΑΪΟΣ"}
        assert "Μάιος" in out  # not \\u-escaped


def test_detect(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = run(["detect", "Hello", "world"], capsys, monkeypatch)
    assert (code, out) == (1, "not-greek\n")

    code, out = run(["detect", "--threshold", "0.4", "Hello κόσμε"], capsys, monkeypatch)
    assert (code, out) == (0, "greek\n")

    code, out = run(["--json", "detect"], capsys, monkeypatch, stdin="Γεια\nHi\n")
    assert code == 1
    records = [json.loads(line) for line in out.splitlines()]
    assert records == [
        {"input": "Γεια", "output": "greek", "ratio": 1.0},
        {"input": "Hi", "output": "not-greek", "ratio": 0.0},
    ]


def test_detect_empty_input_is_not_greek(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    code, out = run(["detect"], capsys, monkeypatch, stdin="")
    assert (code, out) == (1, "")


def test_text_starting_with_a_dash(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    code, out = run(["upper", "--", "-άλφα"], capsys, monkeypatch)
    assert (code, out) == (0, "-ΑΛΦΑ\n")


def test_no_command_is_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert "usage" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argv",
    [
        ["nope"],
        ["latin", "--scheme", "iso", "α"],
        ["slug", "--max-length", "-1", "α"],
        ["detect", "--threshold", "1.5", "α"],
        ["detect", "--threshold", "-0.1", "α"],
        ["detect", "--threshold", "half", "α"],
    ],
)
def test_bad_arguments_exit_2(argv: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 2


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"greektext {__version__}"


def test_broken_pipe(monkeypatch: pytest.MonkeyPatch, tmp_path: object) -> None:
    class ClosedPipe(io.StringIO):
        def write(self, s: str) -> int:
            raise BrokenPipeError

    dup2_calls: list[tuple[int, int]] = []
    monkeypatch.setattr(sys, "stdin", io.StringIO("α\n"))
    monkeypatch.setattr(sys, "stdout", ClosedPipe())
    monkeypatch.setattr(sys.stdout, "fileno", lambda: 99)
    monkeypatch.setattr(os, "dup2", lambda a, b: dup2_calls.append((a, b)))
    assert main(["upper"]) == 1
    assert dup2_calls == [(dup2_calls[0][0], 99)]


# --------------------------------------------------------------------------- subprocess


def cli(*args: str, stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    # A non-UTF-8 locale: the CLI must still read and write UTF-8 itself.
    env = {
        k: v for k, v in os.environ.items() if not k.startswith(("PYTHONIO", "PYTHONUTF8", "LC_"))
    }
    env.update({"LC_ALL": "C", "PYTHONUTF8": "0"})
    return subprocess.run(
        [sys.executable, "-m", "greektext", *args],
        input=stdin,
        capture_output=True,
        env=env,
        check=False,
    )


def test_subprocess_args() -> None:
    proc = cli("upper", "Μάιος")
    assert proc.returncode == 0
    assert proc.stdout.decode("utf-8").splitlines() == ["ΜΑΪΟΣ"]


def test_subprocess_utf8_stdin() -> None:
    proc = cli("latin", stdin="ΘΕΣΣΑΛΟΝΙΚΗ\nΧανιά\n".encode())
    assert proc.returncode == 0
    assert proc.stdout.decode("utf-8").splitlines() == ["THESSALONIKI", "Chania"]


def test_subprocess_detect_exit_codes() -> None:
    assert cli("detect", "Καλημέρα").returncode == 0
    assert cli("detect", "Hello").returncode == 1
    assert cli("bogus").returncode == 2


def test_subprocess_streams_10000_lines() -> None:
    words = ["Καλημέρα Κόσμε", "Ευάγγελος & Σία Ο.Ε.", "Θεσσαλονίκη", "Μπάμπης", "άυλος"]
    lines = [f"{words[i % len(words)]} {i}" for i in range(10_000)]
    proc = cli("slug", stdin=("\n".join(lines) + "\n").encode("utf-8"))
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.decode("utf-8").splitlines()
    assert len(out) == 10_000
    assert out == [slugify(line) for line in lines]


def test_subprocess_json_with_invalid_utf8() -> None:
    proc = cli("--json", "upper", stdin=b"caf\xe9 \xce\xb1\n")
    record = json.loads(proc.stdout.decode("utf-8"))  # valid UTF-8 and valid JSON
    assert record == {"input": "caf\ufffd α", "output": "CAF\ufffd Α"}
    # Plain output keeps the undecodable byte as it was.
    assert cli("upper", stdin=b"caf\xe9\n").stdout.replace(b"\r\n", b"\n") == b"CAF\xe9\n"


def test_json_safe_with_a_lone_surrogate() -> None:
    from greektext._cli import _json_safe

    assert _json_safe("a\ud800b") == "a?b"
    assert _json_safe(0.5) == 0.5


def test_subprocess_json() -> None:
    proc = cli("--json", "key", stdin="Αθήνα\nA8hna\n".encode())
    records = [json.loads(line) for line in proc.stdout.decode("utf-8").splitlines()]
    assert [r["output"] for r in records] == ["athina", "athina"]


def test_argv_from_sys_argv(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["greektext", "upper", "ρολόι"])
    assert main() == 0
    assert capsys.readouterr().out == "ΡΟΛΟΪ\n"


def test_argv_that_the_locale_cannot_encode(monkeypatch: pytest.MonkeyPatch) -> None:
    from greektext import _cli as cli_module

    def ascii_fsencode(arg: str) -> bytes:
        return arg.encode("ascii")

    monkeypatch.setattr(os, "fsencode", ascii_fsencode)
    assert cli_module._utf8_argv(["Μάιος", "abc"]) == ["Μάιος", "abc"]
