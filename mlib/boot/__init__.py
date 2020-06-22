print('booting')
import atexit
import sys
import numpy
numpy.seterr(all='raise')

from mlib.boot.bootutil import register_exception_handler, exceptions
register_exception_handler()

@atexit.register
def print_exception_again():
    from mlib.boot.mlog import log
    # @atexit.register is first in, last out.

    # exctype, value, tb
    log(f'{len(exceptions)=}')
    for e in exceptions:
        sys.__excepthook__(*e)
@atexit.register
def print_warnings_again():
    from mlib.boot.mlog import warnings
    log(f'{len(warnings)=}')
    if len(warnings) > 0:
        log('WARNINGS:')
    for w in warnings:
        log(f'\t{w}')

from mlib.boot.mlog import log
from mlib.boot.mutil import log_invokation

__all__ = [log]
