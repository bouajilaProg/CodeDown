---
title: "Convert"
---

Convert a Markdown file to PDF:

```bash
code-down input.md
```

Write to a specific output file:

```bash
code-down input.md out.pdf
# or
code-down input.md -o out.pdf
```

Write into a directory (it will create `out/input.pdf`):

```bash
code-down input.md out/
```

Pick a theme for this run:

```bash
code-down input.md -s light
```

You can also supply a filename without its extension: `code-down input` resolves
`input.md`. An existing file named `input` takes precedence. Supported extensions
are `.md` and `.markdown`; extensionless files are accepted when they exist.
Quote paths containing spaces: `code-down "my notes.md"`.

The explicit form, `code-down convert input.md`, supports the same options.

Layout and metadata:

```bash
code-down notes.md -s print --page-size Letter --margin 15mm \
  --font "DejaVu Sans" --code-font "DejaVu Sans Mono" \
  --page-numbers --header "Team notes" --footer "Internal" \
  --toc --title "Project guide" --author "Your name"
```

Page sizes: A4 (default), A5, Letter, Legal. Margins accept mm, cm, in, pt, or px.
Code wraps by default; use `--no-wrap-code` to preserve line lengths. Fonts must
be installed locally. Long code blocks and tables can span pages, and table
headers repeat. Local images resolve relative to the Markdown file, regardless
of the working directory. The `print` theme uses a white background.

All layout options also apply in watch mode. Title defaults to the input stem;
headers, footers, page numbers, author, and table of contents are opt-in.
