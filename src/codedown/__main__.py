import sys
from pathlib import Path

from codedown.cli import app


_SUBCOMMANDS = {"convert", "config", "themes", "update"}
_CONVERT_LEADING_OPTIONS = {"-w", "--watch", "-s", "--style", "-o", "--output"}


def _rewrite_argv_for_implicit_convert(argv: list[str]) -> list[str]:
    if len(argv) < 2:
        return argv

    first = argv[1]

    # Let click/typer handle help/version and explicit subcommands.
    if first in {"-h", "--help", "--version"}:
        return argv
    if first in _SUBCOMMANDS:
        return argv

    # Support: code-down -w file.md  (and -s/-o before the file)
    if first in _CONVERT_LEADING_OPTIONS:
        return [argv[0], "convert", *argv[1:]]

    # Support: code-down file.md
    p = Path(first)
    if p.exists() or first.lower().endswith(".md"):
        return [argv[0], "convert", *argv[1:]]

    return argv


def main():
    sys.argv = _rewrite_argv_for_implicit_convert(sys.argv)
    app()


if __name__ == "__main__":
    main()
