# idea is that it could auto format on edits but not sure how to implement this. example: trailing newlines or strip
from collections import UserString
import json
from urllib.parse import urlencode

from mlib.boot.lang import cn, isdict
from mlib.boot.mlog import err
from mlib.boot.stream import listitems, insertZeros
class FormattedString(UserString):
    pass




# overlap should be at the end of s1 and beginning of s2
# @log_invokation
def merge_overlapping(s1, s2):
    final = None
    for i in range(1, len(s1)):
        substr = s1[-i:]
        if substr in s2:
            final = substr
        else:
            break
    assert i >= 1
    assert final is not None, f'could not merge:{s1=}{s2=}'
    return s1.replace(final, '') + s2


def de_quote(s):
    err('consider using eval to also fix escaped characters')
    return s[1:-1]

def query_url(url, arg_dict): return f'{url}?{urlencode(arg_dict)}'



class StringExtension(str, UserString):
    def afterfirst(self, c):
        return StringExtension(self.split(c, 1)[1])
    def beforefirst(self, c):
        return StringExtension(self.split(c, 1)[0])
    def append_by_lines(self):
        def newiadd(slf, other):
            slf.data = self.data + other + '\n'
        self.__iadd__ = newiadd
    def r(self, d):
        s = self
        for k, v in listitems(d):
            s = s.replace(k, v)
        return s
stre = StringExtension



# doesnt really work. Just use <pre>.
def fix_html_whitespace(s):
    return s.replace('\t', '&#9;').replace('\n', '<br>').replace(' ', '&nbsp')




PDT = 'PREVIEW_DICT_TOKEN'
def preview_dict_recurse(d, depth=1):
    pd = PDT + cn({}) + PDT
    if depth > 0:
        pd = {}
        for k, v in listitems(d):
            if isdict(v):
                pd[k] = preview_dict_recurse(v, depth - 1)
            else:
                pd[k] = PDT + cn(v) + PDT
    return pd
def preview_dict(d, depth=1):
    pd = preview_dict_recurse(d, depth)
    pd = json.dumps(pd, indent=2)
    pd = pd.replace(f'"{PDT}', '')
    pd = pd.replace(f'{PDT}"', '')
    return pd





def lengthen_str(s, minlen):
    s = str(s)
    if len(s) >= minlen:
        return s
    else:
        return s + ' ' * (minlen - len(s))

def min_sec_form(dur_secs):
    mins, secs = divmod(dur_secs, 60)
    secs = round(secs)
    # secs = f'0{secs}' if secs < 10 else secs
    return f'{round(mins)}:{insertZeros(secs, 2)}'

def shorten_str(s, maxlen):
    s = str(s)
    if len(s) <= maxlen:
        return s
    else:
        return s[0:maxlen]



def utf_decode(s, nonesafe=False):
    if nonesafe and s is None:
        return str(s)
    return s.decode('utf-8')
