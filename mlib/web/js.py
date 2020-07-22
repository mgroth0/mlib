import functools
import os

from mlib.boot.lang import isinstsafe
from mlib.boot.stream import arr, enum
from mlib.file import File, Temp
from mlib.shell import shell

# TODO: should really inherit a common base class with CSS
class JS:

    def __init__(self, js, onload=True):
        if os.path.isfile(js):
            js = File(js)
        if isinstsafe(js, File):
            js = File(js.abspath.replace('.coffee', '.js'))
            js = js.read()
        self._raw = js
        self._onload = onload

    def output(self):
        if self._onload:
            return self._wrap_in_onload()
        else:
            return self._mark()

    @functools.lru_cache()
    def _process_includes(self):
        inputs = self._raw

        lines = inputs.split('\n')
        includes = []
        for idx, line in enum(lines):
            if 'INCLUDE' in line:
                new_js = JS(line.split(':')[1].replace('"', '').replace("'", '').strip())._process_includes()
                includes.append((idx, new_js))
        for i in includes:
            # lines will now be multiline strings
            lines[i[0]] = i[1]
        return '\n'.join(lines)

    @functools.lru_cache()
    def _fix(self):
        # probably from syntax highlight injection
        inputs = self._process_includes()
        return inputs.replace('\u200b', '')

    @functools.lru_cache()
    def _remove_source_maps(self):
        inputs = self._fix()

        return arr(inputs.split('\n')).filtered(
            lambda l: 'sourceMappingURL' not in l
        ).join('\n')

    def _mark(self):
        inputs = self._remove_source_maps()
        return '\t\t\t//GEN\n'.join(inputs.split('\n'))


    def _wrap_in_onload(self):
        inputs = self._mark()
        return '''
        onload_funs.push( () => {
            "CODE"
        })
        '''.replace('"CODE"', inputs)


def compile_coffeescript(cs) -> str:
    #  '--map'
    # '--compile'
    # '--print'
    with Temp('temp.coffee', w=cs) as f:
        with Temp('temp.js', w='') as ff:
            p = shell(['/usr/local/bin/coffee', '-b', '-o', ff.abspath, '--compile', f.abspath])
            p.interact()
            return ff.read()
