---
title: "Update"
---

Update codeDown from the CLI:

```bash
code-down update
```

Check the installed version:

```bash
code-down --version
```

Pip installations update through the current Python interpreter. Standalone
updates select an exact operating-system and architecture match, such as
`code-down-linux-x86_64`. A release must provide a GitHub SHA-256 asset digest or
a matching `.sha256` file. The download is verified before replacing the binary.
Missing assets, download failures, and checksum mismatches leave it unchanged.

A successful standalone update stores the previous executable beside the current
one as `<executable>.backup`. To recover on Linux, stop codeDown and move that
backup back to the original executable path. Replacement is atomic on the same
filesystem. The destination directory must be writable.

Older releases with only an unlabelled `code-down` asset cannot be selected by the
new updater. Install an appropriate binary manually or use pip. The release
workflow currently builds Linux x86_64; other platforms can use pip.
