---
title: "Theme basics"
---

Use a theme for a single run:

```bash
code-down input.md -s dark
```

Pick a theme interactively and store it as your default:

```bash
code-down themes
```

The `print` theme uses a white background and restrained styling for paper output.
Select it with `code-down notes.md --style print`.

Built-in themes: `dark`, `light`, `print`, `dracula`, `nord`, `solarized`
(Solarized Light), `github`, and `gruvbox`. Each includes matching document colors
and syntax highlighting. All are available in PDFs and the browser preview.

```bash
code-down notes.md -s nord
code-down preview notes.md -s dracula
```
