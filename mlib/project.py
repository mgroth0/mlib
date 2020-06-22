import atexit

from mlib.boot.mutil import main_mod_file
from mlib.proj.meta import daily
from mlib.proj.stat import enable_py_call_graph, py_deps
from mlib.web import shadow
from mlib.web.shadow import PROJ

daily(
    enable_py_call_graph,
    PROJ.PYCALL_FILE
)
daily(
    atexit.register,
    py_deps,
    main_mod_file(),
    PROJ.PYDEPS_OUTPUT
)
atexit.register(shadow.build_docs)
