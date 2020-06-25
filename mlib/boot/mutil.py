from abc import ABCMeta
import asyncio
from collections import UserString
from functools import wraps
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import operator
import pickle
import sys
import threading
# log('mutil imports..')
from collections.abc import Iterable
import traceback
from types import SimpleNamespace

import numpy as np
from scipy import signal
from scipy.signal import butter, lfilter

from mlib.boot import mlog
from mlib.boot.bootutil import pwd, ismac
from mlib.boot.mlog import log

def log_invokation(_func=None, *, with_class=False, with_instance=False, with_args=False, with_result=False):
    def actual_dec(ff):
        @wraps(ff)
        def fff(*args, **kwargs):
            ags = '' if not with_args else f'{args=}{kwargs=}'
            inst = '' if not with_instance else f' of {args[0]}'
            cls = '' if not with_class else f'{cn(ags[0])}.'
            s = f'{cls}.{ff.__name__}(){inst}'
            log(f'Invoking {s}...', ref=1)
            result = ff(*args, **kwargs)
            r_str = '' if not with_result else f' ({result=})'
            log(f'Finished {s}!{r_str}', ref=1)
            return result
        return fff

    if _func is None:
        # called with args. return the ACTUAL decoration
        return actual_dec
    else:
        # called with no args (_func magically added as first arg). This IS the decoration
        return actual_dec(_func)

from colorama import Fore, Style

def greens(s): return f'{Fore.GREEN}{s}{Style.RESET_ALL}'
def reds(s): return f'{Fore.RED}{s}{Style.RESET_ALL}'
def lreds(s): return f'{Fore.LIGHTRED_EX}{s}{Style.RESET_ALL}'
def blues(s): return f'{Fore.BLUE}{s}{Style.RESET_ALL}'
def yellows(s): return f'{Fore.YELLOW}{s}{Style.RESET_ALL}'
def magentas(s): return f'{Fore.MAGENTA}{s}{Style.RESET_ALL}'
def cyans(s): return f'{Fore.CYAN}{s}{Style.RESET_ALL}'


class Progress:
    erase = '\x1b[1A\x1b[2K'

    _instances = []
    def __init__(self, goal, verb='doing', pnoun='things'):
        self.last = 0
        self.goal = goal
        self._internal_n = 1
        log(f'{verb} $ {pnoun}', f'{goal:,}')
        self._instances += [self]
        self.entered = False

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

    def print(self, logfile=True):
        assert self.entered
        progress = round((self._internal_n / self.goal) * 100)
        if progress > self.last:
            self.last = progress
            bar = self.prog_bar(self._internal_n, self.goal)
            s = f'Progress: {bar} {progress}%'
            if progress == 100:
                print(s)
            else:
                print(f'{s}\r', end="")

            if logfile:
                log('$%', progress, silent=True)

    # noinspection PyUnusedLocal
    def tick(self, n=None, logfile=True):
        if n is None:
            self.tick(self._internal_n)
            self._internal_n += 1
        else:
            self._internal_n = n
            self.print()

def assert_int(f):
    if not float(f).is_integer():
        err(str(f) + ' is not a whole number, failing the assertion')
    return int(f)

def parse_inf(o):
    if not isstr(o):
        return o
    else:
        if o == 'inf':
            return np.inf
        elif o == '-inf':
            return -np.inf

def py():
    if ismac():
        return '/Users/matt/miniconda3/bin/python3'
    else:
        return '/home/matt/miniconda3/bin/python3'

def prep_log_file(name, new=False):
    mlog.prep_log_file(name, new=new)










def composed(*decs):
    # https://stackoverflow.com/questions/5409450/can-i-combine-two-decorators-into-a-single-one-in-python
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f

    return deco

def logverb(fun):
    def f(*args, **kwargs):
        log(fun.__name__ + '-ing')
        r = fun(*args, **kwargs)
        log(fun.__name__ + '-ed')
        return r

    return f

def is_non_str_itr(o):
    return isitr(o) and not isstr(o)




def lengthen_str(s, minlen):
    s = str(s)
    if len(s) >= minlen:
        return s
    else:
        return s + ' ' * (minlen - len(s))

def min_sec_form(dur_secs):
    mins, secs = divmod(dur_secs, 60)
    secs = round(secs)
    # secs = f'0{secs}' if secs < 10 else secs
    return f'{round(mins)}:{insertZeros(secs, 2)}'

def shorten_str(s, maxlen):
    s = str(s)
    if len(s) <= maxlen:
        return s
    else:
        return s[0:maxlen]

