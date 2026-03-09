pyinstaller \
  --onefile \
  --clean \
  --strip \
  --name code-down \
  --add-data "./src/codedown/assets:assets" \
  src/codedown/__main__.py

mkdir -p build/linux-build
mv dist/code-down build/linux-build/
