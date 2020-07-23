from collections import Iterable
from dataclasses import dataclass
import operator
import re

import numpy as np

from mlib.boot.lang import isinstsafe, cn, isstr, isnumber, will_break_numpy, isitr, istuple, islist, is_non_str_itr, isdict, enum

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
            from mlib.boot.mlog import Muffle
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


def flat(l): return arr(l).flatten()

# def append


def make2d(v):
    v = arr(v)
    if len(v.shape) == 0:
        v = arr([v])
    if len(v.shape) == 2:
        return v
    v = arr(v)
    # v.shape = (1,max(v.shape[0],1))
    v.shape = (1, v.shape[0])  # just use .flatten()
    return v

def col(ar):
    return arr(ar).transpose()

def mat():
    a = arr()
    a.shape = (0, 0)
    return a


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

    @property
    def isempty(self):
        return len(self) == 0

    @property
    def isnotempty(self):
        return not self.isempty

    def max_by(self, lamp): return max_by(self, lamp)
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



def max_by(li, lamp):
    i = np.argmax(listmap(lamp, li))
    return li[i]

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
    def __getitem__(self, item):
        return lambda x: x.__getitem__(item)
__ = __()
class __C:
    def __getattr__(self, item):
        return lambda x: x.__getattribute__(item)()
    def __getitem__(self, item):
        return lambda x: x.__getitem__(item)()
__C = __C()


def flat1(li):
    r = []
    for sublist in li:
        r += [e for e in sublist]
    return r

def concat(*args, axis=0):
    if len(args) == 0:
        return arr(ndims=axis + 1)
    args = list(args)
    for idx, aa in enumerate(args):
        if not isitr(aa):
            args[idx] = arr([aa])
    return arr(np.concatenate(tuple(args), axis=axis))



@dataclass
class Stacker:
    mat = None
    def cat(self, other, axis):
        if self.mat is None:
            self.mat = other
        else:
            self.mat = concat(
                self.mat,
                other,
                axis=axis
            )
    def vcat(self, other): self.cat(other, axis=0)
    def hcat(self, other): self.cat(other, axis=1)

class H_Stacker(Stacker):
    def __iadd__(self, other): self.hcat(other)
class V_Stacker(Stacker):
    def __iadd__(self, other): self.vcat(other)


def lay(a, new_layer):
    if len(a) == 0 or numel(a) == 0:
        if isitr(new_layer):
            new_layer = make3d(new_layer)
        else:
            new_layer = arr(new_layer)
            new_layer.shape = (1, 1, 1)
        return new_layer
    else:
        return np.concatenate((a, new_layer), axis=2)

def vstack(*args): return np.vstack(args)

def numel(aaa):
    if isstr(aaa) or istuple(aaa): return len(aaa)
    elif islist(aaa): return arr(aaa).size
    else: return aaa.size

def vert(a, row):
    if len(a) == 0 or numel(a) == 0:
        if isitr(row):
            row = make2d(row)
        else:
            row = arr(row)
            row.shape = (1, 1)
        return row
    else:
        return np.vstack((a, row))

def mymin(li):
    min_index, min_value = min(enumerate(li), key=operator.itemgetter(1))
    return min_value, min_index

def flatmax(li):
    return np.max(li).tolist()

def mymax(li):
    max_index, max_value = max(enumerate(li), key=operator.itemgetter(1))
    return max_value, max_index

def nanmax(l):
    return np.amax(list(filter(lambda x: x is not None, l)))

def nanmin(l):
    return np.amin(list(filter(lambda x: x is not None, l)))

def flatten(v):
    r = []
    for vv in v:
        if isitr(vv):
            for vvv in vv:
                r.append(vvv)
        else:
            r.append(vv)
    return arr(r)



def arr2d(v=(), dtype=None):
    return make2d(arr(v, dtype))

def arr3d(v=(), dtype=None):
    return make3d(arr(v, dtype))


def make3d(v):
    v = arr(v)
    if len(v.shape) == 3:
        return v
    v = make2d(v)
    # v.shape = (1,max(v.shape[0],1))
    v.shape = (v.shape[0], v.shape[1], 1)  # just use .flatten()
    return v

def objarray(alist, depth=1):
    shape = []
    li = alist
    for _ in range(depth):
        shape.append(len(li))
        li = li[0]
    arrr = np.empty(shape, dtype=object)
    arrr[:] = alist
    return arr(arrr)



