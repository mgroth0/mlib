from pybtex.database import parse_string

from mlib.boot.stream import listitems
from mlib.web.html import Div, Br, Hyperlink



def bib2html(bibliography, id_use_order=(), exclude_fields=None):
    exclude_fields = exclude_fields or []
    if exclude_fields:

        bibliography = parse_string(bibliography.to_string('bibtex'), 'bibtex')

        for entry in bibliography.entries.values():

            for ef in exclude_fields:
                if ef in entry.fields.__dict__['_dict']:
                    del entry.fields.__dict__['_dict'][ef]

    # return old_format(bibliography)
    return new_format(bibliography, id_use_order)


# trying to make almost-perfect Nature formatter
# definitely allowing myself some creative liberties though too
# https://paperpile.com/s/nature-citation-style/
def new_format(bibliography, id_use_order):
    bibdiv = Div()
    num = 0
    for entry_id, entry in listitems(bibliography):
        num += 1
        entrydiv = Div(id=entry_id)
        entrydiv += (str(num) + '.  ' + _format_entry(entry))

        # unconventional
        entrydiv += ' ('
        entrydiv += Hyperlink('link', entry['murl'], target='_blank')
        entrydiv += ')'

        bibdiv += entrydiv
        bibdiv += Br
    return bibdiv

def _format_entry(entry):
    entrystr = ''

    entrystr += _format_names(entry['authors'])
    entrystr += ' ' + entry['title'] + '.'
    if 'volume' in entry:
        entrystr += f' <b>{entry["volume"]}</b>,'
    if 'pages' in entry:
        pages = entry['pages'].split('--')
        entrystr += f' {pages[0]}-{pages[1]}'
    entrystr += f' ({entry["publisher"]}, {entry["year"]})'
    if 'version' in entry:
        entrystr += f' (Version {entry["version"]})'
    return entrystr

def _format_names(authors):
    if len(authors) >= 6:
        return _format_name(authors[0]) + ' et al.'
    elif len(authors) > 1:
        last = _format_name(authors[-1])
        rest = ', '.join([_format_name(a) for a in authors[0:-1]])
        return rest + ' & ' + last
    else:
        return _format_name(authors[0])

def _format_name(author):
    return author['last'] + ', ' + author['first'][0].upper() + '.'
