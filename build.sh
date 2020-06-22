#!/bin/sh
exec "$HOME/miniconda3/bin/python" "setup.py" "sdist" "bdist_wheel"
#"--record" "files2.txt"