from mlib.file import File
from mlib.term import log_invokation
@log_invokation
def write_README(proj):
    File('README.md').write(README({
        'Installation' : _sec(
            '[![Anaconda-Server Badge](https://anaconda.org/mgroth0/mlib-mgroth0/badges/version.svg)](https://anaconda.org/mgroth0/mlib-mgroth0)') if proj.mbuild else _sec(
            f'git clone --recurse-submodules https://github.com/mgroth0/{proj.EXECUTABLE}',
            'install [miniconda](https://docs.conda.io/en/latest/miniconda.html)',
            '`conda update conda`',
            f'`conda create --name {proj.EXECUTABLE} --file requirements.txt` (requirements.txt is currently not working, TODO)',
            'might need to separately `conda install -c mgroth0 mlib-mgroth0`'
            '-- When updating, use `conda install --file requirements.txt;`',
            f'`conda activate {proj.EXECUTABLE}`',
            numbered=True
        ),
        'Usage'        : _sec(
            f'./{proj.EXECUTABLE} {proj.registered_flags()}',
            proj.instructions,
        ),
        'Configuration': proj.configuration,
        'Testing'      : 'automatic' if proj.mbuild else 'todo',
        'Development'  : _sec(
            'TODO: have separate development and user modes. Developer mode has PYTHONPATH link to mlib and instructions for resolving and developing in ide in parallel. User mode has mlib as normal dependency. might need to use `conda uninstall mlib-mgroth0 --force`. Also in these public readmes or reqs.txt I have to require a specific mlib version',
            f'./{proj.EXECUTABLE} build'
        ),
        'Credits'      : proj.credits
    }))
def README(d):
    s = ''
    for k, v in d.items():
        s += f'{k}\n-\n{v}\n\n'
    return s.strip()

def README_Section(*content, numbered=False):
    s = ''
    if len(content) == 0:
        pass
    elif len(content) == 1:
        s += content[0]
    else:
        for ss in content:
            s += '1. ' if numbered else '- '
            s += f'{ss}\n'
    return s
_sec = README_Section
