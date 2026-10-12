# Changelog

## 3.0.1

- Add a local browser workspace with live Markdown preview and editable content.
- Support side-by-side, stacked, preview-only, and editor-only views, with
  draggable and keyboard-accessible split resizing.
- Copy code blocks or the whole Markdown document from the preview page.
- Download the current preview as a PDF, including browser edits, the selected
  theme, PDF layout settings, and local images.
- Add Dracula, Nord, Solarized Light, GitHub, and Gruvbox themes alongside Dark,
  Light, and Print.
- Extend Bash, Zsh, and Fish autocomplete to preview commands, page sizes,
  configuration keys, and setting values.
- Fix minimum-dependency CI by resolving Typer versions in one installation.

The existing `code-down notes.md` PDF conversion shortcut remains available.
Browser edits stay in the browser; downloading a preview never modifies the
source Markdown file or overwrites an existing PDF on disk.