def sorted_by(l1, l2):
    return [x for _, x in sorted(zip(l2, l1))]


def sort_human(li, keyparam=lambda e: e):
    convert = lambda text: float(text) if text.isdigit() else text
    alphanum = lambda key: [convert(c) for c in re.split(
        r'([-+]?[0-9]*\.?[0-9]*)',
        key)]

    def alphanum_join(element):
        sep = alphanum(element)
        new = []
        for s in sep:
            if not new:
                new.append(s)
            elif isstr(new[-1]) and isstr(s):
                new[-1] = new[-1] + s
            else:
                new.append(s)
        return new

    def get_first_e(the_li):
        while isitr(the_li) and not isinstance(the_li, str):
            the_li = the_li[0]
        return the_li

    orig_li = li  # debug
    li = arr(li).tolist()
    # noinspection PyUnresolvedReferences
    li.sort(key=lambda e: alphanum_join(get_first_e(keyparam(e))))
    return li

def Boole(lll):
    b = []
    for l in lll:
        b.append(not not l)
    return arr(b)


def nans(x, y=None):
    if y is None:
        y = x
    r = np.ones((x, y), dtype=float)
    @np.vectorize
    def makenan(_):
        return np.nan
    return makenan(r)

def trues(x, y):
    return np.ones((x, y), dtype=bool)

def zeros(x, y=None):
    if y is None:
        y = x
    return np.zeros((x, y))

def falses(x, y):
    return np.zeros((x, y), dtype=bool)

def bit_and(x, y):
    return np.bitwise_and(x, y)

# findFirstGreaterOrEqualValueIndexFast
def findFast(aa, vv):
    # log('findF1')
    increment_maybe = (aa[10] - aa[0]) / 10
    # log('findF2: ' + str(inc))
    tryFirst = int((vv - aa[0]) / increment_maybe) - 10
    # log('findF3: ' + str(tryFirst))
    while True:
        # try:
        if aa[tryFirst] > vv:
            # log('findF4: ' + str(tryFirst))
            return tryFirst
        tryFirst = tryFirst + 1
        # except:

def nprange(*arg):
    if len(arg) == 1:
        return arr(range(int(arg[0])))
    elif len(arg) == 2:
        return arr(range(int(arg[0]), int(arg[1])))
    elif len(arg) == 3:
        return arr(range(int(arg[0]), int(arg[1]), int(arg[2])))

def bools(aa):
    if isinstance(aa, np.ndarray) and len(aa.shape) > 1:
        aa = aa[0]
    return arr([x for x in map(bool, aa)]).astype(bool)

def ints(aa):
    if isinstance(aa, np.ndarray) and len(aa.shape) > 1:
        aa = aa[0]
    return arr([x for x in map(int, aa)]).astype(int)

def Select(lll, lamb):
    return list(filter(lamb, lll))



def isnan(v):
    import pandas
    return pandas.isnull(v)

    # Why not just do it the normal way?
    # if isinstance(v, Iterable):
    #     return arrayfun(lambda x: pandas.isnull(x), v)
    # else:
    #     return pandas.isnull(v)



def minidx(lll):
    # noinspection PyUnresolvedReferences
    return arr(lll).tolist().index(min(lll))


def ndims(lll):
    if not isinstance(lll, np.ndarray):
        return ndims(arr(lll))
        # err('not ready')
    return len(lll.shape)


# def append(l,v):
#     n = len(l)
#     a = np.zeros((1,n+1))
#     for i in range(n):
#         a[i] = l[i]
#     a[0,n] = v
#     return a


def mod(x, y):
    return x % y


def ismember(new, sym_i):
    return new in sym_i

# returns True if an element of list matches form, and False otherwise.
def MemberQ(lis, form):
    return form in lis

# gives a sorted list of the elements common to all the list.
def Intersection(list1, list2):
    r = []
    for l in list1:
        if l in list2:
            r.append(l)
    return sort(list(set(r)))

# yields True if e1 contains any of the elements of e2.
def ContainsAny(e1, e2):
    if not isitr(e2):
        return e2 in e1
    r = False
    for e in e2:
        if e in e1:
            r = True
    return r

# gives a list of the positions at which objects matching pattern appear in expr.
def Position(expr, pattern):
    r = []
    for idx, e in enumerate(expr):
        if pattern in e:
            r.append(idx)
    return r

def randperm(iii):
    return np.random.permutation(iii)

