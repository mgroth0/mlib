from pybtex.database import Entry
from pybtex.plugin import find_plugin
from pybtex.richtext import Text, Tag
from pybtex.style.formatting import BaseStyle
from pybtex.style.template import join, FieldIsMissing

APA = find_plugin('pybtex.style.formatting', 'apa')()
HTML = find_plugin('pybtex.backends', 'html')()
def old_format(bibliography):
    # formattedBib = APA.format_bibliography(bibliography)
    formattedBib = NatureAttempt().format_bibliography(bibliography)
    return '<br>'.join(entry.text.render(HTML) for entry in formattedBib)
class NatureAttempt(BaseStyle):

    def __init__(self):
        super().__init__(
            abbreviate_names=True
        )

    def _format_default(self, entry):
        entry: Entry = entry['entry']
        names = []
        for p in entry.persons['author']:
            names.append(self.format_name(p, self.abbreviate_names))
        names = join(sep=', ', last_sep=', … ')[names].format_data(None)
        return Text(
            # 'Article ',
            # self.format_names('author'),
            names,
            # entry.fields['author'],
            ' ',
            Tag('em', entry.fields['title'])
        )

    def format_software(self, entry):
        return self._format_default(entry)
    def format_inproceedings(self, entry):
        return self._format_default(entry)
    def format_article(self, entry):
        return self._format_default(entry)





def apa_names(children, context, role, **kwargs):
    """
    Returns formatted names as an APA compliant reference list citation.
    """
    assert not children

    try:
        persons = context['entry'].persons[role]
    except KeyError:
        raise FieldIsMissing(role, context['entry'])

    style = context['style']

    if len(persons) > 7:
        persons = persons[:6] + persons[-1:]
        formatted_names = [style.format_name(
            person, style.abbreviate_names) for person in persons]
        return join(sep=', ', last_sep=', … ')[
            formatted_names].format_data(context)
    else:
        formatted_names = [style.format_name(
            person, style.abbreviate_names) for person in persons]
        return join(sep=', ', sep2=', & ', last_sep=', & ')[
            formatted_names].format_data(context)
