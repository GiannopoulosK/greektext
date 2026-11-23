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
- `detect` prints `greek` or `not-greek` for each input and exits 0 only if there is input
  and every input is Greek, so it works in shell conditions. Blank lines print an empty line
  (`null` in JSON) and do not count; input with no text at all exits 1. `--threshold` must be
  between 0 and 1.
- Text that starts with a dash needs `--` before it, as with most commands:
  `greektext upper -- "-άλφα"`.
- Input and output are always UTF-8, whatever the console or locale encoding, so Windows
  consoles and `LC_ALL=C` shells do not break Greek text. A UTF-8 BOM at the start of stdin is
  dropped.

| Exit code | Meaning |
|---|---|
| 0 | success |
| 1 | `detect` found non-Greek input |
| 2 | usage error |
| 130 | interrupted (Ctrl-C) |
| 141 | the reader of the output went away (`greektext slug < big.txt \| head`) |

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
