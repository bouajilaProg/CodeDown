python -m build
mkdir -p build/python-build
mv dist/*.whl build/python-build/
mv dist/*.tar.gz build/python-build/
rm -rf dist/*.egg-info
rm -rf build/__pycache__
rm -rf src/codedown/__pycache__
rmdir dist
