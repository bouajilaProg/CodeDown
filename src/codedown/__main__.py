import sys

from codedown.cli import app


_SUBCOMMANDS = {"convert", "config", "themes", "update"}
_CONVERT_LEADING_OPTIONS = {
    "-w", "--watch", "-s", "--style", "-o", "--output", "--page-size",
    "--margin", "--font", "--code-font", "--wrap-code", "--no-wrap-code",
    "--page-numbers", "--no-page-numbers", "--header", "--footer", "--toc",
    "--no-toc", "--title", "--author", "--overwrite", "--no-overwrite",
}


def _rewrite_argv_for_implicit_convert(argv: list[str]) -> list[str]:
    if len(argv) < 2:
        return argv

    first = argv[1]

    # Let click/typer handle help/version and explicit subcommands.
    if first in {"-h", "--help", "-v", "--version"}:
        return argv
    if first in _SUBCOMMANDS:
        return argv

    # Support: code-down -w file.md  (and -s/-o before the file)
    if first in _CONVERT_LEADING_OPTIONS:
        return [argv[0], "convert", *argv[1:]]

    # Support: code-down file.md
    if not first.startswith("-"):
        return [argv[0], "convert", *argv[1:]]

    return argv


def main():
    sys.argv = _rewrite_argv_for_implicit_convert(sys.argv)
    app(prog_name="code-down")


if __name__ == "__main__":
    main()
