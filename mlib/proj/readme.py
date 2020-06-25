from mlib.boot.mutil import log_invokation
from mlib.file import File
@log_invokation
def write_README():
    File('README.md').write(README())
def README():
    return """

setup.py ???

[![Anaconda-Server Badge](https://anaconda.org/mgroth0/mlib-mgroth0/badges/version.svg)](https://anaconda.org/mgroth0/mlib-mgroth0)

conda install -c mgroth0 mlib-mgroth0

Development
-

Testing
-

./test

generate this: `./main`

Conda-Build
-
I'm using a separate build environment for the conda-build
`/mbuild.sh`



HEP BELOW:
Installation
-

1. `git clone --recurse-submodules https://github.com/mgroth0/hep`

2. install [miniconda](https://docs.conda.io/en/latest/miniconda.html)

3. `conda update conda`

4. `conda create --name hep --file requirements.txt`
-- When updating, use `conda install --file requirements.txt;pip install -r reqs_pip.txt`

5. `conda activate hep`
6. `pip install -r reqs_pip.txt`

Basic Usage
-

- `./hep`

Configuration
-

(todo)

Development
- 

- use `conda list -e > requirements.txt; sed -i '' '/pypi/d' requirements.txt` to store dependencies.
There are also a couple of pip dependencies manually written in reqs_pip.txt, since these cannot be found through conda

Credits
-

- Isaac, Brain Modulation Lab




conda install -c mgroth0 mlib-mgroth0



DNN BELOW:

Installation
-

1. `git clone --recurse-submodules https://github.com/mgroth0/dnn`

2. install [miniconda](https://docs.conda.io/en/latest/miniconda.html)

3. `conda update conda`


4. `conda config --add channels conda-forge` (might not be required)

5. `conda create --name dnn --file requirements.txt`  
-- When updating, use `conda install --file requirements.txt; pip install --upgrade -r reqs_pip.txt`

6. `conda activate dnn`
7. `pip install -r reqs_pip.txt`

NORMAL USAGE
- pip install --upgrade -r reqs_matt.txt
DEV
- pip uninstall -r reqs_matt.txt
- clone https://github.com/mgroth0/mlib
- Use an an IDE like PyCharm to link mlib and develop it in parallel (for resolving definitions)
- In addition, add mlib to PYTHONPATH in scripts. This allows normal command line usage as well

Basic Usage
-

Generate some images, train/test a model, run analyses, and generate plots. Tested on Mac, but not yet on linux/Windows.

- `./dnn -cfg=gen_images --INTERACT=0`
- `./dnn -cfg=test_one --INTERACT=0`

The second command will fail with a Mathematica-related error, but your results will be saved in `_figs`.

Configuration
-

-MODE: (default = FULL) is a string that can contain any combination of the following (example: "CLEAN JUSTRUN")
- CLEAN
- JUSTRUN
- GETANDMAKE
- MAKEREPORT

Edit [cfg.yml]() to save configuration options. Feel free to push these.

If there is anything hardcoded that you'd like to be configurable, please submit an issue.

Development
- 

just use `./build`. This is a powerful but dangerous build script (it deletes old folders as part of the process). Only use it if files are all in the right place and you know what you are doing.

matt's packages (just mlib for now) must be located in the same parent directory, as this will automatically be pushed as well.

(old)
- use `conda list -e > requirements.txt; sed -i '' '/pypi/d' requirements.txt` to store dependencies.
- There are also a couple of pip dependencies manually written in reqs_pip.txt, since these cannot be found through conda

Credits
-

- Darius, Xavier, Pawan
- heuritech, raghakot, joel


 conda uninstall mlib-mgroth0 --force

 in these public readmes or reqs.txt I have to require a specifc mlib version

 have to also consider running and developing other executables here: human_exp_1 and human_analyze


""".strip()