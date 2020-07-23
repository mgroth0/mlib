from unittest import main

from mlib.boot import log
from mlib.boot.lang import pwd
from mlib.boot.mlog import err
from mlib.proj.build.metameta import metameta
from mlib.shell import spshell, shell

def build():
    from mlib.proj.struct import Project
    test = main(module='test', exit=False)
    log(test.result)
    if not test.result.wasSuccessful():
        err('failed test')

    assert not Project.GIT.is_dirty()

    reqs_conda, good2go = Project.write_reqs()
    if not good2go: exit(0)

    err('will change version in src code, need to push this after')
    metameta(reqs_conda)

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
    # If you wish to get the exit status of the child you must call the close() method. The exit or signal status of the child will be stored in self.exitstatus or self.signalstatus. If the child exited normally then exitstatus will store the exit return code and signalstatus will be None. If the child was terminated abnormally with a signal then signalstatus will store the signal value and exitstatus will be None:
    sh.close()
    if sh.p.exitstatus is None:
        err(f'error {sh.p.signalstatus}')
    elif sh.p.exitstatus > 0:
        err(f'error code {sh.p.exitstatus}')
    spshell(
        '/Users/matt/miniconda3/envs/build/bin/conda-build purge'
    ).print_and_raise_if_err()
