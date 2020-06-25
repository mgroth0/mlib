from pathlib import Path
import sys
import os
import argparse
import platform
def ismac():
    return platform.system() == 'Darwin'
def islinux():
    return platform.system() == 'Linux'
def pwd(): return os.getcwd()
HOME = str(Path.home())
LOCAL_CWD = os.getcwd()
REMOTE_CWD = None
exceptions = []
def register_exception_handler():
    import traceback
    def my_except_hook(exctype, value, tb):
        listing = traceback.format_exception(exctype, value, tb)
        import mlib.boot.mutil as mutil
        if not ismac():
            for i, line in mutil.enum(listing):
                if line.startswith('  File "'):
                    linux_path = line.split('"')[1]
                    mac_path = LOCAL_CWD + linux_path
                    listing[i] = listing[i].replace(linux_path, mac_path)
                    listing[i] = listing[i].replace(REMOTE_CWD, '')
        if exctype == mutil.MException:
            del listing[-2]
            listing[-2] = listing[-2].split('\n')[0] + '\n'
            listing[-1] = listing[-1][0:-1]
        print("".join(listing), file=sys.stderr)
        print('ERROR ERROR ERROR')
        # exit_for_real(1) #bad. with this, one exception thrown in pdb caused process to exit
        exceptions.append((exctype, value, tb))
        sys.__excepthook__(exctype, value, tb)
    sys.excepthook = my_except_hook

def margparse(**kwargs):
    parser = argparse.ArgumentParser()
    for key, value in kwargs.items():
        parser.add_argument(f'--{key}', type=value, required=True)
    FLAGS = parser.parse_args()
    print('EXECUTION ARGUMENTS: ' + str(FLAGS))
    return FLAGS

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
