# CREDS: https://github.com/peci1

import re
import subprocess
import sys
from types import SimpleNamespace

def gpu_stats(the_gpu_i):
    breakpoint()
    processes = subprocess.run('nvidia-smi', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if processes.returncode != 0:
        print('nvidia-smi exited with error code {}:'.format(processes.returncode))
        print(processes.stdout.decode() + processes.stderr.decode())
        sys.exit()
    lines_proc = processes.stdout.decode().split("\n")
    lines = [line + '\n' for line in lines_proc[:-1]]
    lines += lines_proc[-1]

    gpui = -1

    lines_to_print = []
    # Copy the utilization upper part verbatim
    for i in range(len(lines)):
        if not lines[i].startswith("| Processes:"):
            lines_to_print.append(lines[i].rstrip())
        else:
            i += 3
            break

    gpu_stat = SimpleNamespace()
    gpu_stat.used_mem = None
    gpu_stat.total_mem = None
    gpu_stat.gpu_util = None
    gpu_stat.mem_util = None

    for i in range(len(lines_to_print)):
        line = lines_to_print[i]
        m = re.match(r"\| (?:N/A|..%)\s+[0-9]{2,3}C.*\s([0-9]+)MiB\s+\/\s+([0-9]+)MiB.*\s([0-9]+)%", line)
        if m is not None:
            gpui = gpui + 1
            if gpui == the_gpu_i:
                gpu_stat.used_mem = int(m.group(1))
                gpu_stat.total_mem = int(m.group(2))
                gpu_stat.gpu_util = int(m.group(3)) / 100.0
                gpu_stat.mem_util = gpu_stat.used_mem / float(gpu_stat.total_mem)
                break

    return gpu_stat
import os

def mygpus():
    if "CUDA_VISIBLE_DEVICES" not in list(os.environ.keys()):
        return "all?"
    else:
        devs = os.environ["CUDA_VISIBLE_DEVICES"]
        if devs == '':
            return []
        else:
            return list(map(int, devs.split(',')))
def gpu_mem_str():
    devices = mygpus()
    if isinstance(devices, str): return devices
    r = '(' + os.environ["CUDA_VISIBLE_DEVICES"] + ')'
    for d in devices:
        stat = gpu_stats(d)
        r = r + str(stat.used_mem) + '/' + str(stat.total_mem)
        r = r + ','
    r = r[0:-1]
    return r

def get_available_gpus():
    import tensorflow as tf
    # noinspection PyUnresolvedReferences
    local_device_protos = tf.python.client.device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']
