"""Allow ``python -m greektext``."""

from greektext._cli import main

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
