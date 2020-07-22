USE_IMPORT_LOG_HOOK = False

print(
    f'booting')  # will need to flag for a log statement like this with a sys.argv flag for enhancing the performance of startup
from time import time
with open('_tic.txt', 'w') as f:
    f.write(str(int(time())))
import mlib.boot.mlog
if USE_IMPORT_LOG_HOOK:
    mlib.boot.mlog.register_import_log_hook()
import numpy
numpy.seterr(all='raise')

import mlib.err
mlib.err.register_exception_and_warning_handlers()

from mlib.boot.mlog import log


__all__ = [log]
