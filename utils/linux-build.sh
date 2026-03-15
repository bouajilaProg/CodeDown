set -e

# Ensure PyInstaller is available in the current Python environment.
if ! python -m pip show pyinstaller >/dev/null 2>&1; then
  python -m pip install -q pyinstaller
fi

python -m PyInstaller \
  --onefile \
  --clean \
  --strip \
  --name code-down \
  --add-data "./src/codedown/assets:assets" \
  src/codedown/__main__.py

mkdir -p build/linux-build
mv dist/code-down build/linux-build/
