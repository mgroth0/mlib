from time import time

from mlib.boot import log
from mlib.boot.mutil import yellows, listkeys, cyans
from mlib.proj.struct import PROJ

def daily(fun, *args):
    n = fun.__name__
    if 'daily' not in listkeys(PROJ.STATE):
        PROJ.STATE['daily'] = {}
    if n not in listkeys(PROJ.STATE['daily']):
        log(
            yellows(f'running daily function: {n}')
        )
        fun(*args)
        d = PROJ.STATE['daily']
        d.update({n: time()})
        PROJ.STATE['daily'] = d
    elif PROJ.STATE['daily'][n] < time() - (3600 * 24):
        log(
            yellows(f'running daily function: {n}')
        )
        fun(*args)
        d = PROJ.STATE['daily']
        d.update({n: time()})
        PROJ.STATE['daily'] = d
    else:
        nex = PROJ.STATE['daily'][n] + (3600 * 24)
        log(
            cyans(
                f'{n} will run next in {nex - time()} seconds'
            )
        )
