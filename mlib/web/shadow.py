from dataclasses import dataclass

from bs4 import BeautifulSoup
import matplotlib
from pygments import highlight

from mlib.bib import bib2html
from mlib.boot.lang import isstr, enum, listkeys, isblank
from mlib.boot.mlog import warn
from mlib.boot.stream import listmap, __, arr, listfilt
from mlib.fig.PlotData import makefig, PlotData
from mlib.file import File, Folder, pwdf
from mlib.inspect import caller_file, PythonLine, caller_lines
from mlib.proj.struct import Project
from mlib.pygments import LEXER, FORMATTER
from mlib.web.webpage import write_index_webpage, write_sub_webpage
from mlib.web.html import HTMLPage, Div, Hyperlink, Br, HTMLImage, H4, HR, Span, H3, html_tag_map

SHOW_INDEX = False
SHADOW_ONLINE = False
SHADOW_CACHE = Folder('_cache/shadow')
_tag_map = html_tag_map()
shadow_instances = []
import matplotlib.pyplot as plt
class Shadow(HTMLPage):

    def __getattr__(self, item):
        call_lines = caller_lines()
        if item in _tag_map:
            html_class = _tag_map[item]
            def make_and_add(*args, **kwargs):
                made = html_class(*args, **kwargs)
                self._add(made, call_lines)
            return make_and_add
        else:
            raise AttributeError

    def write_bib(self):
        assert self.bib is not None
        if self._empty_bib:
            self.bibdiv += H3(
                'References',
                style={'text-align': 'center'}
            )
        self.bibdiv += bib2html(self.bib)
        self._empty_bib = False
        self.to_skip += [caller_lines()[0]]


    def math(self, title, whatever):
        with self.next_im(caller_lines()) as f:
            matplotlib.rcParams['text.usetex'] = True
            with plt.style.context('dark_background'):
                plt.text(
                    x=0.5,
                    y=0.5,

                    # displaystyle makes summation things appear on top and bottom instead of right
                    s=r'$\displaystyle ' + whatever.strip() + '$',

                    fontdict={
                        'size': 30
                    },
                    ha='center',
                    va='center'
                )
                plt.axis('off')
                plt.title(title)
                plt.savefig(f.abspath)
                plt.clf()
            matplotlib.rcParams['text.usetex'] = False


    def fig(self, subplots, call_lines=None):
        if call_lines is None:
            call_lines = caller_lines()

        if call_lines[0] in self._called_fig_lines:
            return
        else:
            self._called_fig_lines.append(call_lines[0])
            with self.next_im(call_lines) as f:
                makefig(
                    subplots,
                    file=f,
                    width=4,
                    height=3
                )

    def plot(
            self,
            whatever,
            **kwargs
    ):
        self.fig(
            PlotData(
                item_type='line',
                y=whatever,
                **kwargs
            ),
            call_lines=caller_lines()
        )
    def link(
            self, label, url
    ):
        self._add((Div(  # link wont center without div
            Hyperlink(label, url, target='_blank'),
            style={'text-align': 'center', 'width': '100%'}
        ), Br), caller_lines())

    def _add(self, other, call_lines):
        self.catch_up(call_lines[0])
        self.write_source_buffer()
        self.div += other
        self.catch_up(call_lines[-1] + 1, skip=True)

    def __iadd__(self, other):
        self._add(other, caller_lines())
        return self

    def __init__(
            self,
            mod_file=None,
            show=False,
            analysis=None,
            include_index_link=True,
            bib=None,
            includes=(),
            **kwargs
    ):
        self._called_fig_lines = []
        self.include_index_link = include_index_link
        shadow_instances.append(self)
        self.includes = includes
        self.next_im_idx = 0
        self.bib = bib
        if self.bib is not None:
            self.bib = File(bib).load()

        self._empty_bib = True

        self.bibdiv = Div(

        )

        self.analysis = analysis
        mod_file = File(mod_file) if mod_file else caller_file()
        self.mod_file = mod_file
        if mod_file.parent.abspath == pwdf().abspath:
            assert not (pwdf()[pwdf().name].exists and pwdf()[pwdf().name].isdir)
            self.rootpath = pwdf().name
        else:
            self.rootpath = mod_file.parent[mod_file.name.replace('.py', '')].rel_to(pwdf())

        self.fig_folder = Folder(Project.FIGS_FOLDER[
                                     mod_file.rel_to(pwdf())
                                 ]).mkdirs()

        self.sr = self.source_reader()
        self.source_buffer = []
        self.div = Div()
        self.started = False
        self.to_skip = []
        self.in_docstring = False
        self.next_line_num = 1
        super().__init__(
            'index',
            self.div,
            show=show,
            js='''


var links = document.getElementsByTagName('a')
for (link of links) {
    if (link.getAttribute("href").startsWith("#")) {
        link.onclick = (e) => {
            link.scrollIntoView()
            return false
        }   
    }
} 


            ''',
            **kwargs
        )




    @dataclass
    class ToHighlight:
        line: PythonLine

    def next_im(self, call_lines):
        shad = self
        class ImageAdder:
            def __enter__(self):
                f = SHADOW_CACHE[f'{shad.rootpath}/image{shad.next_im_idx}.png']
                f.parent.mkdirs()
                return f
            def __exit__(self, exc_type, exc_val, exc_tb):
                shad._add_im(call_lines)
        return ImageAdder()

    def _add_im(self, call_lines):
        self.next_im_idx += 1
        i = self.next_im_idx - 1
        self._add(
            [Div(
                HTMLImage(
                    Project.SHADOW_RESOURCES[f'{self.rootpath}/image{i}.png'].rel_to(
                        Project.SHADOW_RESOURCES),
                    fix_rel_to_res=True,
                    style={
                        'width'  : '75%',
                        'display': 'block',  # center
                        'margin' : 'auto'  # center
                    }
                ),
                style={'width': '100%'}
            ), Br],
            call_lines
        )




    def process_line(self, line: PythonLine):
        # please deal with docstrings in proper sophisticated way with inspect or ast modules
        # if self.in_docstring:
        #     if line.startsdocstr:
        #         self.in_docstring = False
        #     elif self.started:
        #         return HTML_P(line.strip())
        #
        #
        if line.strip().startswith('# DOC:'):
            command = line.split(':')[1].strip()
            if command.upper() == 'START':
                self.started = True
            elif command.upper() == 'STOP':
                self.started = False
            # elif command.upper() == 'LINK':
            #     label, url = tuple(line.split(':', 2)[2].split(','))
            #     return Div(  # link wont center without div
            #         Hyperlink(label, url, target='_blank'),
            #         style={'text-align': 'center', 'width': '100%'}
            #     ), Br


        # elif self.started and line.iscomment:
        #     return line.strip().replace('#', '', 1).strip(), Br



        # elif self.started and line.startsdoubledocstr:
        #     self.in_docstring = True
        #     return HTML_P(line.replace('"""', "", 1).strip())
        # elif self.started and line.startssingledocstr:
        #     self.in_docstring = True
        #     return HTML_P(line.replace("'''", "", 1).strip())
        elif self.started and line.strip() not in _SKIPPED_SOURCE:
            return self.ToHighlight(line)

    def format_comment(self, contents):
        s = contents[0]
        new_contents = []
        thing = 'DOC:CITE['
        i = 0
        links = []
        keys = []
        while (i := s.find(thing, i)) >= 0:
            start = i + len(thing)
            after = s[start:]
            key = after.split(']')[0]
            keys.append(key)
            link_num = listkeys(self.bib).index(key) + 1
            links.append(Hyperlink(
                f'[{link_num}]', f'#{key}'
            ))

            i = start

        for link, key in zip(links, keys):
            to_replace = f'{thing}{key}]'
            # s = s.replace(to_replace, link.getCode(None, None), 1)
            before = s.split(to_replace)[0]
            splt = s.split(to_replace)
            s = splt[1] if len(splt) > 1 else ''
            if before != '':
                new_contents += [BeautifulSoup(Span(before).getCode(None, None), 'html.parser').contents[0]]
            new_contents += [BeautifulSoup(link.getCode(None, None), 'html.parser').contents[0]]
        if s != '':
            new_contents += [BeautifulSoup(Span(s).getCode(None, None), 'html.parser').contents[0]]
        return new_contents
    def source_reader(self):
        lines_of_code = File(self.mod_file.abspath).read().split('\n')

        for line_num, line in enum(listmap(PythonLine, lines_of_code)):
            self.next_line_num = line_num + 2
            yield self.process_line(line)

    def write_source_buffer(self):
        src = '\n'.join(listfilt(lambda s: not isblank(s), self.source_buffer))
        if not isblank(src):
            source_div = highlight(
                src,
                LEXER,
                FORMATTER
            )

            soup = BeautifulSoup(source_div, 'html.parser')

            for span in soup.find_all('span'):
                if 'style' in span.attrs and span.attrs['style'] == 'color: #353535':  # is comment
                    # add in-text citations
                    span.contents = self.format_comment(span.contents)

                if span.string in _FUN_LINKS:
                    span.contents = BeautifulSoup(Hyperlink(
                        span.string, _FUN_LINKS[span.string], target='_blank'
                    ).getCode(None, None), 'html.parser')

            self.div += soup.prettify()
        self.source_buffer.clear()

    def catch_up(self, stop_at=None, skip=False):
        while stop_at is None or stop_at > self.next_line_num:
            try:
                o = next(self.sr)
            except StopIteration:
                break
            this_line = self.next_line_num - 1
            skip_line = this_line in self.to_skip
            if o is None: continue
            if isinstance(o, self.ToHighlight):
                if not (skip or skip_line): self.source_buffer += [o.line]
            else:
                if len(self.source_buffer) > 0:
                    self.write_source_buffer()
                if not (skip or skip_line): self.div += o

        if stop_at is None and len(self.source_buffer) > 0 and not skip:
            self.write_source_buffer()










