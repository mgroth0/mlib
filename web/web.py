from abc import ABC, abstractmethod

from mlib.boot.mlog import log
from mlib.boot.mutil import isstr
DARK_CSS = '''
body {
    background:black;
    color: white;
}
 .center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
  text-align: center;
}
.pixel {
    image-rendering: optimizeSpeed;             /* Older versions of FF */
    image-rendering: -moz-crisp-edges;          /* FF 6.0+ */
    image-rendering: -webkit-optimize-contrast; /* Webkit (non standard naming) */
    image-rendering: -o-crisp-edges;            /* OS X & Windows Opera (12.02+) */
    image-rendering: crisp-edges;               /* Possible future browsers. */
    -ms-interpolation-mode: nearest-neighbor;   /* IE (non standard naming) */
}
.textcell {
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}
.parentcell {
position:relative;
width:100%;
}
'''


class HTML:
    def __init__(self,
                 *children,
                 # stylesheet=DARK_CSS.name,
                 stylesheet=DARK_CSS,
                 js=''
                 ):
        self.children = children
        self.stylesheet = stylesheet
        self.js = js
    def getCode(self):
        log('getting HTML code for HTML doc')
        ml = '<!DOCTYPE html>'
        ml += '<html>'
        ml += '<head>'
        ml += '<link rel="stylesheet" href="'
        ml += 'style.css'
        # ml += self.stylesheet
        ml += '">'
        ml += """
        
        <script>
        """
        # probably from syntax highlight injection
        ml += self.js.replace('\u200b', '')
        ml += """
        </script>
        
        """
        ml += '</head>'
        ml += HTMLBody(*self.children).getCode()
        ml += '</html>'
        return ml

class HTMLObject(ABC):
    def __init__(self, style='', clazz='', id=None):
        self.style = style
        self.clazz = clazz
        self.id = id
    @staticmethod
    @abstractmethod
    def tag():
        pass

    @abstractmethod
    def contents(self):
        pass

    @abstractmethod
    def attributes(self):
        pass

    def _attributes(self):
        atts = self.attributes()
        if self.id is not None:
            atts = atts + ' id="' + self.id + '"'
        if atts:
            return ' ' + atts
        else:
            return ''

    @staticmethod
    @abstractmethod
    def closingTag():
        pass

    def _class(self):
        if self.clazz:
            return ' class="' + self.clazz + '"'
        else:
            return ''

    def _style(self):
        if self.style:
            return ' style="' + self.style + '"'
        else:
            return ''

    def getCode(
            self):
        return '<' + self.tag() + self._class() + self._style() + self._attributes() + '>' + self.contents() + self.closingTag()

class HTMLContainer(HTMLObject):
    def __init__(self, *args, **kwargs):
        super(HTMLContainer, self).__init__(**kwargs)
        self.objs = args

    def closingTag(self):
        return '</' + self.tag() + '>'

    @staticmethod
    @abstractmethod
    def sep():
        pass

    def contents(self):
        ml = ''
        for o in self.objs:
            if isstr(o):
                ml += o
            else:
                ml += o.getCode()
            if isstr(o) or 'hidden' not in o.attributes():
                ml += self.sep()
        return ml

class HTMLVar(HTMLContainer):
    def __init__(self, id, var):
        super(HTMLVar, self).__init__(var, id=id)
    def attributes(self): return 'hidden'
    @staticmethod
    def tag(): return 'p'
    @staticmethod
    def sep(): return ''

class HTMLBody(HTMLContainer):
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'body'
    @staticmethod
    def sep(): return '<br>'



class Div(HTMLContainer):
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'div'
    @staticmethod
    def sep(): return ''

class Span(HTMLContainer):
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'span'
    @staticmethod
    def sep(): return ''

class Table(HTMLContainer):
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'table'
    @staticmethod
    def sep(): return ''

class TableRow(HTMLContainer):
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'tr'
    @staticmethod
    def sep(): return ''

class DataCell(HTMLContainer):
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'td'
    @staticmethod
    def sep(): return ''

class P(HTMLContainer):
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'p'
    @staticmethod
    def sep(): return ''

class TextArea(HTMLContainer):
    def __init__(self, text='', **kwargs):
        super(TextArea, self).__init__(text, **kwargs)
        self.text = text
    def attributes(self): return ''
    @staticmethod
    def tag(): return 'textarea'
    @staticmethod
    def sep(): return ''

class Hyperlink(HTMLContainer):
    def __init__(self, label, url, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.url = url
    @staticmethod
    def tag(): return 'a'
    @staticmethod
    def sep(): return ''
    def attributes(self): return f'href="{self.url}"'

class HTMLLabel(HTMLContainer):
    def __init__(self, label, forr, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.forr = forr
    @staticmethod
    def tag(): return 'label'
    @staticmethod
    def sep(): return ''
    def attributes(self): return f'for="{self.forr}"'

class HTMLFigure(HTMLContainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    @staticmethod
    def tag(): return 'figure'
    @staticmethod
    def sep(): return ''
    def attributes(self): return ''

class HTMLFigCaption(HTMLContainer):
    def __init__(self, label, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.label = label
    @staticmethod
    def tag(): return 'figcaption'
    @staticmethod
    def sep(): return ''
    def attributes(self): return ''

class HTMLChild(HTMLObject, ABC):
    def contents(self): return ''
    def closingTag(self): return ''

class _Br(HTMLChild):
    @staticmethod
    def tag():
        return 'br'
    def attributes(self):
        return ''
Br = _Br()



class HTMLImage(HTMLChild):
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
    @staticmethod
    def tag(): return 'img'
    def attributes(self): return f'src="{self.url}" alt="an image" width="500"'

class HTMLProgress(HTMLChild):
    def __init__(self, value, maxx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.maxx = maxx
    @staticmethod
    def tag(): return 'progress'
    def attributes(self): return f'value="{self.value}" max="{self.maxx}"'
