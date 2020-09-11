from abc import abstractmethod, ABC
import atexit
from dataclasses import dataclass
from functools import wraps
import inspect
import logging
from types import SimpleNamespace
from typing import Any, Optional, Union

import wolframclient
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr
from wolframclient.language.expression import WLFunction, WLInputExpression
from wolframclient.serializers import WLSerializable

from mlib.boot.lang import ismac, isinstsafe
from mlib.boot.mlog import err
from mlib.boot.stream import listmap, arr, enum, itr
from mlib.file import File
from mlib.obj import SimpleObject
from mlib.term import log_invokation
from mlib.wolf.wolf_lang import CloudObjects, CloudObject, DirectoryQ, FileExistsQ, Rule, If, Import, CloudExport, CloudDeploy, ImportString

class PERMISSIONS:
    PRIVATE = 'Private'
    PUBLIC = 'Public'
Permissions = PERMISSIONS()

class WOLFRAM:
    MADE = False
    def __init__(self):
        # err('dont use this for now')
        if self.MADE:
            raise Exception('just use one wl kernel')
        self.MADE = True

        # not working, need to debug
        atexit.register(self.terminate)

        self.session = None

    @log_invokation(timer=True)
    def _start_session(self, kwargs):
        self.session = WolframLanguageSession(
            kernel_loglevel=logging.DEBUG,
            # kernel_loglevel=logging.FATAL,
            **kwargs,
        )
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def terminate(self):
        if self.session is not None:
            self.session.terminate()
    @log_invokation(first_only=True, with_args=True)
    def eval(self, s):
        if self.session is None:
            kwargs = {} if ismac() else dict(kernel='/home/matt/WOLFRAM/Executables/WolframKernel')
            self._start_session(kwargs)
        ev = self.session.evaluate_wrap_future(wl.UsingFrontEnd(s))
        ev = ev.result()
        if ev.messages is not None:
            for m in ev.messages:
                err(m)
        return ev.result

    def __getattr__(self, name):
        return weval(name)
WOLFRAM = WOLFRAM()
def weval(arg): return WOLFRAM.eval(arg)



class _WCFile(SimpleObject):
    def __init__(self, file):
        self.file = file
        self.abspath = file.abspath
    def str(self): return f'WC[{self.abspath}]'

    @property
    def files(self):
        return arr(listmap(
            lambda wcf: File(wcf),
            weval(CloudObjects(self.file.abspath))
        ))

    def delete(self):
        if self.isdir:
            return weval(wl.DeleteDirectory(CloudObject(self.file.abspath), Rule(wl.DeleteContents, True)))
        else:
            return weval(wl.DeleteFile(CloudObject(self.file.abspath)))
    @property
    def isdir(self):
        return weval(DirectoryQ(CloudObject(self.file.abspath)))
    @property
    def exists(self):
        return weval(FileExistsQ(CloudObject(self.file.abspath)))
    @log_invokation(timer=True, with_instance=True, single_stack=True)
    def push(self, permissions=PERMISSIONS.PRIVATE):
        if self.file.isdir:
            if weval(wl.DirectoryQ(CloudObject(self.file.abspath))):
                weval(wl.DeleteDirectory(CloudObject(self.file.abspath), Rule(wl.DeleteContents, True)))
            return weval(wl.CopyDirectory(
                self.file.abspath,
                CloudObject(self.file.abspath, Rule(wl.Permissions, permissions))
            ))
        else:
            if weval(wl.FileExistsQ(wl.CloudObject(self.file.abspath))):
                weval(wl.DeleteFile(wl.CloudObject(self.file.abspath)))
            return weval(wl.CopyFile(
                self.file.abspath,
                wl.CloudObject(self.file.abspath, wl.Rule(wl.Permissions, permissions))
            ))
    def push_public(self):
        return self.push(permissions=PERMISSIONS.PUBLIC)
    @log_invokation(timer=True, single_stack=True, with_instance=True)
    def pull(self):
        assert weval(wl.FileExistsQ(wl.CloudObject(self.file.abspath)))
        self.file.deleteIfExists()
        self.file.mkparents()
        if self.file.isdir:
            return weval(wl.CopyDirectory(
                CloudObject(self.file.abspath),
                self.file.abspath
            ))
        else:
            return weval(wl.CopyFile(
                wl.CloudObject(self.file.abspath),
                self.file.abspath
            ))




