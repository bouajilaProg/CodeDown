# codeDown

**codeDown** is a simple yet powerful **CLI tool** that converts Markdown (`.md`) files into **beautiful themed PDFs** — complete with **syntax-highlighted code blocks**.

Built for developers who love clean documentation, readable code snippets, and automated workflows.

---

## 🚀 Features

*  **Syntax Highlighting** for code blocks
*  **Selectable Themes** – choose a style for your PDF (`light` or `dark`)
*  **Fast & Lightweight** – converts Markdown to PDF in seconds

---

## Installation (Linux)

1. **Download the latest release**
   Visit the [Releases Page](https://github.com/bouajilaProg/CodeDown/releases) and download the latest Linux binary (e.g., `code-down`).

2. **Make it executable**

   ```bash
   chmod +x code-down
   ```

3. **Add it to your PATH**
   Move it somewhere accessible globally, such as `/usr/local/bin`:

   ```bash
   sudo mv code-down /usr/local/bin/
   ```

---

## Usage

Convert a Markdown file into a themed PDF:

```bash
code-down input.md -o output.pdf -s dark
```

### Options

| Flag           | Description                     | Default                             |
| -------------- | ------------------------------- | ----------------------------------- |
| `-o, --output` | Output PDF file path            | Same as input with `.pdf` extension |
| `-s, --style`  | Theme style (`light` or `dark`) | `light`                             |

### Examples

Convert `README.md` to `README.pdf` using the default light theme:

```bash
code-down README.md
```

Convert with a dark theme and custom output name:

```bash
code-down README.md -o README_dark.pdf -s dark
```

---

## 💡 Notes

* Ensure your Markdown files are UTF-8 encoded for best results.
* Supports syntax highlighting for most major programming languages.
* Works completely offline — no internet connection required.

 I can also **add a small diagram or CLI usage snippet** showing how `input → output → style` works, which makes the README even more visually clear. Do you want me to do that?