def ShadowIndex(*pages):
    return HTMLPage(
        'index',
        *[Hyperlink(page.rootpath, f"{page.rootpath}/{page.name}.html") for page in pages],
        HTMLImage(Project.PYCALL_FILE, fix_abs_path=True),
        HTMLImage(Project.PYDEPS_OUTPUT, fix_abs_path=True)
    )




def build_docs():
    Project.SHADOW_RESOURCES.deleteIfExists()
    if SHADOW_CACHE:
        SHADOW_CACHE.copy_to(Project.SHADOW_RESOURCES)

    index_page = ShadowIndex(*shadow_instances)
    index_page.show = SHOW_INDEX

    if SHOW_INDEX:
        for page in shadow_instances:
            if page.show:
                if index_page.show is False:
                    warn('cannot currently show multiple pages')
                index_page.show = False

    write_index_webpage(
        htmlDoc=index_page,
        root=Project.DOCS_FOLDER,
        resource_root_file=Project.RESOURCES_FOLDER,
        upload_resources=SHADOW_ONLINE,
        WOLFRAM=SHADOW_ONLINE,
        DEV=False
    )

    assert len(set(listmap(__.rootpath, shadow_instances))) == len(shadow_instances)

    first_cell = True
    for page in shadow_instances:
        page.catch_up()  # in separate loop bc subs

        page += page.bibdiv

    for page in shadow_instances:
        for sub in page.includes:
            if isstr(sub):
                sub = arr(shadow_instances).first(
                    lambda shad: shad.rootpath == sub
                        .replace('..', 'TEMPDOTDOT')
                        .replace('.', '/')
                        .replace('TEMPDOTDOT', '..')
                )
            assert not sub.includes
            # sub += sub.bibdiv
            for c in sub.children:
                page.children.append(c)

        if page.analysis:
            for cel in page.analysis.cells:
                if not first_cell:
                    page.add(HR())
                first_cell = False

                page.add(H4(cel.__name__))
                if cel.shadow_cache_im(page.analysis):
                    cel.shadow_cache_im(page.analysis).copy_into(Project.RESOURCES_FOLDER)
                if cel.shadow_cache(page.analysis):
                    page.add(cel.shadow_cache(page.analysis).load())

        if page.include_index_link:
            page.children.append(Br)
            page.children.append(Hyperlink(
                'Back to Index',
                Project.DOCS_FOLDER['index.html'].rel_to(
                    Project.DOCS_FOLDER[page.rootpath]
                )
            ))
        write_sub_webpage(
            htmlDoc=page,
            index_root=Project.DOCS_FOLDER,
            rel_root=page.rootpath,
            rel_resource_root=Project.RESOURCES_FOLDER.rel_to(Project.DOCS_FOLDER),
            upload_resources=SHADOW_ONLINE,
            WOLFRAM=SHADOW_ONLINE,
            DEV=False,
        )
    if Project.RESOURCES_FOLDER:
        Project.RESOURCES_FOLDER.copy_to(
            Project.DOCS_FOLDER.edition_local[
                Project.RESOURCES_FOLDER.rel_to(Project.DOCS_FOLDER)
            ]
        )
    if Project.SHADOW_RESOURCES:
        assert not Project.RESOURCES_FOLDER
        Project.SHADOW_RESOURCES.copy_to(
            Project.DOCS_FOLDER.edition_local[
                Project.RESOURCES_FOLDER.rel_to(Project.DOCS_FOLDER)
            ]
        )
        Project.SHADOW_RESOURCES.copy_to(
            Project.DOCS_FOLDER[
                Project.RESOURCES_FOLDER.rel_to(Project.DOCS_FOLDER)
            ]
        )



_SKIPPED_SOURCE = [
    '@log_invokation',
    'global DOC',
    '@staticmethod'
]


# doesnt work because scipy exports functions from parent modules (scipy.signal instea of the real module, scipy.signal.signaltools)
# def scipy_doc_url(fun): return f'https://docs.scipy.org/doc/scipy/reference/generated/{mn(fun)}.{fun.__name__}.html'

def scipy_doc_url(funname): return f'https://docs.scipy.org/doc/scipy/reference/generated/{funname}.html'

_FUN_LINKS = {
    'bilinear': 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.bilinear.html'
}
_FUN_LINKS.update(
    {fun.split('.')[-1]: scipy_doc_url(fun) for fun in [
        'scipy.signal.filtfilt',
        'scipy.signal.lfilter',
        'scipy.signal.butter'
    ]}
)
