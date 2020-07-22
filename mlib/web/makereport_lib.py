from mlib.boot import log
from mlib.boot.lang import istuple
from mlib.file import File, is_file
from mlib.term import MagicTermLineLogger
from mlib.web.html import Table, Script, TextArea, HTML_P, DataCell, HTMLImage, TableRow



def FigureTable(*figs_captions, resources_root=None, exp_id=None, editable=False):
    children = [Script(js='''hotElements=[]''')]
    my_stacker = MagicTermLineLogger(FigureTable)
    for maybe_pair in [f for f in figs_captions if f]:
        was_tuple = istuple(maybe_pair)
        if was_tuple:
            fig, caption = maybe_pair
        else:
            fig = maybe_pair
            caption = None
        if is_file(fig):
            if not fig: continue
            fig = File(fig).copy_into(resources_root, overwrite=True)
            fig = HTMLImage(fig.abspath, fix_abs_path=True)
        if not caption:
            children.append(fig)
        else:
            # the_id = f'{exp_id}.{".".join(File(fig).names(keepExtension=False)[-1:])}'
            the_id = f'{exp_id}.{".".join(File(fig).names(keepExtension=False)[-1:])}'
            log(f'creating figure: {the_id}', stacker=my_stacker)
            children.append(
                TableRow(
                    DataCell(fig),
                    DataCell(
                        HTML_P(
                            caption,
                            id=the_id,
                        ) if not editable else TextArea(
                            caption,
                            id=the_id,
                            **{'class': 'textcell'}
                        ),
                        Script(js='''(() => {hotElements.push(document.currentScript.parentNode.childNodes[0])})()'''
                               ),
                        **{'class': 'parentcell'},
                    )
                )
            )
    my_stacker.done = True
    return Table(
        *children,
        Script(js='''
   onload_funs.push(() => {
       hotElements.forEach((e)=>{
            original_value = apiGET(e.id).de_quote()
            e.setText(original_value)
            if (e.tagName === 'TEXTAREA') {
                $(e).on('input',  _=> {
                    apiFun(e.id,e.value)
                })
            }
        }
    )})
        ''')
    )

DNN_REPORT_CSS = '''
.textcell {
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.parentcell {
    position: relative;
    width: 100%;
}

'''