def Nmaxindices(li, N):
    idx_list = []

    for i in range(0, N):
        idx = maxindex(li)
        li[idx] = -np.inf
        idx_list = np.append(idx_list, idx)

    return idx_list

def maxindex(li, num=1):
    if num > 1:
        return tuple(np.argpartition(li, -num)[-num:])
    else:
        return np.argmax(li)





def atleast1(n): return max(n, 1)


def fix_index(i):
    if isinstance(i, slice):
        pass
    elif isitr(i):
        i = tuple([int(a) for a in i])
    else:
        i = int(i)
    return i

def inc(a, i):
    a[fix_index(i)] += 1



def invert(v):
    return arr(np.invert(v))

def bitwise_and(a, b):
    return arr(np.bitwise_and(a, b))




def unique(v):
    return np.unique(v)

def sort(v):
    return np.sort(v)

def safe_insert(aa, i, v):
    while len(aa) <= i:
        aa = concat(aa, arr([None]))
    aa = np.insert(aa, i, v)
    return aa





def isempty(a): return numel(a) == 0
# if isinstance(a, np.ndarray):
#     empty = False
#     for i in itr(a.shape):
#         if a.shape[i] < 1:
#             empty = True
#     return empty
# else:
#     return len(a) == 0

def contains(ss, s):
    return s in ss

def closest(data, target):
    # [clst,I] =
    # https://stackoverflow.com/questions/8089031/how-do-i-find-values-close-to-a-given-value#16965572
    data = arr(data)
    z_data = abs(data - target)
    pw1 = min(z_data)
    pw2 = z_data == pw1
    pw3 = np.where(pw2)
    I = pw3[0]
    # print(I)
    clst = data[I]
    return clst, I

def distinct(lis):
    return list(set(lis))

# tallies the elements in list, listing all distinct elements together with their multiplicities.
def Tally(lis):
    dist = distinct(lis)
    r = {}
    for d in dist:
        r[d] = lis.count(d)

def removeAll(lis, e):
    list(filter(lambda a: a != e, lis))




def insertZeros(ns, minl):
    s = str(ns)
    # n = float(ns)
    while len(s) < minl:
        s = '0' + s
    return s



def recurse_rep_itr(l, o, n, use_is=False):
    c = 0
    for idx, e in enum(l):
        if is_non_str_itr(e):
            e, cc = recurse_rep_itr(e, o, n, use_is=use_is)
            c += cc

        if use_is:
            b = e is o
        else:
            b = e == o
        if b:
            l[idx] = n
            c += 1
        elif isdict(e):
            l[idx], cc = recurse_rep_dict(e, o, n, use_is=use_is)
            c += cc
    return l, c

def recurse_rep_dict(d, o, n, use_is=False):
    c = 0
    for k, v in listitems(d):
        if use_is:
            b = k is o
        else:
            b = k == o
        if b:
            d[n] = v
            del d[o]
            k = n
            c += 1

        if is_non_str_itr(v):
            v, cc = recurse_rep_itr(v, o, n, use_is=use_is)
            c += cc

        if use_is:
            b = v is o
        else:
            b = v == o
        if b:
            d[k] = n
            c += 1
        elif isdict(v):
            d[k], cc = recurse_rep_dict(v, o, n, use_is=use_is)
            c += cc
    return d, c





def itr(a):
    return range(len(a))




def catfun(lamb, l, ax=0):
    return np.concatenate(tuple(list(map(lamb, l))), axis=ax)




def vertfun(lamb, l):
    for i in itr(l):
        if i == 0:
            row = lamb(l[i])
            if len(row.shape) < 2:
                row = [row]
            a = arr(row)
        else:
            # noinspection PyUnboundLocalVariable
            a = np.vstack((a, lamb(l[i])))
    # noinspection PyUnboundLocalVariable
    return a
    # return arrayfun(lamb,l).transpose()

def horzfun(lamb, l):
    for i in itr(l):
        if i == 0:
            colu = lamb(l[i])
            if len(colu.shape) < 2:
                colu = [colu]
            a = arr(colu)
        else:
            # noinspection PyUnboundLocalVariable
            a = np.hstack((a, lamb(l[i])))
    # noinspection PyUnboundLocalVariable
    return a
    # return arrayfun(lamb,l).transpose()

# horzfun(lambda y: y.rate,STIMULI_ALL[0])


def find(lis):
    return np.where(lis)[0]
