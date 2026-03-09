---
title: "Create a theme"
---

Themes live in `src/codedown/assets/themes/`.

Each theme has:

- a TOML descriptor (metadata + which CSS file to use)
- a CSS file (your palette via CSS variables)

## 1) Create the TOML

Create `mytheme.toml`:

```toml
name = "mytheme"
css_file = "mytheme.css"
code_theme = "monokai"
version = "1.0.0"
```

Field meaning:

- `name`: the theme id you pass to `-s` (for example `-s mytheme`)
- `css_file`: the CSS file next to the TOML
- `code_theme`: Pygments style name for code blocks

## 2) Create the CSS

Create `mytheme.css`:

```css
:root {
  --page-bg: #ffffff;
  --page-fg: #0f172a;
  --accent: #2563eb;
}
```

The shared layout/typography lives in `base.css`. Your theme CSS should focus on variables.

## 3) Use it

```bash
code-down input.md -s mytheme
```
