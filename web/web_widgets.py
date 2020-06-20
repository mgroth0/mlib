from mlib.web.web import *
from mlib.wolf.wolfpy import WOLFRAM
from mlib.boot.mutil import File

def FigureTable(*figs_captions, apiURL=None, exp_id=None, editable=False):
    children = []
    for fig, caption in figs_captions:
        the_id = f'{exp_id}.{".".join(File(fig).names(keepExtension=False)[-1:])}'
        log(f'creating figure: {the_id}')
        children.append(
            TableRow(
                DataCell(
                    HTMLImage(WOLFRAM.push_file(fig)[0])
                )
                , DataCell(
                    P(caption, id=the_id) if not editable else TextArea(caption, id=the_id, clazz='textcell'),
                    clazz='parentcell')
            )
        )
    return Table(*children)
