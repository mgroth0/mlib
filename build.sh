#!/bin/sh
set -e
oldPWD=$(pwd)
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH
rm -rf *.eeg-info ; echo test ; rm -rf build ; rm -rf dist ;
"$HOME"/miniconda3/bin/python -m bumpversion patch # minor,major
git add .bumpversion.cfg
git add setup.py
git commit -m "auto-commit build cfgs"
git push
#"$HOME"/miniconda3/bin/python -m incremental.update mlib --patch
"$HOME"/miniconda3/bin/python setup.py sdist bdist_wheel
"$HOME"/miniconda3/bin/python -m twine check dist/*
"$HOME"/miniconda3/bin/python -m twine upload --repository testpypi dist/*
#"--record" "files2.txt"
cd $oldPWD
