# I think this is run in a weird temp dir during conda-build
echo "inside build.sh in:"
pwd
echo "ls:"
ls
#$PYTHON setup.py install
echo "finished build.sh"