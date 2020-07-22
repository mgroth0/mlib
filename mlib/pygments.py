from pygments.filter import simplefilter
from pygments.filters import CodeTagFilter, RaiseOnErrorTokenFilter
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer
from pygments.style import Style, StyleMeta
from pygments.token import Keyword, Name, Token, String, Number, Comment



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

    def __init__(self, *args, wrap_fun_links=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrap_fun_links = wrap_fun_links

    def wrap(self, source, outfile):
        """
        Wrap the ``source``, which is a generator yielding
        individual lines, in custom generators. See docstring
        for `format`. Can be overridden.
        """

        if self.wrap_fun_links:
            source = self._wrap_fun_links(source)

        if self.wrapcode:  # default false
            source = self._wrap_code(source)

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

    def _wrap_fun_links(self, source):
        # nah, doing this in shadow
        # yield 0, '<code>'
        # yield 0, ''
        for i, t in source:
            if i == 1:
                # it's a line of formatted code
                # t += '<br>'
                pass
            yield i, t
        # yield 0, ''
        # yield 0, '</code>'

FORMATTER = CodeHtmlFormatter(
    noclasses=True,
    nobackground=True,
    wrap_fun_links=True,
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
LEXER = PythonLexer()

LEXER.add_filter(
    # cool, but will never run since I remove comments
    CodeTagFilter(codetags=["Todo", "TODO", "FixMe"])
)

LEXER.add_filter(
    RaiseOnErrorTokenFilter()
)

LEXER.add_filter(
    uncolor()
)