def wlblock(*exprs, returnLast=True):
    return wlexpr(f'{"; ".join(listmap(inputForm, exprs))}{"" if returnLast else ";"}')

def wlset(symbol: str, wlstuff):
    return wlexprc(f'{symbol}={inputForm(wlstuff)}'),



class WolframService:
    def __init__(self):
        self.__dict__['_'] = SimpleNamespace()
        self._.exprs = []
        self._.pending_if_condition = None
        self._.pending_if_branch = None
        self._.pending_else_branch = None

        def get_wrapped(fun):
            @wraps(fun[1])
            def wrapped(*args, **kwargs):
                # args = list(args)
                # args.pop(0) #remove self
                r = fun[1](*args, **kwargs)
                self._.exprs.append(r)
            return wrapped

        methods = inspect.getmembers(mwl, predicate=inspect.isfunction)
        for i, mwl_method in enum(methods):
            self.__dict__[mwl_method[0]] = get_wrapped(mwl_method)

    def build_expressions(self):
        if self._.pending_if_condition is not None:
            self._build_if()
        return self._.exprs
    def __getattr__(self, item):
        return APISymbol(item, service=self)
    def __setattr__(self, key, value):
        self._.exprs.append(
            wlset(
                key,
                value
            )
        )
    def _build_if(self):
        if self._.pending_else_branch is None:
            expr = If(
                self._.pending_if_condition,
                self._.pending_if_branch
            )
        else:
            expr = If(
                self._.pending_if_condition,
                self._.pending_if_branch,
                self._.pending_else_branch
            )
        self._.exprs.append(expr)
        self._.pending_if_condition = None
        self._.pending_if_branch = None
        self._.pending_else_branch = None
    def __iadd__(self, wlstuff):
        self._.exprs.append(wlstuff)
    def if_(self, fun):
        blk = WolframService()
        self._.pending_if_condition = wlformc(inspect.signature(fun).parameters['_condition'].default)
        r = fun(blk)
        self._.pending_if_branch = wlform(wlblock(*blk.build_expressions(), r))
    def else_(self, fun):
        blk = WolframService()
        r = fun(blk)
        self._.pending_else_branch = wlform(wlblock(*blk.build_expressions(), r))
        self._build_if()


class WL_API(ABC, WLSerializable):
    @abstractmethod
    def to_wl(self): pass
    def __getitem__(self, item):
        if isinstsafe(item, WL_API):
            item = item.to_wl()
        if isinstsafe(self, APISymbol) or isinstsafe(self, APIPart):
            self: Union[APISymbol, APIPart]
            return APIPart(self.to_wl(), item, self.service)
        else:
            return APIPart(self.to_wl(), item)
    def __setitem__(self, key, value):
        assert self.service is not None
        self.service: WolframService
        self.service._.exprs.append(wlsetpart(self[key], value))

    def __eq__(self, other):
        return APIEquals(self, other)

def wlsetpart(part, wlstuff):
    return wlexprc(f'{inputForm(part)}={inputForm(wlstuff)}'),

def wlform(wexpr):
    return wlexpr(inputForm(wexpr))

def wlformc(wexpr):
    return wlexprc(inputForm(wexpr))

# noinspection PyUnresolvedReferences
def inputForm(wexpr):
    # if isinstsafe(wexpr, WL_API):
    #     wexpr = wexpr.to_wl()
    from mlib.str import utf_decode
    return utf_decode(wolframclient.serializers.export(wexpr))

@dataclass
class APIEquals(WL_API):
    slf: WLFunction
    other: WLFunction
    def to_wl(self):
        return wl.SameQ(self.slf, self.other)

        # DOESN'T EVALUATE SOMETIMES!
        # return wl.Equal(self.slf, self.other)

    def __eq__(self, other):
        return super().__eq__(other)  # needed

@dataclass
class APISymbol(WL_API):
    name: str
    service: Optional[WolframService] = None

    def __eq__(self, other):
        return super().__eq__(other)  # needed

    def to_wl(self):
        # return wl.Symbol(self.name)
        return wlexprc(self.name)

@dataclass
class APIRule(WL_API):
    # just to make things prettier
    key: Any
    value: Any
    def to_wl(self):
        return wlexprc(f'{inputForm(self.key)}->{inputForm(self.value)}')
        # wl.Part(self.root, self.idx)
    def __eq__(self, other):
        return super().__eq__(other)  # needed

