from abc import abstractmethod, ABC
from logging import warning
import os
import time
import traceback
import os.path
from multiprocessing import Process, Queue
import atexit
import platform
import multiprocessing
import threading

import numpy as np

from mlib.boot.lang import isinstsafe
from mlib.err import MException, Short_MException
from mlib.gpu import gpu_mem_str
from mlib.term import MagicTermLine, Progress, MagicTermLineLogger, lreds, reds, yellows, cyans


USE_THREADING = False
ticTime = None
STATUS = dict()

def initTic():
    if ticTime is None:
        with open('_tic.txt', 'r') as myfile:
            data = myfile.read().strip()
        setTic(np.long(data) * 1000)
    return ticTime



def setTic(t):
    global ticTime
    ticTime = t

def tic():
    global ticTime
    # ticTime = time.time() * 1000
    ticTime = initTic()
    return ticTime

TIC = tic()

def toc():
    global ticTime
    if ticTime is None:
        # print('NOT GOOD, ticTIME  is None (' + s + ')')
        return -1
        # err('not good')
        # tic()
    return (time.time() * 1000) - ticTime

def resize_str(s, n):
    if len(s) > n:
        s = s[0:n]
    elif len(s) < n:
        dif = n - len(s)
        for i in range(0, dif):
            s = s + ' '
    return s

def toc_str(t=None):
    if t is None:
        return f'{toc() / 1000:.2f}'
    else:
        return f'{t:.2f}'

STARTED_GPU_INFO_THREAD = False

gpu_q = None
gpu_q_stop = Queue(maxsize=1)

def stop_gpu_info_fun():
    gpu_q_stop.put('anything')
atexit.register(stop_gpu_info_fun)
GPU_WATCH_PERIOD_SECS = 1
latest_gpu_str = ''

def gpu_info_fun(gpu_q, GPU_WATCH_PERIOD_SECS):
    while gpu_q_stop.empty():
        s = gpu_mem_str()
        gpu_q.put(s, block=True)
        time.sleep(GPU_WATCH_PERIOD_SECS)


mac = platform.system() == 'Darwin'

QUIET = False

def get_log_info(old_s, *args, ref=0):
    global STARTED_GPU_INFO_THREAD, gpu_q, latest_gpu_str
    if not mac and not STARTED_GPU_INFO_THREAD:
        STARTED_GPU_INFO_THREAD = True
        gpu_q = Queue(maxsize=1)
        Process(
            target=gpu_info_fun,
            args=(gpu_q, GPU_WATCH_PERIOD_SECS)
        ).start()

    t = toc() / 1000
    ss = old_s
    for idx, aa in enumerate(args):
        ss = ss.replace("$", str(aa), 1)
    stack = traceback.extract_stack()
    indx = -3 - ref
    while len(stack) < abs(indx):
        if indx < 0:
            indx = indx + 1
        else:
            indx = indx - 1
    file = {
        1: 'MATLAB'
    }.get(len(stack), os.path.basename(stack[indx][0]).split('.')[0])
    line_start = f'[{processTag()}|{toc_str(t)}|'
    if not mac:
        if not gpu_q.empty():
            latest_gpu_str = gpu_q.get()
        line_start = f'{line_start}{latest_gpu_str}|'
    if QUIET:
        line = ss
        file_line = ss
    else:
        line = f'{line_start}{resize_str(file, 14)}] {ss}'
        file_line = f'{line_start}{resize_str(file, 10)}) {old_s}'
    return line, file_line, t

warnings = []
def warn(ss, *args, silent=False, ref=0):
    ref = ref + 1  # or minus 1? I think its plus

    ss = lreds(ss)
    log(f'WARNING:{ss}', *args, silent=silent, ref=ref)
    warning(ss)
    warnings.append(ss)

def logr(thing):
    log(thing, ref=1)
    return thing

