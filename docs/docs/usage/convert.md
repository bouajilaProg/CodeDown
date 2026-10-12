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

## Browser preview

```bash
code-down preview notes.md -s nord
# Or use the filename shortcut:
code-down notes.md --preview
# Choose a port and open the URL yourself:
code-down preview notes.md --no-open --port 8080
```

The local workspace renders Markdown as you type and includes a **Copy code**
button for every code block and a **Copy Markdown** toolbar button. Choose
**Side by side**, **Stacked**, **Preview only**, or **Editor only**. Drag the
split divider, or focus it and use the arrow keys. Double-click the divider or
use **Reset split** to restore equal panes. Split size and view are remembered
in your browser.

Edits in the workspace stay in the browser and do not modify your Markdown
file. Copy Markdown to keep those edits. Changes saved from an external editor
appear automatically unless you have browser edits; **Reload file** replaces
browser edits with the file contents. Stop the server with Ctrl+C.

Preview honors theme and rendering defaults from configuration. With
`--preview`, the conversion layout flags also apply; PDF output paths and
`--watch` cannot be combined with preview. Code-copy controls are browser-only
and do not appear in PDF output.
