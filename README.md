# 🧠 Codedown

**Codedown** is a simple yet powerful **CLI tool** that lets you export your Markdown (`.md`) files into **beautiful themed PDFs** — complete with **syntax-highlighted code blocks**.

Built for developers who love clean documentation, readable code snippets, and automated workflows.

---

## 🚀 Features

* 🎨 **Syntax Highlighting** for code blocks (via Pygments)
* 🧩 **Custom Themes** – apply your own CSS styles for a personalized look
* ⚡ **Fast & Lightweight** – converts Markdown to PDF in seconds
* 📁 **Command Line Friendly** – perfect for integrating into build scripts or documentation pipelines
* 🧱 **No External Dependencies** – just Python and your Markdown files

---

## 📦 Installation

Make sure you have **Python 3.8+** installed.

```bash
git clone https://github.com/bouajilaprog/codedown.git
cd codedown
pip install -r requirements.txt
```

Then make the CLI executable:

```bash
chmod +x main.py
```

Or just run it with Python.

---

## 🧰 Usage

Convert a Markdown file into a themed PDF:

```bash
python main.py input.md output.pdf
```

### Example

```bash
python main.py README.md README.pdf
```
