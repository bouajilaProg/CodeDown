# Development

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Or use `just setup uv`, `just setup venv`, or `just setup conda`.
Runtime dependencies live in `pyproject.toml`; `requirements.txt` installs that
project rather than a snapshot of unrelated machine packages.

## Run and test

```bash
code-down --help
code-down examples/example.md out/
python -m pytest -q
python -m build
```

Tests cover filename routing, Bash/Zsh/Fish completion requests, configuration
precedence and validation, real PDF rendering, editor replacement saves, local
resource changes, atomic output, update checksums and recovery backups, and
wheel theme assets. Update tests mock the network and use temporary binaries;
they never update the installed executable.

Linux needs Pango and HarfBuzz system libraries and installed fonts for rendering.
CI installs those libraries and runs the tests on Python 3.9, 3.12, and 3.14.
Release publication depends on those checks. Standalone Linux release assets are
named `code-down-linux-x86_64` and include a `.sha256` checksum file.

## Documentation

```bash
npm --prefix docs install
npm --prefix docs run start
npm --prefix docs run build
```
