# Command line

The `greektext` command (also `python -m greektext`) exposes each core function as a
subcommand.

```text
greektext normalize [TEXT ...] [--lookalikes] [--no-final-sigma]
greektext strip     [TEXT ...] [--no-dialytika]
greektext fold      [TEXT ...]
greektext upper     [TEXT ...]
greektext lower     [TEXT ...]
greektext latin     [TEXT ...] [--scheme elot743|simple]
greektext key       [TEXT ...]
greektext slug      [TEXT ...] [--sep -] [--max-length N] [--scheme elot743|simple]
greektext detect    [TEXT ...] [--threshold 0.5]
greektext --version
```

- With TEXT arguments, they are joined with spaces and processed once.
- Without, stdin is read **line by line** and output is streamed, so it works on large files:
  `cat names.txt | greektext slug > slugs.txt`.
- `--json` (before or after the subcommand) prints one JSON object per line:
  `{"input": ..., "output": ...}`; `detect` adds `"ratio"`.
- `detect` prints `greek` or `not-greek` for each input and exits 0 if every input is Greek,
  1 otherwise, so it works in shell conditions.
- Input and output are always UTF-8, whatever the console or locale encoding, so Windows
  consoles and `LC_ALL=C` shells do not break Greek text.

| Exit code | Meaning |
|---|---|
| 0 | success |
| 1 | `detect` found non-Greek input |
| 2 | usage error |

```console
$ greektext upper "Μάιος"
ΜΑΪΟΣ
$ greektext slug "Ευάγγελος & Σία Ο.Ε."
evangelos-sia-o-e
$ greektext latin "ΘΕΣΣΑΛΟΝΙΚΗ"
THESSALONIKI
$ printf 'Αθήνα\nA8hna\n' | greektext --json key
{"input": "Αθήνα", "output": "athina"}
{"input": "A8hna", "output": "athina"}
$ if greektext detect "Καλημέρα" > /dev/null; then echo Greek; fi
Greek
```
