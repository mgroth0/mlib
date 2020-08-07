from abc import abstractmethod, ABC
from dataclasses import dataclass
from time import time
from typing import Callable

from colorama import Fore, Style

from mlib.boot.lang import cn
from mlib.obj import SimpleObject, Decorator

def greens(s): return f'{Fore.GREEN}{s}{Style.RESET_ALL}'
def reds(s): return f'{Fore.RED}{s}{Style.RESET_ALL}'
def lreds(s): return f'{Fore.LIGHTRED_EX}{s}{Style.RESET_ALL}'
def blues(s): return f'{Fore.BLUE}{s}{Style.RESET_ALL}'
def yellows(s): return f'{Fore.YELLOW}{s}{Style.RESET_ALL}'
def magentas(s): return f'{Fore.MAGENTA}{s}{Style.RESET_ALL}'
def cyans(s): return f'{Fore.CYAN}{s}{Style.RESET_ALL}'


class MagicTermLine(ABC):
    ERASE = '\x1b[1A\x1b[2K'
    last_len = 0

    def __init__(self):
        self.DISABLED = False
    @abstractmethod
    def current_line(self): pass
    @abstractmethod
    def ended(self): pass
    def print(self, normally=False):
        from mlib.boot import log
        s = self.current_line()
        if len(s) < self.last_len:
            for _ in range(self.last_len - len(s)):
                s += ' '
        if self.ended() or normally:
            print(s)
        else:
            print(f'{s}\r', end="", flush=True)
        log(s, silent=True)
        self.last_len = len(s)

@dataclass(repr=False)
class MagicTermLineLogger(MagicTermLine, SimpleObject):
    owner: Callable
    line: str = ''
    done: bool = False
    killed: bool = False

    def __post_init__(self):
        self.DISABLED = False
    def str(self): return f'<{cn(self)} of {self.owner.__name__}>'
    def current_line(self):
        return self.line
    def set_current_line(self, line):
        self.line = line
    def ended(self):
        return False
    def kill(self):
        self.done = True
        self.killed = True

class Progress(MagicTermLine):
    PROGRESS_DISABLED = False
    _instances = []
    def __init__(self, goal, verb='doing', pnoun='things'):
        from mlib.boot import log
        self.last = 0
        self.goal = goal
        self._internal_n = 1
        log(f'{verb} $ {pnoun}', f'{goal:,}')
        self._instances += [self]
        self.entered = False
        super().__init__()

        self.DISABLED = self.PROGRESS_DISABLED

    def __enter__(self):
        self.entered = True
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._instances.remove(self)

    # PROG_CHAR = '|'
    PROG_CHAR = greens('▮')
    @staticmethod
    def prog_bar(n, d=100, BAR_LENGTH=50):
        progress = round((n / d) * 100)
        s = '['
        for x in range(BAR_LENGTH):
            if progress >= x * (100 / BAR_LENGTH):
                s += Progress.PROG_CHAR
            else:
                s += ' '
        s += f']'
        return s

    def progress(self):
        return round((self._internal_n / self.goal) * 100)

    def ended(self):
        return self.progress() == 100

    def current_line(self):
        assert self.entered
        progress = round((self._internal_n / self.goal) * 100)
        self.last = progress
        bar = self.prog_bar(self._internal_n, self.goal)
        return f'Progress: {bar} {progress}%'

    # noinspection PyUnusedLocal
    def tick(self, n=None):
        if n is None:
            self.tick(self._internal_n)
            self._internal_n += 1
        else:
            self._internal_n = n
            if not self.DISABLED:
                self.print()

def log_invokation(
        _func=None, *, with_class=False, with_instance=False, with_args=False, with_result=False, stack=False,
        timer=False, single_stack=False, first_only=False, invoke_only=False
):
    assert not (stack and single_stack)
    def actual_dec(ff):
        # cant do @wraps any more with class
        # @wraps(ff)
        class fff(Decorator):
            def __init__(self, _):
                self.my_stacker = None
                if stack:
                    self.my_stacker = MagicTermLineLogger(ff)
                self.first_call = True


            def __call__(self, *args, **kwargs):
                from mlib.boot import log
                ags = '' if not with_args else f'{args=}{kwargs=}'
                inst = '' if not with_instance else f' of {args[0]}'
                cls = '' if not with_class else f'{cn(args[0])}.'
                first_str = '' if not first_only else 'first '
                s = f'{first_str}{cls}.{ff.__name__}({ags}){inst}'
                if single_stack: self.my_stacker = MagicTermLineLogger(ff)
                if not first_only or self.first_call:
                    log(f'Invoking {s}...', ref=1, stacker=self.my_stacker)
                start_time = time()
                result = ff(*args, **kwargs)
                duration = time() - start_time

                r_str = '' if not with_result else f' (result={result=})'

                t = '' if not timer else f' ({duration=:.2f}s)'
                if not invoke_only and (not first_only or self.first_call):
                    log(f'Finished {s}!{r_str}{t}', ref=1, stacker=self.my_stacker)
                if single_stack: self.my_stacker.done = True
                self.first_call = False
                return result
        return fff(ff)

    if _func is None:
        # called with args. return the ACTUAL decoration
        return actual_dec
    else:
        # called with no args (_func magically added as first arg). This IS the decoration
        return actual_dec(_func)
