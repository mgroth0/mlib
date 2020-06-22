#!/bin/sh
set -e
rm -rf *.eeg-info ; echo test ; rm -rf build ; rm -rf dist ;
"$HOME"/miniconda3/bin/python -m bumpversion micro
#"$HOME"/miniconda3/bin/python -m incremental.update mlib --patch
"$HOME"/miniconda3/bin/python setup.py sdist bdist_wheel
"$HOME"/miniconda3/bin/python -m twine check dist/*
"$HOME"/miniconda3/bin/python -m twine upload --repository testpypi dist/*
#"--record" "files2.txt"
