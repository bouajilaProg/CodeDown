# codeDown

[![PyPI version](https://img.shields.io/pypi/v/code-down.svg?color=blue)](https://pypi.org/project/code-down/)
[![Python versions](https://img.shields.io/pypi/pyversions/code-down.svg)](https://pypi.org/project/code-down/)
[![License: MIT](https://img.shields.io/github/license/bouajilaProg/CodeDown.svg)](https://github.com/bouajilaProg/CodeDown/blob/main/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/bouajilaProg/CodeDown/release.yml)](https://github.com/bouajilaProg/CodeDown/actions)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://bouajilaprog.github.io/CodeDown/)

**codeDown** is a simple yet powerful **CLI tool** that converts Markdown (`.md`) files into **beautiful themed PDFs** — complete with **syntax-highlighted code blocks**.

Built for developers who love clean documentation, readable code snippets, and automated workflows.

---

## Features

*  **Direct filenames** – `code-down notes.md` or `code-down notes`
*  **Shell Autocomplete** – run `code-down --install-completion` from Bash, Zsh, or Fish
*  **Syntax Highlighting** for code blocks
*  **Selectable Themes** – interactive picker or CLI flag (`light`, `dark`, `print`, `dracula`, `nord`, `solarized`, `github`, `gruvbox`)
*  **PDF Layout** – print theme, page sizes, fonts, contents, headers, and metadata
*  **Browser Preview** – live Markdown editing, code-copy buttons, and resizable split views
*  **Watch Mode** – auto-regenerate PDF on file save
*  **Self-Update** – update from the CLI (`code-down update`)
*  **Configurable** – set a default theme via `code-down config set-theme`
*  **Fast & Lightweight** – converts Markdown to PDF in seconds

---

## Installation

### Via pip

```bash
pip install code-down
```

### Via binary (Linux)

1. **Download the latest release**
   Visit the [Releases Page](https://github.com/bouajilaProg/CodeDown/releases) and download the Linux x86_64 binary (`code-down-linux-x86_64`).

2. **Make it executable and move to PATH**

   ```bash
   chmod +x code-down-linux-x86_64
   sudo mv code-down-linux-x86_64 /usr/local/bin/code-down
   ```

---

## Usage

Convert a Markdown file into a themed PDF:

```bash
code-down input.md output.pdf -s dark
```

### Watch mode

Automatically rebuild the PDF when the Markdown file changes:

```bash
code-down -w input.md
```

### Browser preview

```bash
code-down preview notes.md -s nord
code-down notes.md --preview
code-down preview notes.md --no-open --port 8080
```

Choose side-by-side, stacked, preview-only, or editor-only views. Drag the
split divider or use its arrow keys; double-click it to reset. Copy individual
code blocks with **Copy code**, or the whole document with **Copy Markdown**.
Use **Download preview** to export a PDF with your current browser edits and
selected theme, including configured PDF layout settings and local images.
Browser edits do not change your source file. External file changes refresh the
preview automatically when there are no browser edits. Use **Reload file** to
replace browser edits with the file. Press Ctrl+C in the terminal to stop.

### Options

| Flag              | Description                             | Default                             |
| ----------------- | --------------------------------------- | ----------------------------------- |
| `-o, --output`    | Output PDF file path                    | Same as input with `.pdf` extension |
| `-s, --style`     | Theme style (`light`, `dark`, `print`, `dracula`, `nord`, `solarized`, `github`, `gruvbox`)      | Config default or `dark`            |
| `--preview`      | Open the browser preview workspace      |                                     |
| `-w, --watch`     | Watch file and rebuild PDF on changes   |                                     |
| `-v, --version`   | Print version and exit                  |                                     |

### Commands

| Command              | Description                                   |
| -------------------- | --------------------------------------------- |
| `code-down preview input.md` | Open the live preview workspace          |
| `code-down themes`   | Pick a theme interactively (sets as default)   |
| `code-down config show` | Show current configuration                 |
| `code-down config set-theme` | Set the default theme (interactive or by name) |
| `code-down update`   | Update codeDown to the latest version          |

### Examples

Quick test file:

```bash
code-down examples/example.md
```

Convert `README.md` to `README.pdf` using the default theme:

```bash
code-down README.md
```

Convert with a dark theme and custom output name:

```bash
code-down README.md -o README_dark.pdf -s dark
```

Watch a file and rebuild on every save:

```bash
code-down -w notes.md -s light
```

Pick a theme interactively:

```bash
code-down themes
```

---

## Notes

* Ensure your Markdown files are UTF-8 encoded for best results.
* Supports syntax highlighting for most major programming languages.
* Works completely offline — no internet connection required (except for `update`).

## Autocomplete and filename shortcuts

```bash
code-down notes                # resolves notes.md
code-down "my notes.md"        # paths with spaces
code-down --install-completion # run from Bash, Zsh, or Fish; restart the shell
```

Completion suggests commands, Markdown files, directories, options, and themes.
Use `code-down --show-completion` to inspect the generated shell script.

Autocomplete also covers preview filenames and options, all eight themes,
page sizes, configuration keys, and matching setting values:

```text
code-down preview notes.md --style <Tab>
code-down notes.md --page-size <Tab>
code-down config set <Tab>
code-down config set wrap_code <Tab>
```

Upgrade to 3.0.1 and refresh completion:

```bash
python -m pip install --upgrade code-down
code-down --install-completion
```

## PDF layout and project defaults

```bash
code-down notes.md -s print --page-size Letter --margin 15mm --page-numbers \
  --toc --header "Project notes" --title "Guide" --author "Your name"
code-down notes.md --no-overwrite
```

Local images resolve relative to the input file. Watch mode handles replacement
saves and local resource changes, and failed renders preserve the previous PDF.
See `code-down convert --help` for fonts, code wrapping, headers, and footers.

A nearest ancestor `codedown.toml` can supply validated project defaults:

```toml
default_theme = "print"
page_size = "A4"
margin = "20mm"
page_numbers = true
```

CLI options override project settings, which override user settings and built-in
defaults. Use `code-down config set margin 15mm` for a user default and
`code-down config show` to inspect settings. Existing PDFs are overwritten by
default; `--no-overwrite` refuses an existing output without prompting.

## Development and checks

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m build
```

Tests include real PDFs, completion requests, watch events, verified updates, and
wheel contents. CI tests Python 3.9, 3.12, and 3.14 before release publication.
Standalone releases include SHA-256 verification and retain a backup on update.
