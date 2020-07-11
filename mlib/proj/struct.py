from abc import abstractmethod
import atexit
import os
import sys
from time import time

from git import Repo

from mlib.JsonSerializable import obj
from mlib.boot import log
from mlib.boot.bootutil import pwd, all_superclasses, all_subclasses, isstr
from mlib.boot.dicts import SubDictProxy
from mlib.boot.mlog import getNextIncrementalFile
from mlib.boot.mutil import Runner, enum, err, listkeys, listitems
from mlib.file import File, Folder, PermaDict, pwdf
from mlib.proj.build.mbuild import build
from mlib.proj.build.readme import write_README
from mlib.shell import shell
from mlib.term import log_invokation, yellows, cyans
from mlib.wolf import wolf_manager
from mlib.wolf.wolfpy import WOLFRAM

def main_mod_file():
    if hasattr(sys.modules['__main__'], '__file__'):
        return File(os.path.abspath(sys.modules['__main__'].__file__))
class Project(metaclass=Runner):
    # "True" is meaningless here, only existence of attr is checked (fix)
    __super_runner__ = True

    INPUT_FILE = File('_input.txt')

    REQS_FILE = File('reqs.json')
    STATE = PermaDict('_metastate.json')
    # noinspection PyMethodMayBeStatic,PyMethodParameters
    def _default_config():
        proto = {'placeholder1': None}
        alll = {'placeholder2': None}
        return {
            'profiles': {
                'proto'  : proto,
                'default': proto
            },
            'config'  : {
                'all'    : alll,
                'default': alll
            }
        }
    CFG = File('cfg.yml', default=_default_config(), quiet=True)
    DOCS_FOLDER = Folder('docs')
    LOCAL_DOCS_FOLDER = Folder('_docs')
    RESOURCES_FOLDER = DOCS_FOLDER['resources']
    FIGS_FOLDER = RESOURCES_FOLDER['figs']
    DNN_FIGS_FOLDER = Folder('_figs')
    DNN_FIGS_FIGS_FOLDER = DNN_FIGS_FOLDER['figs_dnn']
    GITHUB_LFS_IMAGE_ROOT = os.path.join('https://media.githubusercontent.com/media/mgroth0/', pwdf().name, 'master')
    PYCALL_FILE = RESOURCES_FOLDER['pycallgraph.png']
    PYDEPS_OUTPUT = None
    LOG_FILE = None
    if main_mod_file() is not None:
        PYDEPS_OUTPUT = RESOURCES_FOLDER[
            f'{main_mod_file().name_pre_ext}.svg'
        ]
        EXECUTABLE = main_mod_file().name_pre_ext

    GIT = Repo(pwd())

    mbuild = False
    extra_flags = []
    def registered_flags(self): return [
                                           'readme',
                                           'build'
                                       ] + self.extra_flags + listkeys(
        self.fun_registry()
    )

    instructions = ''
    configuration = ''
    credits = ''

    cfg = None
    def super_run(self):
        cfg = self._get_cfg()
        self.cfg = cfg
        with WOLFRAM:
            if 'build' in cfg.FLAGS and self.mbuild:
                assert len(cfg.FLAGS) == 1
                err('anything that depends on mlib has to push that too')
                build()
                write_README(self)
                self.push()
            elif 'readme' in cfg.FLAGS:
                assert len(cfg.FLAGS) == 1
                write_README(self)
            else:
                # need to have dailyOrFlag
                self.daily(
                    wolf_manager.manage
                )
                self.run(cfg)
    @abstractmethod
    def run(self, cfg): pass

    def push(self):
        if self.GIT.is_dirty():
            log(
                f'A diff between the index and the commit’s tree your HEAD points to: {self.GIT.index.diff(self.GIT.head.commit)}')
            log(
                f'A diff between the index and the commit’s tree your HEAD points to: {self.GIT.index.diff(self.GIT.head.commit)}')
            log(f'A list of untracked files: {self.GIT.untracked_files}')
            inp = input('Ok to add, commit and push? [y/n] >')
            inp = inp in ['y', 'Y']
            if inp:
                self.GIT.index.add('--all')
                inp = "Commit Message: "
                self.GIT.index.commit(inp.strip())
                self.GIT.remotes[0].push()
        else:
            log('repo is not dirty')

    @log_invokation
    def _get_cfg(self):
        assert len(self.registered_flags()) == len(set(self.registered_flags()))
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
            elif a in self.registered_flags():
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
                err(f'invalid -- arguments: {k}, please see {Project.CFG.name} for configuration options')
            if isinstance(cfg[k], bool):
                v = bool(int(v))
            cfg[k] = v

        return obj(cfg)

    def fun_registry(self):
        if 'daily' not in listkeys(self.STATE):
            self.STATE['daily'] = {}
        return SubDictProxy(self.STATE, 'daily')

    def daily(self, fun, *args):
        n = fun.__name__
        if n in self.cfg.FLAGS:
            log(
                yellows(f'running daily function FROM FLAG: {n}')
            )
            fun(*args)
        elif n not in listkeys(self.fun_registry()):
            log(
                yellows(f'running daily function: {n}')
            )
            fun(*args)
            self.fun_registry().update({n: time()})
        elif self.fun_registry()[n] < time() - (3600 * 24):
            log(
                yellows(f'running daily function: {n}')
            )
            fun(*args)
            self.fun_registry().update({n: time()})
        else:
            nex = self.fun_registry()[n] + (3600 * 24)
            log(
                cyans(
                    f'{n} will run next in {nex - time()} seconds'
                )
            )



    QUIET = False
    _already_initialized = False
    def init(self):
        # because I can't find a good python plantUML library
        log('~~MY MODEL~~')
        from mlib.web.web import HTMLObject
        root_class = HTMLObject
        superclasses = all_superclasses(root_class)
        subclasses = all_subclasses(root_class)
        log(f'\troot:{root_class.__name__}')
        for s in superclasses:
            log(f'\t\tsuper :{s.__name__}')
        for s in subclasses:
            log(f'\t\tsub   :{s.__name__}')

        from mlib.web import shadow
        from mlib.proj.stat import enable_py_call_graph, py_deps
        if not self._already_initialized:
            self.daily(
                enable_py_call_graph,
                Project.PYCALL_FILE
            )
            self.daily(
                atexit.register,
                py_deps,
                main_mod_file(),
                Project.PYDEPS_OUTPUT
            )
            atexit.register(shadow.build_docs)
            self._already_initialized = True

    @staticmethod
    def prep_log_file(filename, new=False):
        if filename is None:
            filename = os.path.basename(sys.argv[0]).replace('.py', '')

        import mlib.boot.bootutil as bootutil
        if bootutil.ismac():
            filename = f'_logs/local/{filename}.log'
        else:
            filename = f'_logs/remote/{filename}.log'

        from mlib.file import Folder
        filename = Folder(pwd())[filename]

        if new:
            filename = getNextIncrementalFile(filename)

        if Project.LOG_FILE is None:
            Project.LOG_FILE = File(filename)
        Project.LOG_FILE.deleteIfExists()
        Project.LOG_FILE.write('')
        if not Project.QUIET: log(f'Initialized log file: {File(Project.LOG_FILE).relpath}')


def MITILI_FOLDER():
    import mlib.boot.bootutil as bootutil
    if bootutil.ismac():
        return File(pwd())
    else:
        return File('/home/matt/mitili')



GIT_IGNORE = File('.gitignore')
GIT_DIR = Folder('.git')
@log_invokation()
def push_docs():
    shell('git reset').interact()
    shell('git add docs').interact()
    shell('git commit docs -m "auto-gen docs"').interact()
    shell('git push').interact()
