from abc import abstractmethod, ABC
from logging import warning
import os
import time

from mlib.boot.bootutil import isinstsafe, MException
from mlib.gpu import gpu_mem_str
from mlib.term import MagicTermLineLogger, reds


USE_THREADING = False
ticTime = None
STATUS = dict()
import numpy as np
import sys
import traceback
import os.path
def initTic():
    # err('')
    if ticTime is None:
        with open('bin/tic.txt', 'r') as myfile:
            data = myfile.read().replace('\n', '')

        setTic(np.long(data) * 1000)

        if len(sys.argv) > 2 and sys.argv[2] == 'tic':
            setTic(time.time() * 1000)

        log('got tic')

def getNextIncrementalFile(file):
    from mlib.file import File
    file = File(file)
    onename = file.name.replace('.', '_1.')
    onefile = file.parent[onename]
    if not onefile.exists:
        return onefile
    else:
        if '_' in file.name:
            base = file.name.split('_')[0]
            ext = file.name.split('_')[1].split('.')[1]
            n = int(file.name.split('_')[1].split('.')[0])
            n = n + 1
        else:
            base = file.name.split('.')[0]
            ext = file.name.split('.')[1]
            n = 1
        return file.parent[base + '_' + str(n) + '.' + ext]


def setTic(t):
    global ticTime
    ticTime = t

def tic():
    global ticTime
    ticTime = time.time() * 1000
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
from multiprocessing import Process, Queue
gpu_q = None
gpu_q_stop = Queue(maxsize=1)
import atexit
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

import platform
mac = platform.system() == 'Darwin'




def get_log_info(old_s, *args, ref=0):
    from mlib.proj import struct
    global STARTED_GPU_INFO_THREAD, gpu_q, latest_gpu_str
    if not mac and not STARTED_GPU_INFO_THREAD:
        STARTED_GPU_INFO_THREAD = True
        gpu_q = Queue(maxsize=1)
        Process(
            target=gpu_info_fun,
            args=(gpu_q, GPU_WATCH_PERIOD_SECS)
        ).start()
    if struct.Project.LOG_FILE is None: struct.Project.prep_log_file(None)
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
    if struct.Project.QUIET:
        line = ss
        file_line = ss
    else:
        line = f'{line_start}{resize_str(file, 14)}] {ss}'
        file_line = f'{line_start}{resize_str(file, 10)}) {old_s}'
    return line, file_line, t

warnings = []
def warn(ss, *args, silent=False, ref=0):
    ref = ref + 1  # or minus 1? I think its plus
    from mlib.term import lreds
    ss = lreds(ss)
    log(f'WARNING:{ss}', *args, silent=silent, ref=ref)
    warning(ss)
    warnings.append(ss)


_last_stacker = None
def log(ss, *args, silent=False, ref=0, stacker=None):
    global _last_stacker
    line, file_line, v = get_log_info(ss, *args, ref=ref)
    from mlib.term import MagicTermLine
    if not silent:
        from mlib.term import Progress
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
    from mlib.proj import struct
    with open(struct.Project.LOG_FILE.abspath, "a") as myfile:
        myfile.write(file_line + "\n")
    return v

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
        import threading
        ident = threading.get_ident()
        if ident in thread_name_dict.keys():
            name = thread_name_dict[ident]
        else:
            name = len(thread_name_dict.keys()) + 1
            thread_name_dict[ident] = name
        return 'T' + str(name)
    else:
        import multiprocessing
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

# log('mutil imports done')
def err(s, exc_class=MException):
    log(f'err:{s}')
    raise exc_class(s)
