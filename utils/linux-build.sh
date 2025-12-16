pyinstaller --onefile -n code-down src/codedown/__main__.py
strip dist/code-down
if [ ! -d build/linux-build ]; then
  mkdir -p build/linux-build
fi
mv dist/code-down build/linux-build
