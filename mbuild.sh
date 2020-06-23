#!/bin/sh
set -e
oldPWD=$(pwd)
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd ""$SCRIPTPATH
rm -rf *.eeg-info ; rm -rf build ; rm -rf dist ;
#"$HOME"/miniconda3/envs/mlib/bin/pip freeze > reqs_pip.txt

"$HOME"/miniconda3/envs/mlib/bin/python test.py

"$HOME"/miniconda3/bin/conda list -n mlib -e > reqs_conda.txt; sed -i '' '/pypi/d' reqs_conda.txt



# checks git is not dirty
"$HOME"/miniconda3/envs/build/bin/python -m bumpversion patch # minor,major

python metameta.py

git add .bumpversion.cfg
git add setup.py
git add meta.yaml
git commit -m "auto-commit build cfgs"
git push
#"$HOME"/miniconda3/bin/python -m incremental.update mlib --patch


#these are now run inside of conda-build
#"$HOME"/miniconda3/envs/build/bin/python setup.py sdist bdist_wheel
#"$HOME"/miniconda3/envs/build/bin/python -m twine check dist/*

#no longer uploading to pypi because pip package doesnt work since there are conda deps
#"$HOME"/miniconda3/envs/build/bin/python -m twine upload --repository testpypi dist/*


#"--record" "files2.txt"

/Users/matt/miniconda3/envs/build/bin/conda-build .

cd "$oldPWD"
