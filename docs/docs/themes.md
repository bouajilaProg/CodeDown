---
title: "Themes"
---

## Create your own theme

Themes live in `src/codedown/assets/themes/`.

Each theme is defined by a TOML file:

```toml
name = "dark"
css_file = "dark.css"
code_theme = "monokai"
version = "1.0.0"
```

- `css_file` is the theme palette (CSS variables)
- `base.css` contains the shared layout/typography styles
- `code_theme` controls Pygments syntax highlighting

Add a new theme by dropping:

- `mytheme.toml`
- `mytheme.css`

in that directory.

## Example

`mytheme.toml`:

```toml
name = "mytheme"
css_file = "mytheme.css"
code_theme = "monokai"
version = "1.0.0"
```

`mytheme.css`:

```css
:root {
  --page-bg: #ffffff;
  --page-fg: #0f172a;
  --accent: #2563eb;
}
```
