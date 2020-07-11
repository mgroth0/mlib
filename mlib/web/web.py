from abc import ABC, abstractmethod
from dataclasses import dataclass
import os

from mlib.boot.bootutil import isinstsafe, isdictsafe
from mlib.boot.mlog import err
from mlib.boot.mutil import isstr, listkeys, isblankstr, merge_overlapping
from mlib.boot.stream import listitems, listmap
from mlib.file import File
from mlib.web.js import JS

# Gutter icon linking to dark.css from ide-scripting would do well here
DARK_CSS = File(__file__).parent['dark.css'].read()

class HTMLPage:
    def __init__(
            self,
            name,
            *children,
            # stylesheet=DARK_CSS.name,
            stylesheet=DARK_CSS,
            style='',
            js='',
            show=False,
            jQuery=True,
            bodyStyle=None,
            bodyAttributes=None,
            identified=None
    ):
        if identified is None: identified = {}
        if bodyAttributes is None: bodyAttributes = {}
        if bodyStyle is None: bodyStyle = {}
        self.name = name
        self.children = list(children)
        self.stylesheet = stylesheet
        self.style = style
        self.show = show
        self.jQuery = jQuery
        self.js = js
        self.bodyStyle = bodyStyle
        self.bodyAttributes = bodyAttributes
        self.identified = identified



    def prepend(self, child): self.children.insert(0, child)
    def add(self, child): self.children.append(child)

    def getCode(
            self,
            resource_root,
            resource_root_rel
    ):
        ml = '<!DOCTYPE html>'

        # with Temp('temp.css') as f:
        #     f.write(self.style)
        head_objs = [
            '''<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">''',
            '<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">',
            HTMLCSSLink(href='style.css'),
            # StyleTag(lesscpy.compile(f.abspath, minify=True))
        ]

        if self.jQuery:
            head_objs.extend([
                ExternalScript(
                    src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"
                ),
                ExternalScript(src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"),
                HTMLCSSLink(
                    href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css")
            ])

        # head_objs.append(ExternalScript(
        # Blocked loading mixed active content
        #     src='http://cdn.jsdelivr.net/gh/bestiejs/platform.js/platform.js',
        # ))
        head_objs.extend(
            [
                ExternalScript(src='platform.js'),
                ExternalScript(src='mlib.js'),
                JScript(JS(self.js))
            ]
        )
        columnChildren = []
        for c in self.children:
            columnChildren.append(c)
            if isstr(c) or 'hidden' not in listkeys(c.attributes):
                columnChildren.append(Br)
        if columnChildren and columnChildren[-1] == Br:
            columnChildren = columnChildren[:-1]

        ml += HTMLRoot(
            HTMLHead(*head_objs),
            HTMLBody(
                *columnChildren,
                style=self.bodyStyle,
                **self.bodyAttributes,
                identified=self.identified
            ).getCode(resource_root, resource_root_rel)
        ).getCode(resource_root, resource_root_rel)

        return ml



class HTMLObject(ABC):
    # *args is unused for now, a placeholder
    def __init__(self, *args, **attributes):
        for k, v in listitems(attributes):
            if k == 'style' and isdictsafe(v):
                attributes[k] = CSS_Style_Attribute(**v)
        self.attributes = attributes
    @staticmethod
    @abstractmethod
    def tag(): pass
    @abstractmethod
    def contents(self, root_path, resource_root_rel): pass
    def _attributes(self, resource_root_path, resource_root_rel):
        a = ''
        for k, v in self.attributes.items():
            if k in ['onclick', 'onchange', 'onmouseover', 'onmouseout', 'onkeydown', 'onload']:
                err('JS pipeline not prepared for html even handlers')

            if v is None:
                a += f' {k}'
            elif isinstsafe(v, CSS_Style_Attribute):
                a += f' {k}="{repr(v)}"'
            elif isinstance(v, MagicLink.TempAbsPath) or not isblankstr(v):
                if isinstance(v, MagicLink.TempAbsPath):
                    v = merge_overlapping(resource_root_path, v.abs)
                elif isinstance(v, MagicLink.TempRelToResPath):
                    v = os.path.join(resource_root_rel, v.rel)
                a += f' {k}="{v}"'
        return a
    @staticmethod
    @abstractmethod
    def closingTag(): pass
    def getCode(self, root_path, resource_root_rel):
        return f'<{self.tag}{self._attributes(root_path, resource_root_rel)}>{self.contents(root_path, resource_root_rel)}{self.closingTag()}'
class HTMLParent(HTMLObject, ABC):
    def __init__(self, *args, **kwargs):
        objs = list(args)
        if 'identified' in kwargs:
            identified = kwargs['identified']
            del kwargs['identified']
            for id, ided in listitems(identified):
                ided.attributes['id'] = id
                objs.append(ided)
        super().__init__(**kwargs)
        self.objs = objs
    def closingTag(self): return f'</{self.tag}>'
    def contents(self, resource_root_path, resource_root_rel):
        ml = ''
        for o in self.objs: ml += o if isstr(o) else o.getCode(resource_root_path, resource_root_rel)
        return ml

    def extended(self, *objs):
        self.objs.extend(objs)
        return self
class HTMLChild(HTMLObject, ABC):
    def contents(self, resource_root, resource_root_rel): return ''
    def closingTag(self): return ''

class HTMLContainer(HTMLParent):
    tag = 'container'



class HTMLBody(HTMLParent):
    tag = 'body'
class HTMLHead(HTMLParent):
    tag = 'head'
class HTMLCSSLink(HTMLChild):
    def __init__(self, href):
        super().__init__(href=href, rel="stylesheet")
    tag = 'link'
class HTMLRoot(HTMLParent):
    def __init__(self, head, body):
        super().__init__(head, body)
    tag = 'html'

class Div(HTMLParent):
    tag = 'div'

class Span(HTMLParent):
    tag = 'span'

class Table(HTMLParent):
    tag = 'table'

class TableRow(HTMLParent):
    tag = 'tr'

class DataCell(HTMLParent):
    tag = 'td'

class HTML_P(HTMLParent):
    tag = 'p'

class HTMLSelect(HTMLParent):
    def __init__(self, values, *objs, **kwargs):
        super().__init__(*listmap(HTMLOption, values), *objs, **kwargs)
    tag = 'select'

class HTMLOption(HTMLParent):
    def __init__(self, value, *args, **kwargs):
        super().__init__(str(value), *args, value=value, **kwargs)
    tag = 'option'

class HTMLButton(HTMLParent):
    tag = 'button'

class StyleTag(HTMLParent):
    tag = 'style'

class TextArea(HTMLParent):
    def __init__(self, text='', **kwargs):
        super().__init__(text, **kwargs)
    tag = 'textarea'

class HTMLForm(HTMLParent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    tag = 'form'
class HTMLInput(HTMLChild):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    tag = 'input'
class HTMLInputSubmit(HTMLInput):
    def __init__(self, text, **kwargs):
        super().__init__(type="submit", value=text, **kwargs)
class HTMLDateInput(HTMLInput):
    def __init__(self, **kwargs):
        err('html date input doesnt work natively on safari and gets messy. make your own with Select')
        super().__init__(type="date", **kwargs)

class HTMLLabel(HTMLParent):
    def __init__(self, text, forr, *args, **kwargs):
        super().__init__(text, *args, **kwargs, **{'for': forr})
    tag = 'label'

class HTMLFigure(HTMLParent):
    tag = 'figure'

class HTMLFigCaption(HTMLParent):
    def __init__(self, label, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
    tag = 'figcaption'

class _Br(HTMLChild):
    tag = 'br'
Br = _Br()



class MagicLink:
    @dataclass
    class TempAbsPath:
        abs: str
        def __post_init__(self):
            if isinstsafe(self.abs, File):
                self.abs = self.abs.abspath
    @dataclass
    class TempRelToResPath:
        rel: str

class Hyperlink(HTMLParent, MagicLink):
    def __init__(self, label, url, *args, fix_path=False, **kwargs):
        if fix_path: url = self.TempAbsPath(url)
        super().__init__(label, *args, **kwargs, href=url)
    tag = 'a'
class HTMLImage(HTMLChild, MagicLink):
    def __init__(self, url, *args, fix_abs_path=False, fix_rel_to_res=False, **kwargs):
        assert not (fix_abs_path and fix_rel_to_res)

        if fix_abs_path: url = self.TempAbsPath(url)
        elif fix_rel_to_res: url = self.TempRelToResPath(url)

        super().__init__(*args, **kwargs, src=url, alt='an image', width=500)
        self.url = url
    tag = 'img'


class HTMLProgress(HTMLChild):
    def __init__(self, value, maxx, *args, **kwargs):
        super().__init__(*args, **kwargs, value=value, max=maxx)
    tag = 'progress'

class Script(HTMLParent, ABC):
    tag = 'script'
class JScript(Script):
    def __init__(self, js: JS, *args, **kwargs):
        assert isinstsafe(js, JS)
        super().__init__(f'\n{js.output()}\n', *args, **kwargs)
class ExternalScript(Script):
    def __init__(self, src: str, *args, **kwargs):
        super().__init__(*args, src=src, **kwargs)

class CSS_Style_Attribute:
    def __init__(self, **kwargs):
        self._style = kwargs
    def __repr__(self):
        s = ''
        for k, v in listitems(self._style):
            s += f'{k}: {v}; '
        return s


        # Hyperlink(
        #     label="Click here to automatically open a pre-filled email",
        #     url=f"mailto:mjgroth@mit.edu,dsinha@bbns.org?subject=SymTest{urllib.parse.quote(THIS_VERSION[0])}&",
        #     **{'class': 'center'},
        #     id='link',
        #     style={'display': 'none'}
        # ),

def arg_tags(**kwargs):
    return Div(
        *[HTML_P(
            str(v),
            id=str(k),
        ) for k, v in listitems(kwargs)],
        style={'display': 'none'}
    )
