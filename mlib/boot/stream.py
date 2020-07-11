from collections import Iterable

import numpy as np

from mlib.boot.bootutil import isnumber, will_break_numpy, isinstsafe, cn, isstr
from mlib.boot.mlog import Muffle



def arr(v=(), dtype=None, ndims=None):
    if ndims is None and (
            isinstsafe(v, np.ndarray) or
            cn(v) == 'ImagingCore' or
            (
                    len(v) > 0 and isinstance(v[0], Iterable) and
                    not isstr(v[0]) and
                    not (hasattr(v[0], '__npitr__') and v[0].__npitr__ is False)
            )
    ):
        return mparray(v, dtype=dtype)
    if not isinstance(v, Iterable):
        v = [v]
    if len(v) > 0 and not isnumber(v[0]):
        if ndims is None: ndims = 1
        if dtype is None:
            dtype = {
                str: object
            }.get(v[0].__class__, object)
        shape = []
        slices = []
        stopper = None
        for d in range(ndims):
            if d > 0:
                stopper = [stopper]
            ref = v
            slices += [None]
            for dd in range(d):
                ref = ref[0]
            shape += [len(ref)]
        v.append(stopper)
        shape[0] = shape[0] + 1
        ar = np.ndarray(shape=tuple(shape), dtype=dtype)
        from mlib.file import File
        try:
            with Muffle(*listfilt(will_break_numpy, v)):
                ar[slice(*slices)] = v
        except File.NoLoadSupportException:
            pass
        ar = mparray(ar, dtype=dtype)
        v.pop()
        ar = ar[:-1]
        assert len(v) == len(ar)
        return ar
    else:
        return mparray(v, dtype=dtype)


def listmap(fun, ll): return list(map(fun, ll))
flatn = lambda l: arr([item for sublist in l for item in sublist])
def append(l, v): return arr(np.append(l, v))
def arrayfun(lamb, l): return arr(listmap(lamb, l))


class mparray(np.ndarray):
    class _ArrayOf:
        def __init__(self, this_arr):
            self.arr = this_arr
        def __getattr__(self, name):
            return arrayfun(
                lambda x: eval(f'x.{name}'),
                self.arr
            )
    @property
    def arrayof(self):
        return self._ArrayOf(self)
    flatn = flatn
    __iadd__ = append
    def __new__(cls, input_array, dtype=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        if dtype is not None:
            obj = np.asarray(input_array, dtype=dtype).view(cls)
        else:
            obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        # Finally, we must return the newly created object:
        return obj

    # noinspection PyMethodMayBeStatic
    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return

    def filtered(self, *tests): return arr(filtered(self, *tests))
    def first(self, *tests): return filtered(self, *tests)[0]
    def map(self, fun): return arr(listmap(fun, self))
    def join(self, s): return s.join(self.tolist())
    def filt_includes(self, s): return self.filtered(
        lambda mine: s in mine,
    )
    def sorted(self, key=None):
        if key is None:
            key = lambda e: e
        return arr(
            sorted(
                self.tolist(),
                key=key
            )
        )



def filtered(lis, *tests):
    r = []
    for item in lis:
        add = True
        for test in tests:
            if not test(item): add = False
        if add: r += [item]
    return r
def listfilt(fun, ll): return list(filter(fun, ll))
def arrfilt(fun, ll): return arr(listfilt(fun, ll))
def strs(ll): return listmap(str, ll)
def arrmap(fun, ll): return arr(listmap(fun, ll))
def listitems(d): return list(d.items())
def ziplist(*args): return list(zip(*args))
# dont know if this works or is useful. idea from fn.py
class __:
    def __getattr__(self, item):
        return lambda x: x.__getattribute__(item)
__ = __()
