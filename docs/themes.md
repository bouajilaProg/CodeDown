# Themes

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
