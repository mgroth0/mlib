import functools
import os

# TODO: this and JS should really have a common base class
import lesscpy

from mlib.boot.lang import isinstsafe
from mlib.file import File, Temp

# Gutter icon linking to dark.css from ide-scripting would do well here
DARK_CSS = File(__file__).parent['dark.css'].read()
PIXEL_CSS = File(__file__).parent['pixel.css'].read()


class CSS:
    def __init__(self, css):
        if os.path.isfile(css):
            js = File(css)
        if isinstsafe(css, File):
            css = css.read()
        self._raw = css


    def __iadd__(self, other):
        self._raw += '\n'
        self._raw += '\n'
        self._raw += other
        return self

    def output(self):
        return self._compile()

    @functools.lru_cache()
    def _compile(self):
        inputs = self._raw

        with Temp('temp.css') as f:
            f.write(inputs)
            return lesscpy.compile(f.abspath, minify=False)
