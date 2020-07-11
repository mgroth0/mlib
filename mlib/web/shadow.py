from dataclasses import dataclass
import os
import traceback

from pygments import highlight
from pygments.filter import simplefilter
from pygments.filters import CodeTagFilter, RaiseOnErrorTokenFilter
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer
from pygments.style import Style, StyleMeta
from pygments.token import Keyword, Name, Comment, String, Number, Token

from mlib.boot.mlog import warn
from mlib.boot.mutil import err
from mlib.fig.PlotData import makefig
from mlib.file import File, Folder, pwdf
from mlib.proj.struct import Project
from mlib.web.makereport_lib import write_webpage
from mlib.web.web import HTMLPage, Div, Hyperlink, HTML_P, Br, HTMLImage


class Dark(Style):
    default_style = '#FF0000'
    #: overall background color (``None`` means transparent)
    background_color = '#ffffff'
    #: highlight background color
    highlight_color = '#ffffcc'
    #: Style definitions for individual token types.
    styles = {
        # Comment      : 'italic #888',
        Keyword            : 'bold #6400EB',
        Name               : '#DCDDFF',
        Token.Name.Function: '#FF5EB5',
        Name.Class         : 'bold #9FEB4C',
        # String       : 'bg:#eee #111',
        String             : '#00FF00',
        # Error        : 'italic #888',
        Number             : 'italic #00EBAA',
        # Operator     : 'italic #888',
        # Generic      : 'italic #888'
        #     Text
        # Text.Whitespace
        # Other
        # Literal
        # Token.Literal.String
        # Token.Literal.Number
        # Operator
        # Punctuation
        Comment            : '#353535'
        # Generic
    }
Dark.__iter__ = StyleMeta.__iter__
Dark.style_for_token = StyleMeta.style_for_token

class CodeHtmlFormatter(HtmlFormatter):

    def wrap(self, source, outfile):
        """
        Wrap the ``source``, which is a generator yielding
        individual lines, in custom generators. See docstring
        for `format`. Can be overridden.
        """
        if self.wrapcode:
            return self._wrap_div(self._wrap_pre(self._wrap_code(source)))
        else:
            # default
            return self._wrap_div(self._wrap_pre(source))

    # not called by default since wrap_code is false
    def _wrap_code(self, source):
        yield 0, '<code>'
        # yield 0, ''
        for i, t in source:
            if i == 1:
                # it's a line of formatted code
                # t += '<br>'
                pass
            yield i, t
        # yield 0, ''
        yield 0, '</code>'

_FORMATTER = CodeHtmlFormatter(
    noclasses=True,
    nobackground=True,
    style=Dark()
)

# Token.Text
# Token.Keyword
# Token.Name.Function
# Token.Punctuation
# Token.Name.Builtin.Pseudo
# Token.Name
# Token.Operator

# noinspection PyUnusedLocal
@simplefilter
def uncolor(self, lexer, stream, options):
    for ttype, value in stream:
        if ttype is Token.Name.Function:
            pass
        elif ttype is Token.Name.Builtin:
            pass
            # ttype = Name
        yield ttype, value


# _LEXER = NumPyLexer()
_LEXER = PythonLexer()

_LEXER.add_filter(
    # cool, but will never run since I remove comments
    CodeTagFilter(codetags=["Todo", "TODO", "FixMe"])
)

_LEXER.add_filter(
    RaiseOnErrorTokenFilter()
)

_LEXER.add_filter(
    uncolor()
)

shadow_instances = []
class Shadow(HTMLPage):
    def __init__(self, mod_file=None, show=False):
        if mod_file is None:
            # use the caller's file
            ref = 0
            stack = traceback.extract_stack()
            mod_file = os.path.abspath(stack[-2 - ref][0])  # .split('.')[0]
            mod_file = File(mod_file)
        else:
            mod_file = File(mod_file)

        self.fig_folder = Folder(Project.FIGS_FOLDER[
                                     mod_file.rel_to(pwdf())
                                 ]).mkdirs()

        lines_of_code = File(mod_file.abspath).read().split('\n')
        html_objects = []
        started = False
        in_docstring = False

        @dataclass
        class ToHighlight:
            line: str
        for line in lines_of_code:
            if in_docstring:
                if line.strip().startswith('"') or line.strip().startswith("'"):
                    in_docstring = False
                elif started:
                    html_objects += [HTML_P(line.strip())]
            elif line.strip().startswith('# DOC:'):
                command = line.split(':')[1].strip()
                if command.upper() == 'START':
                    started = True
                elif command.upper() == 'LINK':
                    label, url = tuple(line.split(':', 2)[2].split(','))
                    html_objects += [Hyperlink(label, url)]
            elif started and line.strip().startswith('#'):
                html_objects += [line.strip().replace('#', '', 1).strip()]
            elif started and line.strip().startswith('"'):
                in_docstring = True
                html_objects += [HTML_P(line.replace('"""', "", 1).strip())]
            elif started and line.strip().startswith("'"):
                in_docstring = True
                html_objects += [HTML_P(line.replace("'''", "", 1).strip())]
            elif started:
                html_objects += [ToHighlight(line)]
        stored_lines = []
        real_html_os = []
        for o in html_objects:
            if isinstance(o, ToHighlight):
                stored_lines += [o.line]
            else:
                if len(stored_lines) > 0:
                    real_html_os += [highlight(
                        '\n'.join(stored_lines),
                        _LEXER,
                        _FORMATTER
                    )]
                    stored_lines.clear()
                real_html_os += [o]
        if len(stored_lines) > 0:
            real_html_os += [highlight(
                '\n'.join(stored_lines),
                _LEXER,
                _FORMATTER
            )]
        super().__init__(
            mod_file.rel_to(pwdf()).split('.')[0],
            Div(
                *real_html_os,
                # style='''
                # overflow: scroll;
                # height: 90vh;
                # '''
            ),
            show=show
        )
        shadow_instances.append(self)
        self._figs = []


    def fig(self, subplots):
        i = 1 + len(self._figs)
        file = self.fig_folder[f'{i}.png']
        self._figs.append(file)
        makefig(subplots, file=file)
        self.add(HTMLImage(file, fix_abs_path=True))



def HTMLIndex(*pages):
    for page in pages:
        num_parents = len(page.name.split('/')) - 1
        parents = '../' * num_parents
        page.children.append(Br)
        page.children.append(Hyperlink(
            'Back to Index',
            f'{parents}index.html',
            # style='position: fixed; bottom: 0;'
        ))
    for page in pages:
        write_webpage(
            page,
            Project.DOCS_FOLDER,
            # AutoHTMLImage, ???
            err('???'),
            Project.LOCAL_DOCS_FOLDER
        )
        if page.show: Project.LOCAL_DOCS_FOLDER[f'{page.name}.html'].open()

    return HTMLPage(
        'index',
        *[Hyperlink(page.name, f"{page.name}.html") for page in pages],
        HTMLImage(Project.PYCALL_FILE, fix_abs_path=True),
        HTMLImage(Project.PYDEPS_OUTPUT, fix_abs_path=True)
    )

def build_docs():
    index_page = HTMLIndex(*shadow_instances)
    index_page.show = True
    for page in shadow_instances:
        if page.show:
            if index_page.show is False:
                warn('cannot currently show multiple pages')
            index_page.show = False
    write_webpage(
        htmlDoc=index_page,
        root=Project.DOCS_FOLDER,
        resource_root_file=Project.RESOURCES_FOLDER
    )
    if index_page.show: Project.LOCAL_DOCS_FOLDER[f'{index_page.name}.html'].open()