from packaging import version
def vers(s):
    return version.parse(str(s))










def cn(o): return o.__class__.__name__


def struct():
    return SimpleNamespace()

class MException(Exception): pass

def TODO():
    trace = traceback.extract_stack()[-2]
    fun_todo = trace[0]
    line = trace[1]
    return err(f'\n\n\t\t--TODO--\nFile "{fun_todo}", line {line}')

# log('mutil imports done')
def err(s, exc_class=MException):
    log(f'err:{s}')
    raise exc_class(s)

def min2sec(m): return float(m) * 60


def log_return(as_count=False):
    def f(ff):
        def fff(*args, **kwargs):
            r = ff(*args, **kwargs)
            s = f'{r}' if not as_count else f'{len(r)} {"items" if len(r) == 0 else r[0].__class__.__name__ + "s"}'
            log(f'{ff.__name__} returned {s}', ref=1)
            return r
        return fff
    return f



def ls(d=pwd()):
    import os
    dirlist = os.listdir(d)
    return dirlist

def mypwd(remote=None):
    if remote is None:
        return pwd()
    elif remote:
        if not ismac():
            return '/home/matt'
        else:
            return pwd()
    else:
        if ismac():
            return pwd()
        else:
            return '/Users/matt'

def listkeys(d):
    return list(d.keys())

def utf_decode(s, nonesafe=False):
    if nonesafe and s is None:
        return str(s)
    return s.decode('utf-8')


def arg_str(o):
    if isinstance(o, bool):
        return '1' if o else '0'
    else: return str(o)

def listfilt(fun, ll):
    return list(filter(fun, ll))
def arrfilt(fun, ll): return arr(listfilt(fun, ll))
def strs(ll): return listmap(str, ll)
def listmap(fun, ll):
    return list(map(fun, ll))
def arrmap(fun, ll): return arr(listmap(fun, ll))


def listitems(d): return list(d.items())

# works, but causes intelliJ warnings due to unresolved references
class Attributed:
    def __init__(self, **kwargs):
        for k, v in listitems(kwargs):
            self.__setattr__(k, v)

def ziplist(*args):
    return list(zip(*args))

def do_twice(func):
    def wrapper_do_twice(*args, **kwargs):
        func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper_do_twice


def track_progress(f):
    def runAndTrackProgress(iterable):
        with Progress(len(iterable)) as p:
            for item in iterable:
                y = f(item)
                p.tick()
                yield y
    return runAndTrackProgress

AIO_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(AIO_LOOP)

# noinspection PyUnusedLocal
def testInPools(f, li, af,
                test_multiprocess=True,
                test_threadpool=True,
                test_async=True
                ):
    # TODO: make this a decorator?

    t1 = log('Starting No Pool Test')
    f = track_progress(f)
    r = list(f(li))
    t2 = log('\tFinished No Pool Test')
    log(f'\t\ttotal time: {t2 - t1}s')

    if test_multiprocess:
        t1 = log('Starting CPU Pool Test')
        with Pool() as p:
            r = p.map(f, li)
        t2 = log('\tFinished CPU Pool Test')
        log(f'\t\ttotal time: {t2 - t1}s')

    if test_threadpool:
        t1 = log('Starting Thread Pool Test')
        with ThreadPool() as p:
            r = p.map(f, li)
        t2 = log('\tFinished Thread Pool Test')
        log(f'\t\ttotal time: {t2 - t1}s')

    # if test_async:
    #     from asyncio_pool import AioPool
    #     t1 = log('Starting AIO Pool Test')
    #     pool = AioPool()
    #     coro = pool.map(af, li)
    #     fut = asyncio.gather(coro)
    #     r = asyncio.get_event_loop().run_until_complete(fut)
    #     t2 = log('\tFinished AIO Pool Test')
    #     log(f'\t\total time: {t2 - t1}s')

    # TODO: add Wolfram concurrency
    # TODO: add GPU parallelism
    # TODO: add Java Multithreading? (no GIL)







def strrep(s, s1, s2):
    return s.replace(s1, s2)

def isa(o, name):
    return classname(o) == name

def classname(o):
    return o.__class__.__name__

def simple_classname(o):
    return classname(o).split('.')[-1]

def mkdir(name):
    from pathlib import Path
    Path(name).mkdir(parents=True, exist_ok=True)

enum = enumerate

def itr(a):
    return range(len(a))

def demean(lll):
    mean = np.mean(lll)
    return lll - mean

def normalized(lll):
    return lll / np.std(lll)

