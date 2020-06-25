from time import time

from mlib.boot import log
from mlib.boot.mutil import yellows, listkeys, cyans
from mlib.proj.struct import Project

def daily(fun, *args):
    n = fun.__name__
    if 'daily' not in listkeys(Project.STATE):
        Project.STATE['daily'] = {}
    if n not in listkeys(Project.STATE['daily']):
        log(
            yellows(f'running daily function: {n}')
        )
        fun(*args)
        d = Project.STATE['daily']
        d.update({n: time()})
        Project.STATE['daily'] = d
    elif Project.STATE['daily'][n] < time() - (3600 * 24):
        log(
            yellows(f'running daily function: {n}')
        )
        fun(*args)
        d = Project.STATE['daily']
        d.update({n: time()})
        Project.STATE['daily'] = d
    else:
        nex = Project.STATE['daily'][n] + (3600 * 24)
        log(
            cyans(
                f'{n} will run next in {nex - time()} seconds'
            )
        )
