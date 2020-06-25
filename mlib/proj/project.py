import atexit

from mlib.proj.struct import main_mod_file
from mlib.proj.meta import daily
from mlib.proj.stat import enable_py_call_graph, py_deps
from mlib.web import shadow
from mlib.web.shadow import Project

QUIET = False

_already_initialized = False
def init():
    global _already_initialized
    if not _already_initialized:
        daily(
            enable_py_call_graph,
            Project.PYCALL_FILE
        )
        daily(
            atexit.register,
            py_deps,
            main_mod_file(),
            Project.PYDEPS_OUTPUT
        )
        atexit.register(shadow.build_docs)
        _already_initialized = True
