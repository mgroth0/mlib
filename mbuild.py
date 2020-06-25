from pexpect import spawn

from metameta import metameta
from mlib.boot.bootutil import pwd, HOME
from mlib.boot.mutil import err
from mlib.file import Folder, File
from mlib.shell import spshell, shell
projectFolder = Folder(File(__file__).parentDir)

# for file in projectFolder.glob('*.eeg-info') + projectFolder.glob('build') + projectFolder.glob('dist'):
#     file.deleteIfExists()


spshell(
    f'{HOME}/miniconda3/envs/mlib/bin/python test.py'
).print_and_raise_if_err()

reqs_conda = spshell(
    f'{HOME}/miniconda3/bin/conda list -n mlib -e'
).readlines_and_raise_if_err()

File('reqs_conda.txt').write('\n'.join(reqs_conda))

reqs_conda = spshell(
    ['sed', '-i', '', '/pypi/d', 'reqs_conda.txt']
).print_and_raise_if_err()

from git import Repo
my_repo = Repo(pwd())
assert not my_repo.is_dirty()

from conda_prune import conda_prune
if not conda_prune(): exit(0)

metameta()

spshell(
    'git add setup.py meta.yaml'
).print_and_raise_if_err()

spshell(
    ['git', 'commit', '-m', "auto-commit build cfgs"]
).print_and_raise_if_err()

spshell(
    'git push'
).print_and_raise_if_err()

sh = shell(
    ['/Users/matt/miniconda3/envs/build/bin/conda-build', pwd()]
)

sh.interact()
if sh.p.exitstatus > 0: err('error')

spshell(
    '/Users/matt/miniconda3/envs/build/bin/conda-build purge'
).print_and_raise_if_err()