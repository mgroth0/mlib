# I think this is run in a weird temp dir during conda-build
echo "inside build.sh in:"
pwd
echo "ls -a:"
ls -a
#"$HOME"/miniconda3/envs/build/bin/python setup.py sdist bdist_wheel
python -m pip install --no-deps --ignore-installed .
#"$HOME"/miniconda3/envs/build/bin/python -m twine check dist/*
#$PYTHON setup.py install
echo "finished build.sh"