def nopl_high(data, Fs):
    sig = bandstop(data, 59, 61, Fs, 1)
    return highpass(sig, 1, Fs)

def highpass(data, Hz, Fs, order=1):
    nyq = 0.5 * Fs
    normal_cutoff = Hz / nyq
    # noinspection PyTupleAssignmentBalance
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return signal.filtfilt(b, a, data)

def nopl(data, Fs):
    return bandstop(data, 59, 61, Fs, 1)

def lowpass(data, lowcut, Fs, order=1):
    nyq = 0.5 * Fs
    low = lowcut / nyq
    # noinspection PyTupleAssignmentBalance
    i, u = butter(order, low, btype='lowpass')
    y = lfilter(i, u, data)
    return y


# def notch(data,bad_freq,Fs,order):
#     width =
#     return bandstop(data, lowcut, highcut, fs, order)

def bandstop(data, lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    # noinspection PyTupleAssignmentBalance
    i, u = butter(order, [low, high], btype='bandstop')
    y = lfilter(i, u, data)
    return y

def difffun(lamb, l):
    newlist = arrayfun(lamb, l)
    diffs = arr()
    for idx, e in enumerate(newlist):
        if idx == 0:
            last_e = e
            continue
        # noinspection PyUnboundLocalVariable
        diffs += e - last_e
        last_e = e
    return diffs

def arrayfun(lamb, l):
    return arr(list(map(lamb, l)))

def catfun(lamb, l, ax=0):
    return np.concatenate(tuple(list(map(lamb, l))), axis=ax)

def run_in_daemon(target):
    threading.Thread(target=target, daemon=True).start()

def run_in_thread(target, **kwargs):
    t = threading.Thread(target=target, **kwargs)
    t.start()
    return t

def addpath(p):
    sys.path.append(p)

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

from datetime import datetime

def now():
    # datetime object containing current date and time
    noww = datetime.now()

    # print("now =", now)
    # dd/mm/YY H:M:S
    dt_string = noww.strftime("%m/%d/%Y %H:%M:%S")
    # print("date and time =", dt_string)
    return dt_string

# noinspection PyDefaultArgument
def interact(l=vars()):
    import code
    code.interact(local=l)

def find(lis):
    return np.where(lis)[0]

# noinspection PyUnusedLocal
def slope(m, x, y):
    from scipy.stats import linregress
    # log('slope1')
    # try:
    not_nans = invert(isnan(y))
    # except Exception as e:
    if np.count_nonzero(not_nans) < 2:
        return None
    not_infs = invert(isinf(y))
    x = x[bitwise_and(not_nans, not_infs)]
    y = y[bitwise_and(not_nans, not_infs)]
    # from PyMat import matfun
    # coefs = matfun(m,'polyfit', x, y, 1)
    # coefs = arr(coefs)
    # log('slopeR')
    # return coefs[0,0]
    # noinspection PyUnresolvedReferences
    return linregress(x, y).slope

def strcmp(s1, s2, ignore_case=False):
    if ignore_case:
        return s1.lower() == s2.lower()
    return s1 == s2

def save_pickle(o, f):
    log('saving pickle:' + f)
    with open(f, 'wb') as file:
        pickle.dump(o, file,
                    protocol=pickle.HIGHEST_PROTOCOL)
    log('saved pickle: ' + f)

def load_pickle(f):
    log('loading pickle: $', f)
    with open(f, 'rb') as file:
        o = pickle.load(file)
        return o
    log('loaded pickle: $', f)

debug_i = 0

def todict(obj, classkey=None):
    global debug_i
    debug_i = debug_i + 1
    if debug_i == 100:
        raise Exception
    log('todict(' + classname(obj) + '): ' + str(obj))
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        # noinspection PyCallingNonCallable,PyProtectedMember
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        # noinspection PyUnresolvedReferences
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

def Nmaxindices(li, N):
    idx_list = []

    for i in range(0, N):
        idx = maxindex(li)
        li[idx] = -np.inf
        idx_list = np.append(idx_list, idx)

    return idx_list

def maxindex(li):
    return np.argmax(li)

def numel(aaa):
    return aaa.size

def randperm(iii):
    return np.random.permutation(iii)

def disp(s):
    return log(s)

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




# def append(l,v):
#     n = len(l)
#     a = np.zeros((1,n+1))
#     for i in range(n):
#         a[i] = l[i]
#     a[0,n] = v
#     return a

def mod(x, y):
    return x % y

def trues(x, y):
    return np.ones((x, y), dtype=bool)

def zeros(x, y):
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

def nanstd(lll):
    # l = list(filter(lambda x: not isnan(x),l))
    lll = arr(lll)
    lll = lll[np.invert(isnan(lll))]
    if len(lll) > 0:
        # tolist needed because dtype is obj sometimes for some reason ????
        lll = lll[np.invert(isinf(lll.tolist()))]
    rr = safestd(lll)
    return rr

def safeStandardErr(lll):
    return safestd(lll) / sqrt(len(lll))

def ndims(lll):
    if not isinstance(lll, np.ndarray):
        return ndims(arr(lll))
        # err('not ready')
    return len(lll.shape)

def nanmean(lll):
    if ndims(lll) > 2:
        err('no ready')
    elif ndims(lll) == 2:
        rrr = arr()
        for i in range(0, lll.shape[1]):
            colu = list(filter(lambda x: not isnan(x), lll[:, i]))
            rrr += safemean(colu)
    else:  # 1-d
        lll = list(filter(lambda x: not isnan(x), lll))
        rrr = safemean(lll)
    # noinspection PyUnboundLocalVariable
    return rrr

def all_superclasses(clazz):
    li = []
    for b in clazz.__bases__:
        li.extend([b] + all_superclasses(b))
    return li

def isinstsafe(o, c):
    return isinstance(o, c) or c in all_superclasses(o.__class__)

def sqrt(l):
    return np.sqrt(l)

def isint(v):
    return isinstance(v, int) or isinstance(v, np.int64)

def isstr(v):
    return isinstance(v, str)

def flat(l): return arr(l).flatten()

flatn = lambda l: arr([item for sublist in l for item in sublist])

# def append


def isitr(v):
    return isinstance(v, Iterable)

def mat():
    a = arr()
    a.shape = (0, 0)
    return a

def atleast1(n): return max(n, 1)

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

import re
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

    li = arr(li).tolist()
    # noinspection PyUnresolvedReferences
    li.sort(key=lambda e: alphanum_join(get_first_e(keyparam(e))))
    return li


def add_headers_to_mat(ar2d, row_headers, col_headers, alphabetize=False):
    ar2d = np.concatenate((make2d(col_headers), arr(ar2d)), axis=0)
    row_headers = make2d(np.insert(row_headers, 0, None)).T
    cmat = np.concatenate((row_headers, ar2d), axis=1)
    if alphabetize:
        cmat[1:] = sort_human(cmat[1:])
        temp = np.transpose(arr(cmat))
        temp[1:] = sort_human(temp[1:])
        cmat = np.transpose(arr(temp))
    return cmat

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

def Boole(lll):
    b = []
    for l in lll:
        b.append(not not l)
    return arr(b)

# just prevents stupid warning when taking mean of empty list
def safemean(v):
    import statistics
    if isinstance(v, (int, float)):
        return v
    if len(v) > 0:
        if isinstance(v, np.ndarray):
            v = v.flatten()
        v = list(filter(lambda x: x != 'Excluded', v))
        if isinstance(v[0], str):
            v = list(map(float, v))
        return statistics.mean(map(float, v))
    else:
        return None

def flatten(v):
    r = []
    for vv in v:
        if isitr(vv):
            for vvv in vv:
                r.append(vvv)
        else:
            r.append(vv)
    return arr(r)

def safestd(v):
    if len(v) > 0:
        return np.std(arr(np.vectorize(float)(v)))
    else:
        return None

def xcorr(x, y, Fs, lagSecs=30):
    log('in xcorr')

    maxlags = np.floor(Fs * lagSecs)

    x = x - np.mean(x)
    y = y - np.mean(y)

    x = x.flatten()
    y = y.flatten()

    Nx = len(x)
    if Nx != len(y):
        raise ValueError('x and y must be equal length')

    ccc = np.correlate(x, y, mode='full')

    if maxlags is None:
        maxlags = Nx - 1

    if maxlags >= Nx or maxlags < 1:
        raise ValueError('maxlags must be None or strictly positive < %d' % Nx)

    # zero_lag_idx = int((len(ccc) - 1) / 2)
    ccc = ccc[int(Nx - 1 - maxlags):int(Nx + maxlags)]

    # denom = sqrt((x[zero_lag_idx]**2) * y[zero_lag_idx]**2)
    denom = sqrt(np.correlate(x, x, mode='full')[len(x) - 1] * np.correlate(y, y, mode='full')[len(y) - 1])

    if denom == 0:
        return None, None, None, None, None
    for idx, cc in enumerate(ccc):
        ccc[idx] = cc * 1 / denom

    mx = max(ccc)
    mn = min(ccc)
    mx_latency = ccc.tolist().index(mx)
    mn_latency = ccc.tolist().index(mn)

    # [max_mi,i] = max(abs(xc));
    mx_latency_secs = (mx_latency - (maxlags + 1)) / Fs
    mn_latency_secs = (mn_latency - (maxlags + 1)) / Fs

    return ccc, mx, mn, mx_latency_secs, mn_latency_secs

class mparray(np.ndarray):
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

    def filtered(self, *tests):
        return arr(filtered(self, *tests))
    def first(self, *tests):
        return filtered(self, *tests)[0]
    def map(self, fun):
        return arr(listmap(fun, self))

    def join(self, s):
        return s.join(self.tolist())

def arr2d(v=(), dtype=None):
    return make2d(arr(v, dtype))

def arr3d(v=(), dtype=None):
    return make3d(arr(v, dtype))


def sigfig(number, ndigits):
    testnumber = abs(number)
    if testnumber == 0:
        return 0
    ref = 1
    roundn = ndigits
    while testnumber >= ref:
        roundn -= 1
        ref = ref * 10
    ref = 0.1
    while testnumber <= ref:
        roundn += 1
        ref = ref / 10
    return round(number, roundn)



# numpy thinks infinity is real, i dont think so
def isreal(n):
    if n is None or abs(n) == np.inf:
        return False
    return np.isreal(n)

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


def arr(v=(), dtype=None):
    if not isinstance(v, Iterable):
        v = [v]
    return mparray(v, dtype=dtype)

def isinf(v):
    if v is None:
        return False
    return arr(np.isinf(v))

def inv_map(d): return {v: k for k, v in d.items()}

def invert(v):
    return arr(np.invert(v))

def bitwise_and(a, b):
    return arr(np.bitwise_and(a, b))

def append(l, v):
    return arr(np.append(l, v))

def simple_downsample(aa, ds):
    bb = arr()
    for i in range(0, len(aa), ds):
        bb = append(bb, aa[i])
    return bb
    # if mod(len(aa),ds) == 0:
    #     a = np.array([1.,2,6,2,1,7])
    #     return a.reshape(-1, ds).mean(axis=1)
    # else:
    #     pad_size = math.ceil(float(len(aa)) / ds) * ds - len(aa)
    #     b_padded = np.append(aa, np.zeros(pad_size) * np.NaN)
    #     return scipy.nanmean(b_padded.reshape(-1,ds), axis=1)

def nandiv(a, v):
    r = arr()
    for i in itr(a):
        if isnan(a[i]):
            r = append(r, None)
        else:
            r = append(r, a[i] / v)
    return r

def unique(v):
    return np.unique(v)

def sort(v):
    return np.sort(v)

def safe_insert(aa, i, v):
    while len(aa) <= i:
        aa = concat(aa, arr([None]))
    aa = np.insert(aa, i, v)
    return aa

def num2str(num):
    return str(num)

def iseven(n):
    return n % 2 == 0

def concat(*args, axis=0):
    args = list(args)
    for idx, aa in enumerate(args):
        if not isitr(aa):
            args[idx] = arr([aa])
    return arr(np.concatenate(tuple(args), axis=axis))

def isblank(s):
    return len(s.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')) == 0
def notblank(s): return not isblank(s)

def isempty(a):
    if isinstance(a, np.ndarray):
        empty = False
        for i in itr(a.shape):
            if a.shape[i] < 1:
                empty = True
        return empty
    else:
        return len(a) == 0

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



def functionalize(f):
    def ff(): return f
    return ff


def singleton(cls): return cls()
def run(cls): cls().run()

class Runner(ABCMeta):
    # noinspection PyMethodParameters
    def __new__(metacls, name, bases, attrs):
        cls = type.__new__(metacls, name, bases, attrs)
        if '__super_runner__' in listkeys(attrs):
            # print(f'debug: {name} is cls ({attrs=})')
            return cls
        else:
            # print(f'debug: {name} is none ({attrs=})')
            cls().super_run()
            return None

# done know if this works or is useful. idea from fn.py
@singleton
class __:
    def __getattr__(self, item):
        return lambda x: x.__getattribute__(item)

# idea is that it could auto format on edits but not sure how to implement this. example: trailing newlines or strip
class FormattedString(UserString):
    pass

def filtered(lis, *tests):
    r = []
    for item in lis:
        add = True
        for test in tests:
            if not test(item): add = False
        if add: r += [item]
    return r
