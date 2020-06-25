from abc import abstractmethod
import os
import sys

from mlib.JsonSerializable import obj
from mlib.boot.bootutil import pwd
from mlib.boot.mutil import Runner, enum, err, listkeys, isstr, listitems, log_invokation
from mlib.file import File, Folder, PermaDict, Config
from mlib.proj.readme import write_README
def main_mod_file():
    if hasattr(sys.modules['__main__'], '__file__'):
        return File(os.path.abspath(sys.modules['__main__'].__file__))
class Project(metaclass=Runner):
    # "True" is meaningless here, only existence of attr is checked (fix)
    __super_runner__ = True

    STATE = PermaDict('_metastate.json')
    _CFG_FILE = File('cfg.yml')
    CFG = Config(_CFG_FILE)
    DOCS_FOLDER = Folder(
        'docs', mker=True
    )
    LOCAL_DOCS_FOLDER = Folder('_docs').mkdir()
    RESOURCES_FOLDER = DOCS_FOLDER['resources']
    FIGS_FOLDER = RESOURCES_FOLDER['figs']
    GITHUB_LFS_IMAGE_ROOT = 'https://media.githubusercontent.com/media/mgroth0/'
    PYCALL_FILE = RESOURCES_FOLDER['pycallgraph.png']
    PYDEPS_OUTPUT = None
    if main_mod_file() is not None:
        PYDEPS_OUTPUT = RESOURCES_FOLDER[
            f'{main_mod_file().name_pre_ext}.svg'
        ]
    def super_run(self):
        cfg = self._get_cfg()
        write_README()
        assert len(cfg.FLAGS) <= 1
        if 'readme' not in cfg.FLAGS:
            self.run(cfg)
    @abstractmethod
    def run(self, cfg): pass

    @log_invokation
    def _get_cfg(self):
        prof = 'default'
        cfg = 'default'
        changes = {}
        flags = []
        for idx, a in enum(sys.argv):
            if idx == 0: continue
            elif a.startswith('--'):
                k, v = tuple(a.replace('--', '').split('='))
                changes[k] = v
            elif a.startswith('-'):
                k, v = tuple(a.replace('-', '').split('='))
                if k == 'prof':
                    prof = v
                elif k == 'cfg':
                    cfg = v
                else:
                    err('arguments with one dash (-) need to be prof= or cfg=')
            elif idx == 1 and len(sys.argv) == 2 and a == 'readme':
                flags += [a]
            else:
                err(f'invalid argument:{a} please see README')

        prof = Project.CFG['profiles'][prof]
        cfg = Project.CFG['configs'][cfg]

        for k in listkeys(prof):
            if k in listkeys(cfg):
                prof_ntrain = prof[k]
                for i, n in enum(cfg[k]):
                    if isstr(n) and n[0] == 'i':
                        cfg[k][i] = prof_ntrain[int(n[1])]

        cfg = {**prof, **cfg, 'FLAGS': flags}

        for k, v in listitems(changes):
            if k not in listkeys(cfg):
                err(f'invalid -- arguments: {k}, please see {Project._CFG_FILE.name} for configuration options')
            if isinstance(cfg[k], bool):
                v = bool(int(v))
            cfg[k] = v

        return obj(cfg)

def MITILI_FOLDER():
    import mlib.boot.bootutil as bootutil
    if bootutil.ismac():
        return File(pwd())
    else:
        return File('/home/matt/mitili')


def pwdf(): return Folder(pwd())
GIT_IGNORE = File('.gitignore')
GIT_DIR = Folder('.git')