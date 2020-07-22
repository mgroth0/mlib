# noinspection PyDefaultArgument
from dataclasses import dataclass
import inspect
import os
import traceback

from mlib.boot.mlog import err
from mlib.boot.stream import listmap
from mlib.file import File
from mlib.str import StringExtension, stre
def interact(loc=vars()):
    import code
    code.interact(local=loc)

def mn(o): return inspect.getmodule(o).__name__

def current_fun():
    return caller_fun(1)

def caller_fun(steps_back=1):
    curframe = inspect.currentframe()
    return inspect.getouterframes(curframe, 2)[1 + steps_back][3]

def caller_lines():
    # inner_fun = caller_fun(1)
    # outer_fun = caller_fun(2)
    outer_file = caller_file(2)
    start = official_caller_line(2)
    end = start + 1
    lines = listmap(
        lambda l: l.strip(),
        File(outer_file).readlines()
    )
    while True:
        if end - start > 40: err('really???')
        e = '\n'.join(lines[start - 1:end - 1]) + '\n'  # MUST END WITH NEWLINE IN EVAL OR SINGLE MODE
        try:
            compile(
                e,
                '<string>',
                'exec'
            )
            break
        except SyntaxError:
            end += 1
    return list(range(start, end))

def official_caller_line(steps_back=1):
    stack = traceback.extract_stack()
    return stack[-2 - steps_back][1]

def caller_file(steps_back=1):
    stack = traceback.extract_stack()
    mod_file = os.path.abspath(stack[-2 - steps_back][0])  # .split('.')[0]
    mod_file = File(mod_file)
    return mod_file



def all_superclasses(clazz):
    li = []
    for b in clazz.__bases__:
        li.extend([b] + all_superclasses(b))
    return li

def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)])

class PythonLine(StringExtension):
    def __init__(self, s):
        super().__init__(s)
        assert '\n' not in self
        self.iscomment = self.strip().startswith('#')
        self.startsdoubledocstr = self.strip().startswith('"')
        self.startssingledocstr = self.strip().startswith("'")
        self.startsdocstr = self.startsdoubledocstr or self.startssingledocstr
