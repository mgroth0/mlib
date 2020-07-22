# no point of this. just instantiate under the class def. Would be nice if I could use a decorate, but IDE doesn't understand it whereas it does understand the instantiation underneath
from abc import ABCMeta, abstractmethod, ABC
import functools
import inspect
from types import SimpleNamespace

from mlib.boot.lang import listkeys
from mlib.boot.stream import listitems
def singleton(cls): return cls()




def run(cls): cls().run()

# class Runner(ABCMeta):
#     def __new__(mcs, name, bases, attrs):
#         cls = type.__new__(mcs, name, bases, attrs)
#         if inspect.isabstract(cls):
#             return cls
#         else:
#             cls().super_run()
#             return None

class SuperRunner(ABC):  # metaclass=Runner
    @abstractmethod
    def super_run(self): pass
    @abstractmethod
    def run(self, cfg): pass
    def __init_subclass__(cls, **kwargs):
        if not inspect.isabstract(cls):
            cls().super_run()




# works, but causes intelliJ warnings due to unresolved references
class Attributed:
    def __init__(self, **kwargs):
        for k, v in listitems(kwargs):
            self.__setattr__(k, v)



class SimpleObject:
    def __repr__(self): return self.__str__()
    def __str__(self): return self.str()
    @abstractmethod
    def str(self) -> str: pass

    def apply(self, l):
        l(self)
        return self



def struct():
    return SimpleNamespace()



class Decorator(ABC):
    def __new__(cls, fun, *args, **kwargs):
        o = super().__new__(cls)
        o.__wrapped__ = None  # just so this gets resolved in IDE. Its actually set in update_wrapper.
        o.ccls = None  # just so this gets resolved in IDE. Its actually set in __get__.
        functools.update_wrapper(o, fun)  # TA-DA! #
        return o
    @abstractmethod
    def __call__(self, *args, **kwargs): pass
    def __get__(self, instance, owner):
        from functools import partial
        p = partial(self, instance)
        p.ccls = owner
        for k, v in list(self.__dict__.items()):
            if k not in list(p.__dict__.keys()):
                p.__dict__[k] = v
        for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            setattr(p, method_name, method)
        return p
        # return partial(self.__call__, instance)
