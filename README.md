# codeDown

[![PyPI version](https://img.shields.io/pypi/v/code-down.svg?color=blue)](https://pypi.org/project/code-down/)
[![Python versions](https://img.shields.io/pypi/pyversions/code-down.svg)](https://pypi.org/project/code-down/)
[![License: MIT](https://img.shields.io/github/license/bouajilaProg/CodeDown.svg)](https://github.com/bouajilaProg/CodeDown/blob/main/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/bouajilaProg/CodeDown/release.yml)](https://github.com/bouajilaProg/CodeDown/actions)

**codeDown** is a simple yet powerful **CLI tool** that converts Markdown (`.md`) files into **beautiful themed PDFs** — complete with **syntax-highlighted code blocks**.

Built for developers who love clean documentation, readable code snippets, and automated workflows.

---

## Features

*  **Syntax Highlighting** for code blocks
*  **Selectable Themes** – interactive picker or CLI flag (`light`, `dark`)
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
   Visit the [Releases Page](https://github.com/bouajilaProg/CodeDown/releases) and download the latest Linux binary.

2. **Make it executable and move to PATH**

   ```bash
   chmod +x code-down
   sudo mv code-down /usr/local/bin/
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

### Options

| Flag              | Description                             | Default                             |
| ----------------- | --------------------------------------- | ----------------------------------- |
| `-o, --output`    | Output PDF file path                    | Same as input with `.pdf` extension |
| `-s, --style`     | Theme style (e.g. `light`, `dark`)      | Config default or `dark`            |
| `-w, --watch`     | Watch file and rebuild PDF on changes   |                                     |
| `-v, --version`   | Print version and exit                  |                                     |

### Commands

| Command              | Description                                   |
| -------------------- | --------------------------------------------- |
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
