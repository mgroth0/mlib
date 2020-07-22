from abc import ABC, ABCMeta
from dataclasses import dataclass
from enum import Enum
import inspect
from typing import Optional, Tuple

from mlib.boot.lang import istuple, cn
from mlib.boot.mlog import log
from mlib.boot.stream import listmap, listitems
from mlib.file import pwdf, Folder
from mlib.obj import Decorator
from mlib.str import preview_dict
from mlib.term import log_invokation
from mlib.web.css import PIXEL_CSS
from mlib.web.html import HTML_Pre, HTMLImage

class AnalysisMode(Enum):
    PIPELINE = 1
    CELL = 2

_ANALYSES = []
def ANALYSES(mode: AnalysisMode):
    [__import__(f.pymodname) for f in pwdf()['analyses'] if f.name != '__pycache__']
    ans = listmap(lambda a: a(mode), _ANALYSES)
    for a in ans:
        a.check_shadow()
    return ans


class AnalysisMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        global _ANALYSES
        if len(cls.__abstractmethods__) == 0 and ABC not in bases:
            _ANALYSES += [cls]
        cls._created_shadow = False
        return cls


class Analysis(ABC, metaclass=AnalysisMeta):
    SHOW_SHADOW = False
    def __init__(self, mode: AnalysisMode):
        self.mode = mode
        self.cells = []
        for name, m in listitems(self.__class__.__dict__):
            if iscell(m):
                self.cells += [m]


    def check_shadow(self):
        cls = self.__class__
        from mlib.web.shadow import Shadow
        if not cls._created_shadow:
            Shadow(
                inspect.getmodule(self).__file__,
                show=self.SHOW_SHADOW,
                analysis=self,
                style=PIXEL_CSS
            )
            cls._created_shadow = True


def cell(_func=None, inputs=None):
    def actual_dec(ff):
        return Cell(ff, inputs)
    return actual_dec if _func is None else actual_dec(_func)

CELL_CACHE = Folder('_cache')['cell']


class CellInput(Enum):
    CACHE = 1

@dataclass
class CellShadowOptions:
    ftype = None


class Cell(Decorator):



    def __str__(self):
        if self.__wrapped__:
            return f'<Cell {self.container_name()}.{self.__wrapped__.__name__}>'
        else:
            return 'PROB GETTING __wrapped__'
    def container_name(self):
        if self.ccls:
            return self.ccls.__name__ + self.ccls_q
        else:
            return 'PROB_GETTING_CONTAINER_NAME'
    def __repr__(self):
        return str(self) + f'[{super()}]'
    def __init__(self, _fun, inputs):
        # checked by attribute name in hasattr
        self.ISCELL = True

        self.shadow_options = CellShadowOptions()

        if not istuple(inputs):
            inputs = inputs,
        for inp in inputs:
            if isinstance(inp, Cell) and inp.ccls is None:
                # ccls is only set if accessed from an object, not a module or within class def
                # so this means it is either a mod level fun or defined in the same class
                # best I can do is assume its ccls is the containing module.
                # at least ccls doesn't need to be exact... for now
                inp.ccls = inspect.getmodule(inp)
                inp.ccls_q = '?'
        self.ccls_q = ''
        self.inputs: Tuple[Optional[
            Cell,
            CellInput,
            Tuple[Cell, int]
        ]] = inputs
    def __call__(self, *args, **kwargs):
        analysis = args[0]
        mode = analysis.mode
        if CellInput.CACHE in self.inputs:
            assert len(self.inputs) == 1
            if len(args) == 1:
                inp = ()
            else:
                inp = tuple(args[1:])
            self._input_cache(analysis).save(inp)
        result = self.__wrapped__(*args, **kwargs)
        if mode == AnalysisMode.CELL:
            self._output_cache(analysis).save(result)
            if self.shadow_options.ftype == ShadowFigType.PREVIEW:
                self.shadow_cache(analysis).save(
                    HTML_Pre(preview_dict(
                        result,
                        depth=4
                    ))
                )
            elif self.shadow_options.ftype == ShadowFigType.RAW:
                self.shadow_cache(analysis).save(
                    result
                )
            elif self.shadow_options.ftype == ShadowFigType.IM:
                self.shadow_cache_im(analysis).save(
                    result
                )
                self.shadow_cache(analysis).save(
                    HTMLImage(
                        url=self.shadow_cache_im(analysis).name, fix_rel_to_res=True
                    ),
                )
            else:
                self.shadow_cache(analysis).deleteIfExists()
        return result
    def _input_cache(self, a):
        return CELL_CACHE[cn(a)][self.__wrapped__.__name__]['input.p']
    def _output_cache(self, a):
        return CELL_CACHE[cn(a)][self.__wrapped__.__name__]['output.p']
    def shadow_cache(self, a):
        return CELL_CACHE[cn(a)][self.__wrapped__.__name__]['shadow.p']
    def shadow_cache_im(self, a):
        return CELL_CACHE[cn(a)][self.__wrapped__.__name__][f'{cn(a)}_{self.__wrapped__.__name__}.png']

    def load_cached_input(self, a) -> tuple:
        if self.inputs[0] == CellInput.CACHE:
            assert len(self.inputs) == 1
            input_args = self._input_cache(a).load()
        else:
            input_args = []
            for inp in self.inputs:
                assert inp != CellInput.CACHE
                if istuple(inp):
                    assert inp[0] != CellInput.CACHE
                    iarg = inp[0]._output_cache(a).load()[inp[1]]
                else:
                    iarg = inp._output_cache(a).load()

                input_args += [iarg]
        # if not f:
        #     short_err(f'cached input for {self} does not exist')
        # TODO: except filenotfound error and throw this
        # return tuple()
        return tuple(input_args)

@log_invokation
def clear_cell_cache():
    c = len(CELL_CACHE.files_recursive)
    CELL_CACHE.clear()
    log(f'deleted {c} cell cache files')


class ShadowFigType(Enum):
    NONE = 0
    PREVIEW = 1
    RAW = 2
    IM = 3

# def _shadow_cell(cel, ftype=None):
#     cel.shadow_options.ftype = ftype


def shadow(_func=None, *, ftype=None):
    # assert _func is None
    def actual_dec(cel):
        assert iscell(cel)
        cel.shadow_options.ftype = ftype
        # _shadow_cell(cel, **kwargs)
        # else:
        #     assert iscls(_func)
        #     _shadow_analysis(_func, **kwargs)
        return cel

    return actual_dec

def iscell(o):
    # return isinstance(o, Cell)
    return hasattr(o, 'ISCELL') and o.ISCELL
