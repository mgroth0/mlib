from abc import abstractmethod, ABC
import os
import sys
from time import time

from git import Repo

from mlib.JsonSerializable import obj
from mlib.analyses import ANALYSES, AnalysisMode, clear_cell_cache
from mlib.boot import log, mlog
from mlib.boot.dicts import SubDictProxy, PermaDict
from mlib.boot.lang import listkeys, isstr, ismac, pwd, cn, HOME, islinux
from mlib.boot.mlog import toc_str, err, logy, logc
from mlib.boot.stream import arr, enum, listitems
from mlib.file import File, Folder, pwdf, getNextIncrementalFile
from mlib.inspect import mn
from mlib.km import reloadIdeaFilesFromDisk
from mlib.obj import SuperRunner
from mlib.parallel import run_in_daemon
from mlib.proj.build.conda_prune import conda_prune
from mlib.proj.build.mbuild import build
from mlib.proj.build.readme import write_README
from mlib.shell import shell, spshell
from mlib.str import utf_decode
from mlib.term import log_invokation
from mlib.wolf import wolf_manager
from mlib.wolf.wolfpy import WOLFRAM

def main_mod_file():
    if hasattr(sys.modules['__main__'], '__file__'):
        return File(os.path.abspath(sys.modules['__main__'].__file__))


def py():
    if ismac():
        return '/Users/matt/miniconda3/bin/python3'
    else:
        return '/home/matt/miniconda3/bin/python3'






from packaging import version
def vers(s):
    return version.parse(str(s))


def mexit(code, message):
    log(message)
    exit(code)





REMOTE_CWD = None
if islinux():
    REMOTE_CWD = pwd()

log('Defining Project')

class Project(SuperRunner, ABC):
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
    # LOCAL_DOCS_FOLDER = Folder('_docs')
    RESOURCES_FOLDER = DOCS_FOLDER['resources']
    SHADOW_RESOURCES = Folder('_Shadow_Resources')
    FIGS_FOLDER = RESOURCES_FOLDER['figs']
    DNN_FIGS_FOLDER = Folder('_figs')
    DNN_WEB_FOLDER = Folder('_web')
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

    if File('git').exists:
        GIT = Repo(pwd())

    mbuild = False
    extra_flags = []
    clear_clear_cache_flags = [
        'clear_cell_cache',
        'cell_clear_cache',
        'ccc'
    ]
    def registered_flags(self): return [
                                           'readme',
                                           'build',
                                           'cell',
                                       ] + self.extra_flags + self.clear_clear_cache_flags + listkeys(
        self.fun_registry()
    )

    instructions = ''
    configuration = ''
    credits = ''

    cfg = None
    def super_run(self):
        from mlib.web.html import HTMLObject
        from mlib.web import shadow
        from mlib.proj.stat import enable_py_call_graph, py_deps, class_model_report
        self.prep_log_file(None)
        cfg = self._get_cfg()
        self.cfg = cfg
        if ismac():
            self.daily(
                self.write_reqs
            )
            self.daily(
                enable_py_call_graph,
                Project.PYCALL_FILE
            )
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
            elif any(x in cfg.FLAGS for x in self.clear_clear_cache_flags):
                assert len(cfg.FLAGS) == 1
                clear_cell_cache()
            elif 'cell' in cfg.FLAGS:
                assert len(cfg.FLAGS) == 3
                analysisFlag = cfg.FLAGS[1]
                cellName = cfg.FLAGS[2]
                analysisO = arr(ANALYSES(AnalysisMode.CELL)).first(
                    lambda o: cn(o) == analysisFlag or mn(o).split('.')[-1] == analysisFlag
                )
                cell = getattr(analysisO, cellName)
                if cell.inputs[0] is not None:
                    inputs = cell.load_cached_input(analysisO)
                    cell(*inputs)
                else:
                    cell()
            else:
                if ismac():
                    # need to have dailyOrFlag
                    self.daily(
                        wolf_manager.manage
                    )
                run_in_daemon(pingChecker)
                self.run(cfg)
        self.daily(
            class_model_report, HTMLObject
        )
        if ismac():
            self.daily(
                # atexit.register,
                py_deps,
                main_mod_file(),
                Project.PYDEPS_OUTPUT
            )
        # atexit.register(
        if ismac() and shadow.enabled:  # not doing this on openmind yet because it erases docs_local/results.html which I am using. need to fix this though
            shadow.build_docs()
        # )
        if ismac():
            reloadIdeaFilesFromDisk()

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
        cell = False
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
            elif cell or a in self.registered_flags():
                if a == 'cell':
                    cell = True
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
        return SubDictProxy(self.STATE, 'daily',makeObjs = False)

    def daily(self, fun, *args):
        self._daily(fun, fun.__name__, *args)

    def daily_reminder(self, ss):
        self._daily(lambda: input(ss), ss)

    def _daily(self, fun, key, *args):
        n = key
        if n in self.cfg.FLAGS:
            logy(f'running daily function FROM FLAG: {n}')
            fun(*args)
        elif n not in listkeys(self.fun_registry()):
            logy(f'running daily function: {n}')
            fun(*args)
            self.fun_registry().update({n: time()})
        elif self.fun_registry()[n] < time() - (3600 * 24):
            logy(f'running daily function: {n}')
            fun(*args)
            self.fun_registry().update({n: time()})
        else:
            nex = self.fun_registry()[n] + (3600 * 24)
            logc(f'{n} will run next in {nex - time()} seconds')


    @staticmethod
    def prep_log_file(filename, new=False):
        if filename is None:
            filename = os.path.basename(sys.argv[0]).replace('.py', '')

        if ismac():
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
        mlog.LOG_FILE = Project.LOG_FILE
        if not mlog.QUIET: log(f'Initialized log file: {File(Project.LOG_FILE).relpath}')

    @classmethod
    def write_reqs(cls):
        File('environment.yml').write(shell('conda env export').all_output())
        reqs_conda = spshell(
            f'{HOME}/miniconda3/bin/conda list -n {pwdf().name} -e'
        ).readlines_and_raise_if_err().filtered(
            lambda l: 'pypi' not in l and (not l.strip().startswith("#"))
        )
        File('reqs_conda.txt').write('\n'.join(reqs_conda))
        conda_prune(just_cache=True)
        good2go = conda_prune()
        return reqs_conda, good2go


def MITILI_FOLDER():
    if ismac():
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

log('imported Project module')


def pingChecker():
    f = File('_logs/local/pingchecker.log', w='')
    p = shell('ping www.google.com')
    while True:
        line = p.readline()
        if len(line) == 0:
            log('pingchecker got EOF')
            f.append(f'({toc_str()})got EOF')
            break
        else:
            f.append(f'({toc_str()}){utf_decode(line)}')
