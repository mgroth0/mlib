import collections
import os
from pathlib import Path
import platform
import sys
import typing
enum = enumerate
import numpy as np
def cn(o): return o.__class__.__name__
def strcmp(s1, s2, ignore_case=False):
    if ignore_case:
        return s1.lower() == s2.lower()
    return s1 == s2



def inv_map(d): return {v: k for k, v in d.items()}



def num2str(num):
    return str(num)




def isblank(s):
    return len(s.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')) == 0
def notblank(s): return not isblank(s)
def isblankstr(s): return isstr(s) and isblank(s)



def composed(*decs):
    # https://stackoverflow.com/questions/5409450/can-i-combine-two-decorators-into-a-single-one-in-python
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f

    return deco



def listkeys(d): return list(d.keys())
def listvalues(d): return list(d.values())



def strrep(s, s1, s2):
    return s.replace(s1, s2)
def classname(o):
    return o.__class__.__name__

def simple_classname(o):
    return classname(o).split('.')[-1]
def isa(o, name):
    return classname(o) == name


def isnumber(o):
    return isinstsafe(o, int) or isinstsafe(o, float) or isinstsafe(o, np.long)
def will_break_numpy(o):
    return not isnumber(o) and not isstr(o) and not isbool(o) and not islist(o)


def isinstsafe(o, c):
    from mlib.inspect import all_superclasses
    return isinstance(o, c) or c in all_superclasses(o.__class__)

def isint(v):
    return isinstance(v, int) or isinstance(v, np.int64)
def isdict(v):
    return isinstance(v, dict)
def isdictsafe(v):
    return isinstance(v, collections.Mapping)
def iscls(v):
    return isinstance(v, type)
def isfun(v):
    return callable(v) and not iscls(v)
def isstr(v):
    from mlib.str import StringExtension
    return isinstance(v, str) or isinstance(v, StringExtension)
def istuple(v):
    return isinstance(v, tuple)
def islist(v):
    return isinstance(v, list)
def isbool(v):
    return isinstance(v, bool)
def isitr(v):
    return isinstance(v, collections.Iterable) or isinstance(v, typing.Iterable)  # not sure if I need both





def is_non_str_itr(o):
    return isitr(o) and not isstr(o)



def addpath(p):
    sys.path.append(p)

def ismac():
    return platform.system() == 'Darwin'
def islinux():
    return platform.system() == 'Linux'
def pwd(): return os.getcwd()


HOME = str(Path.home())
