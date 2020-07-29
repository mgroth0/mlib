from abc import ABC, abstractmethod
from dataclasses import dataclass
import inspect
import os

from mlib.boot.dicts import CaseInsensitiveDict
from mlib.boot.lang import isinstsafe, isstr, listkeys, isdictsafe, isblankstr, is_non_str_itr
from mlib.boot.mlog import err, warn
from mlib.boot.stream import listitems, listmap
from mlib.file import File
from mlib.inspect import all_subclasses
from mlib.str import merge_overlapping
from mlib.web.css import DARK_CSS, TABS_CSS
from mlib.web.js import JS
from mlib.web.soup import soup

class HTMLPage:
    def __init__(
            self,
            name,
            *children,
            stylesheet=DARK_CSS + "\n" + TABS_CSS,
            style='',
            js='',
            show=False,
            jQuery=True,
            bodyStyle=None,
            bodyAttributes=None,
            identified=None,
            CDNs=()
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
        self.CDNs = CDNs
        self._tab = None
        self._tabpane = None
        self._tabcontent_container = None
        self.javascript_files = ['platform.js', 'mlib.coffee', 'mplotly.coffee']



    def prepend(self, child): self.children.insert(0, child)
    def add(self, child):
        self.children.append(child)


    def addTab(self, name, content):
        if self._tab is None:
            self._tabpane = Div(
                **{'class': 'tabpane'}
            )
            self._tab = Tab(
                **{'class': 'tab'}
            )
            self._tabcontent_container = Div(
                **{'class': 'tabcontent_container'}
            )
            self._tabpane += self._tab
            self._tabpane += self._tabcontent_container
            self += self._tabpane
        self._tab += HTMLButton(
            name,
            **{
                'class'  : 'tablinks',
                'onclick': f'openTab(event,\'{name}\')'  # strs must be single quoted
            }
        )
        self._tabcontent_container += Div(
            content,
            id=name,
            **{'class': 'tabcontent', 'style': "display:none;"}
        )



    def __iadd__(self, other):
        if is_non_str_itr(other):
            for o in other:
                self.add(o)
        else:
            self.add(other)
        return self

    def getCode(
            self,
            resource_root,
            resource_root_rel,
            force_fix_to_abs=False
    ):
        ml = '<!DOCTYPE html>'

        # with Temp('temp.css') as f:
        #     f.write(self.style)
        head_objs = [
            '''<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">''',
            '<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">',
            HTMLCSSLink(href='style.css'),
            StyleTag(self.style)
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

        for cdn in self.CDNs:
            head_objs.append(ExternalScript(cdn))

        # head_objs.append(ExternalScript(
        # Blocked loading mixed active content
        #     src='http://cdn.jsdelivr.net/gh/bestiejs/platform.js/platform.js',
        # ))

        head_objs.extend(
            listmap(lambda x: ExternalScript(src=x.replace('.coffee', '.js')), self.javascript_files) +
            [
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
            ).getCode(resource_root, resource_root_rel, force_fix_to_abs)
        ).getCode(resource_root, resource_root_rel, force_fix_to_abs)

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
    def contents(self, root_path, resource_root_rel, force_fix_to_abs): pass
    def _attributes(self, resource_root_path, resource_root_rel, force_fix_to_abs):
        a = ''
        for k, v in self.attributes.items():
            if k in ['onclick', 'onchange', 'onmouseover', 'onmouseout', 'onkeydown', 'onload']:
                # not sure why i cared so much to make this an err before
                warn('JS pipeline not prepared for html even handlers')

            if v is None:
                a += f' {k}'
            elif isinstsafe(v, CSS_Style_Attribute):
                a += f' {k}="{repr(v)}"'
            elif isinstance(v, MagicLink.TempAbsPath) or not isblankstr(v):
                if isinstance(v, MagicLink.TempAbsPath):
                    if force_fix_to_abs:
                        v = merge_overlapping(resource_root_path, v.abs)
                    else:
                        v = merge_overlapping(resource_root_path, v.abs)
                elif isinstance(v, MagicLink.TempRelToResPath):
                    if force_fix_to_abs:
                        v = merge_overlapping(resource_root_path, v.rel)
                    else:
                        v = os.path.join(resource_root_rel, v.rel)
                a += f' {k}="{v}"'
        return a
    @staticmethod
    @abstractmethod
    def closingTag(): pass
    def soup(self):
        return soup(self.getCode(None, None))
    def getCode(self, root_path, resource_root_rel, force_fix_to_abs=False):
        return f'<{self.tag}{self._attributes(root_path, resource_root_rel, force_fix_to_abs)}>{self.contents(root_path, resource_root_rel, force_fix_to_abs)}{self.closingTag()}'
class HTMLParent(HTMLObject, ABC):
    def __init__(self, *args, **kwargs):
        objs = list(args)
        if 'identified' in kwargs:
            identified = kwargs['identified']
            del kwargs['identified']
            for idd, ided in listitems(identified):
                ided.attributes['id'] = idd
                objs.append(ided)
        super().__init__(**kwargs)
        self.objs = objs

    def __iadd__(self, other):
        if is_non_str_itr(other):
            for o in other:
                self.objs.append(o)
        else:
            self.objs.append(other)
        return self


    def closingTag(self): return f'</{self.tag}>'
    def contents(self, resource_root_path, resource_root_rel, force_fix_to_abs):
        ml = ''
        for o in self.objs: ml += o if isstr(o) else o.getCode(resource_root_path, resource_root_rel, force_fix_to_abs)
        return ml

    def extended(self, *objs):
        self.objs.extend(objs)
        return self
class HTMLChild(HTMLObject, ABC):
    def contents(self, resource_root, resource_root_rel, force_fix_to_abs): return ''
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

class H1(HTMLParent): tag = 'h1'
class H2(HTMLParent): tag = 'h2'
class H3(HTMLParent): tag = 'h3'
class H4(HTMLParent): tag = 'h4'
class H5(HTMLParent): tag = 'h5'
class H6(HTMLParent): tag = 'h6'


class Table(HTMLParent):
    tag = 'table'

class TableRow(HTMLParent):
    tag = 'tr'

class DataCell(HTMLParent):
    tag = 'td'

class HTML_Pre(HTMLParent):
    tag = 'pre'

class HR(HTMLParent): tag = 'hr'

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
                self.abs: File
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
    def __init__(self, url, *args, fix_abs_path=False, fix_rel_to_res=False, width=500, **kwargs):
        assert not (fix_abs_path and fix_rel_to_res)

        if fix_abs_path: url = self.TempAbsPath(url)
        elif fix_rel_to_res: url = self.TempRelToResPath(url)

        super().__init__(*args, **kwargs, src=url, alt='an image', width=width)
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

def html_tag_map():
    HTML_TAG_MAP = CaseInsensitiveDict()
    for sub in all_subclasses(HTMLObject):
        if not inspect.isabstract(sub):
            HTML_TAG_MAP[sub.tag] = sub
    return HTML_TAG_MAP


class Tab(HTMLParent): tag = 'tab'
