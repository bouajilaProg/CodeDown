# codeDown

**codeDown** is a simple yet powerful **CLI tool** that lets you export your Markdown (`.md`) files into **beautiful themed PDFs** — complete with **syntax-highlighted code blocks**.

Built for developers who love clean documentation, readable code snippets, and automated workflows.

---

## 🚀 Features

* 🎨 **Syntax Highlighting** for code blocks 
* ⚡ **Fast & Lightweight** – converts Markdown to PDF in seconds
* 📁 **Command Line Friendly** – perfect for integrating into build scripts or documentation pipelines
* 🧱 **No External Dependencies** – just Python and your Markdown files

---

## Installation (Linux)

1. **Download the latest release**
   Visit the [Releases Page](https://github.com/bouajilaProg/CodeDown/releases) and download the latest binary for Linux (e.g. `code-down`).

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
code-down input.md output.pdf
```

### Example

```bash
code-down README.md README.pdf
```


---

## 💡 Notes

* Ensure your Markdown files are UTF-8 encoded for best results.
* codeDown supports code syntax highlighting for most major languages.
* Works offline — no internet connection required.

