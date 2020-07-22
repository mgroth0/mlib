import atexit

from pycallgraph import PyCallGraph, Config
from pycallgraph.output import GraphvizOutput

from mlib.boot import log
import mlib.file
from mlib.file import File
from mlib.inspect import all_superclasses, all_subclasses
from mlib.shell import shell
from mlib.str import StringExtension

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


def class_model_report(root_class):
    # because I can't find a good python plantUML library
    report = StringExtension('~~MY MODEL~~\n')
    report.append_by_lines()
    superclasses = all_superclasses(root_class)
    subclasses = all_subclasses(root_class)
    report += f'\troot:{root_class.__name__}'
    for s in superclasses:
        report += f'\t\tsuper :{s.__name__}'
    for s in subclasses:
        report += f'\t\tsub   :{s.__name__}'
    log(report)
    return report
