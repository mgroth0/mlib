import os
import time

from mlib.gpu import gpu_mem_str

USE_THREADING = False
ticTime = None
LOG_FILE = None
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
    import mlib.boot.mutil as mutil
    file = mutil.File(file)
    onename = file.name.replace('.', '_1.')
    onefile = mutil.File(file.parentDir).resolve(onename)
    if not onefile.exists():
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
        return mutil.File(file.parentDir).resolve(base + '_' + str(n) + '.' + ext)

def prep_log_file(filename, new=False):
    if filename is None:
        filename = os.path.basename(sys.argv[0]).replace('.py', '')

    import mlib.boot.mutil as mutil
    import mlib.boot.bootutil as bootutil
    if bootutil.ismac():
        filename = '_logs/local/' + filename
    else:
        filename = '_logs/remote/' + filename

    filename = filename + '.log'
    filename = mutil.MITILI_FOLDER().respath(filename)

    if new:
        filename = getNextIncrementalFile(filename)

    import mlib.boot.mutil as mutil
    global LOG_FILE
    if LOG_FILE is None:
        LOG_FILE = mutil.File(filename)
    if LOG_FILE.exists():
        LOG_FILE.delete()
    LOG_FILE.mkparents()
    LOG_FILE.touch()
    log(f'Initialized log file: {mutil.File(LOG_FILE).relpath}')

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
    global STARTED_GPU_INFO_THREAD, gpu_q, latest_gpu_str
    if not mac and not STARTED_GPU_INFO_THREAD:
        STARTED_GPU_INFO_THREAD = True
        gpu_q = Queue(maxsize=1)
        Process(
            target=gpu_info_fun,
            args=(gpu_q, GPU_WATCH_PERIOD_SECS)
        ).start()
    if LOG_FILE is None: prep_log_file(None)
    t = toc() / 1000
    ss = old_s
    for idx, aa in enumerate(args):
        ss = ss.replace("$", str(aa), 1)
    stack = traceback.extract_stack()
    file = {
        1: 'MATLAB'
    }.get(len(stack), os.path.basename(stack[-3 - ref][0]).split('.')[0])
    line_start = f'[{processTag()}|{toc_str(t)}|'
    if not mac:
        if not gpu_q.empty():
            latest_gpu_str = gpu_q.get()
        line_start = f'{line_start}{latest_gpu_str}|'
    line = f'{line_start}{resize_str(file, 14)}] {ss}'
    file_line = f'{line_start}{resize_str(file, 10)}) {old_s}'
    return line, file_line, t

def log(ss, *args, silent=False, ref=0):
    line, file_line, v = get_log_info(ss, *args, ref=ref)

    if not silent:
        from mlib.boot.mutil import Progress
        for p in Progress._instances:
            line = Progress.erase + line
        print(line)
        for p in Progress._instances:
            p.print()
    with open(LOG_FILE.abspath, "a") as myfile:
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