@dataclass
class APIPart(WL_API):
    root: WLFunction
    idx: Any
    service: Optional[WolframService] = None
    def to_wl(self):
        return wlexprc(f'{inputForm(self.root)}[[{inputForm(self.idx)}]]')
        # wl.Part(self.root, self.idx)
    def __eq__(self, other):
        return super().__eq__(other)  # needed


def wlapply(newhead, wexpr):
    return wlexprc(f'{newhead}@@{inputForm(wexpr)}')

def FormatWLInput(ss):
    f_s = ''

    OPEN_Ps = []
    OPEN_Cs = []
    OPEN_Bs = []
    OPENS = ['(', '{', '[']
    CLOSES = [')', '}', ']']

    in_str = False

    fragments = []

    for ii, cc in enum(ss):
        if in_str:
            in_str = cc != '"'
        else:
            in_str = cc == '"'
            if cc == '(':
                OPEN_Ps.append(ii)
            elif cc == '{':
                OPEN_Cs.append(ii)
            elif cc == '[':
                OPEN_Bs.append(ii)
            elif cc == ',':
                pass
            elif cc == ')':
                fragments.append((OPEN_Ps.pop(), ii))
            elif cc == '}':
                fragments.append((OPEN_Cs.pop(), ii))
            elif cc == ']':
                fragments.append((OPEN_Bs.pop(), ii))
            elif cc == ';':
                pass

    for ii, f in enum(fragments):
        fragments[ii] = list(f) + [f[1] - f[0]]

    frag_for_i = []
    for ii in itr(ss):
        added = False
        for f in fragments:
            if f[0] == ii or f[1] == ii:
                frag_for_i.append(f)
                added = True
                break
        if not added:
            frag_for_i.append(None)

    in_str = False
    opening = False
    closed = False

    THRESHOLD = 10

    for ii, cc in enum(ss):
        newline_after = False
        newline_before = False
        frag = None
        if in_str:
            in_str = cc != '"'
        else:
            in_str = cc == '"'
            if cc in OPENS:
                opening = True
            if cc in [',', ';']:
                newline_after = True
                frag = (0, 0, 100)

        if opening and cc not in OPENS:
            newline_before = True
            opening = False
            frag = frag_for_i[ii - 1]

        if closed and cc not in CLOSES:
            closed = False

        if not closed and cc in CLOSES:
            newline_before = True
            frag = frag_for_i[ii]
            closed = True

        if newline_before and frag[2] >= THRESHOLD:
            f_s += '\n'
        f_s += cc
        if newline_after and frag[2] >= THRESHOLD:
            f_s += '\n'

    return f_s

# the parentheses are still there. This failed...
class WLInputExpressionClean(WLInputExpression):
    """ Same as base but without parentheses version """

    def __repr__(self):
        return "%s" % self.input

    def __str__(self):
        return "%s" % self.input
wlexprc = WLInputExpressionClean




class mwl:
    """Every single method in here is added to WolframService in a wrapped form"""
    @staticmethod
    def abort(): return wl.Abort()
    @staticmethod
    def parse_json(o): return ImportString(o, "RawJSON")
    @staticmethod
    def load_json(o): return Import(o, "RawJSON")
    @staticmethod
    def to_json(o): return wl.ExportString(o, "RawJSON")
    @staticmethod
    def save_json(co, o, permissions=PERMISSIONS.PRIVATE):
        return CloudExport(o, 'RawJSON', co, Rule(wl.Permissions, permissions))
    @staticmethod
    def abort(): return wl.Abort()
    @staticmethod
    def cloud_deploy(expr, file, permissions=PERMISSIONS.PRIVATE):
        return CloudDeploy(
            wlexpr(expr),
            CloudObject(File(file).abspath, Rule(wl.Permissions, permissions))
        )


class MWL:
    """wrapper for mwl that evaluates each function on the spot"""
    def __init__(self):
        def get_wrapped(fun):
            @wraps(fun[1])
            def wrapped(*args, **kwargs):
                # args = list(args)
                # args.pop(0) #remove self
                r = fun[1](*args, **kwargs)
                return weval(r)
            return wrapped
        methods = inspect.getmembers(mwl, predicate=inspect.isfunction)
        for i, mwl_method in enum(methods):
            self.__dict__[mwl_method[0]] = get_wrapped(mwl_method)
MWL = MWL()