_last_stacker = None
LOG_FILE = None
def log(ss, *args, silent=False, ref=0, stacker=None):
    global _last_stacker
    line, file_line, v = get_log_info(ss, *args, ref=ref)

    if not silent:
        for p in Progress._instances:
            if not p.DISABLED:
                print(MagicTermLine.ERASE)
        for p in Progress._instances:
            if not p.DISABLED:
                p.print(normally=True)

        if _last_stacker is not None and _last_stacker != stacker:
            if not _last_stacker.done:
                # err here causes recursion
                # raise Exception(f'not ready to stack multiple logs. {_last_stacker=},{line=}')
                _last_stacker.kill()
            print('')
        if stacker is not None:
            stacker: MagicTermLineLogger
            stacker.line = line
            if not stacker.killed and not stacker.DISABLED:
                stacker.print()
            else:
                print(reds(line))
        else:
            print(line)
    _last_stacker = stacker
    if LOG_FILE is not None:
        with open(LOG_FILE.abspath, "a") as myfile:
            myfile.write(f"{file_line}\n")
    return v

def logy(ss, *args, **kwargs):
    log(yellows(ss), *args, **kwargs)
def logr(ss, *args, **kwargs):
    log(reds(ss), *args, **kwargs)
def logc(ss, *args, **kwargs):
    log(cyans(ss), *args, **kwargs)

def processTag():
    name = processName()
    if USE_THREADING:
        return name
    else:
        if 'Main' in name:
            return 'MP'
        else:
            return 'L' + name[-1]

thread_name_dict = dict()

def processName():
    if USE_THREADING:
        ident = threading.get_ident()
        if ident in thread_name_dict.keys():
            name = thread_name_dict[ident]
        else:
            name = len(thread_name_dict.keys()) + 1
            thread_name_dict[ident] = name
        return 'T' + str(name)
    else:
        return multiprocessing.current_process().name



class Muffle:
    def __init__(self, *objs):
        self.objs = objs
    def __enter__(self):
        for o in self.objs:
            if o is not None and isinstsafe(o, Muffleable):
                o.muffle()
    def __exit__(self, exc_type, exc_val, exc_tb):
        for o in self.objs:
            if o is not None and isinstsafe(o, Muffleable):
                o.unmuffle()
class Muffleable(ABC):
    @abstractmethod
    def muffle(self): pass
    @abstractmethod
    def unmuffle(self): pass


STACK_KEY = ''


def TODO():
    trace = traceback.extract_stack()[-2]
    fun_todo = trace[0]
    line = trace[1]
    return err(f'\n\n\t\t--TODO--\nFile "{fun_todo}", line {line}')

def err(s, exc_class=MException):
    log(reds(f'err:{s}'))
    raise exc_class(s)

def short_err(s):
    err(s, exc_class=Short_MException)




def register_import_log_hook():
    imported = []
    import builtins
    old_imp = builtins.__import__
    def custom_import(*args, **kwargs):
        m = old_imp(*args, **kwargs)
        ms = m.__name__
        if ms not in imported:
            log(f'imported {ms}')
            imported.append(ms)
        return m
    builtins.__import__ = custom_import

def disp(s):
    return log(s)




def logverb(fun):
    def f(*args, **kwargs):
        log(fun.__name__ + '-ing')
        r = fun(*args, **kwargs)
        log(fun.__name__ + '-ed')
        return r

    return f



def log_return(as_count=False):
    def f(ff):
        def fff(*args, **kwargs):
            r = ff(*args, **kwargs)
            s = f'{r}' if not as_count else f'{len(r)} {"items" if len(r) == 0 else r[0].__class__.__name__ + "s"}'
            log(f'{ff.__name__} returned {s}', ref=1)
            return r
        return fff
    return f

def setup_logging(verbose=True):
    import logging
    import tensorflow as tf
    import mlib.boot.mlog as loggy
    class TF_Log_Filter(logging.Filter):
        def filter(self, record):
            line, file_line, v = loggy.get_log_info(record.msg)
            record.msg = line
            return True
    tf.get_logger().setLevel('DEBUG')
    if not verbose:
        tf.get_logger().addFilter(TF_Log_Filter())  # not working
        tf.autograph.set_verbosity(1)
        import os
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        # tf.get_logger().setLevel('INFO')
        tf.get_logger().setLevel('WARNING')  # always at least show warnings

log('finished setting up logging')
