rm -Rf dist/*
rm -Rf src/fmpy_qi.egg-info
python3 -m build
python3 -m twine upload dist/*