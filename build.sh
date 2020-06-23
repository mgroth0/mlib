# I think this is run in a weird temp dir during conda-build
echo "build.sh: start"
echo "build.sh: pwd:"
pwd
echo "build.sh: ls:"
ls -a
#"$HOME"/miniconda3/envs/build/bin/python setup.py sdist bdist_wheel
#echo "build.sh: conda install"
#conda install --file reqs_conda.txt
echo "build.sh: pip install"
python -m pip install --no-deps --ignore-installed .
#"$HOME"/miniconda3/envs/build/bin/python -m twine check dist/*
#$PYTHON setup.py install
echo "build.sh: finished"