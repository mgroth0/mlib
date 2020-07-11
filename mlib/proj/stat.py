import atexit

from pycallgraph import PyCallGraph, Config
from pycallgraph.output import GraphvizOutput

import mlib.file
from mlib.file import File
from mlib.shell import shell

def enable_py_call_graph(output):
    # Makes code about 4 times slower
    DEFAULT_PY_CALL_GRAPH = PyCallGraph(
        output=GraphvizOutput(
            output_file=mlib.file.abspath
        ),
        config=Config(
            max_depth=2
        )
    )
    atexit.register(DEFAULT_PY_CALL_GRAPH.done)
    DEFAULT_PY_CALL_GRAPH.start()

# module is actually called pydeps so keep underscore to avoid bugs
def py_deps(start, output):
    start = File(start).abspath
    output = File(output).abspath
    if not output.endswith('.svg'):
        output = output + '.svg'
    return shell(
        '/Users/matt/miniconda3/bin/python',
        '-m', 'pydeps',
        '-o', output,

        '-T', 'svg',  # default
        '--noshow',
        # '--display','IntelliJ IDEA'

        # Verbosity stuff
        # '-vvv',  # very verbose
        # '--show-deps',
        # '--show-raw-deps',
        # '--show-dot',

        # '--no-output',
        # '--show-cycles',
        # ' --noise-level INT',
        # '--max-bacon', '2',  # default,
        '--max-bacon', '3',  # default,

        '--pylib',
        # '--pylib-all',

        # '--include-missing',
        # --x PATTERN, --exclude PATTERN
        #  --xx MODULE, --exclude-exact MODULE
        #  --only MODULE_PATH
        '--cluster',
        '--min-cluster-size', '2',  # DEFAULT
        '--max-cluster-size', '10',  # DEFAULT
        # '--externals', #causes stuff to print but no svg
        # '--keep-target-cluster',
        # '--rmprefix PREFIX'
        # --reverse
        start
    ).interact()



