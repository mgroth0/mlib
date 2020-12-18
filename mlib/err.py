import atexit
import sys

from mlib.boot.lang import ismac, pwd, enum

exceptions = []
def register_exception_and_warning_handlers():
    import traceback
    def my_except_hook(exctype, value, tb):
        from mlib.proj.struct import REMOTE_CWD
        exceptions.append((exctype, value, tb))
        if exctype != Short_MException:
            listing = traceback.format_exception(exctype, value, tb)
            if not ismac():
                for i, line in enum(listing):
                    if line.startswith('  File "'):
                        linux_path = line.split('"')[1]
                        mac_path = pwd() + linux_path
                        listing[i] = listing[i].replace(linux_path, mac_path)
                        listing[i] = listing[i].replace(REMOTE_CWD, '')
            if exctype == MException:
                del listing[-2]
                listing[-2] = listing[-2].split('\n')[0] + '\n'
                listing[-1] = listing[-1][0:-1]
            print("".join(listing), file=sys.stderr)
            print('ERROR ERROR ERROR')
            # exit_for_real(1) #bad. with this, one exception thrown in pdb caused process to exit
            sys.__excepthook__(exctype, value, tb)
        else:
            sys.exit(1)
    sys.excepthook = my_except_hook
    @atexit.register
    def print_exception_again():
        from mlib.boot.mlog import log
        import mlib.boot.mlog
        # @atexit.register is first in, last out.

        # exctype, value, tb
        if not mlib.boot.mlog.QUIET: log(f'{len(exceptions)=}')
        for e in exceptions:
            if e[0] != Short_MException:
                sys.__excepthook__(*e)

    @atexit.register
    def print_warnings_again():
        from mlib.boot.mlog import warnings, log
        import mlib.boot.mlog
        if not mlib.boot.mlog.QUIET: log(f'{len(warnings)=}')
        if len(warnings) > 0:
            log('WARNINGS:')
        for w in warnings:
            log(f'\t{w}')




class MException(Exception): pass
class Short_MException(MException): pass


def assert_int(f):
    from mlib.boot.mlog import err
    if not float(f).is_integer():
        err(str(f) + ' is not a whole number, failing the assertion')
    return int(f)
