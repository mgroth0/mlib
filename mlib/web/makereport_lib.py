import os

from mlib.boot import log
from mlib.file import url, pwdf, File
from mlib.proj.struct import Project
from mlib.term import greens, MagicTermLineLogger
# @log_invokation(with_args=True)
from mlib.web.web import HTMLPage, Table, Script, TextArea, HTML_P, DataCell, HTMLImage, TableRow
def write_webpage(
        htmlDoc: HTMLPage,
        root,
        resource_root_file,
        upload_resources=True,
        WOLFRAM=False,
        DEV=False,

):
    resource_root_rel = File(resource_root_file).rel_to(root)

    # assert not (resource_root_file and upload_resources)
    # resource_root_url = resource_root_file if isstr(resource_root_file) else resource_root_file.wcurl
    # resource_root_url_local = resource_root_file if isstr(resource_root_file) else resource_root_file.wcurl
    r = f'\n~~Created Webpage: {htmlDoc.name}~~\n'
    title = r
    if WOLFRAM:
        if upload_resources:
            resource_root_file.wc.push_public()
        if DEV:
            root.edition_wolf_dev.make_webpage(htmlDoc, resource_root_file.wcurl, resource_root_rel)
            root.edition_wolf_dev.wc.push()
            r += f'\tPrivate:{root.edition_wolf_dev.wcurl}\n'
        else:
            root.edition_wolf_pub.make_webpage(htmlDoc, resource_root_file.wcurl, resource_root_rel)
            root.edition_wolf_pub.wc.push_public()
            r += f'\tPublic:{root.edition_wolf_pub.wcurl}\n'

    root.edition_git.make_webpage(
        htmlDoc,
        os.path.join(Project.GITHUB_LFS_IMAGE_ROOT, resource_root_file.rel_to(pwdf())),
        resource_root_rel
    )

    r += f'\tFor GitHub:{root.edition_git.url}\n'

    root.edition_local.make_webpage(htmlDoc, url(resource_root_file), resource_root_rel)

    r += f'\tLocal:{root.edition_local.url}/index.html\n'

    r += '~' * (len(title) - 2)

    print(greens(r))




def FigureTable(*figs_captions, resources_root=None, exp_id=None, editable=False):
    children = [Script(js='''hotElements=[]''')]
    my_stacker = MagicTermLineLogger(FigureTable)
    for fig, caption in figs_captions:
        fig = File(fig).copy_into(resources_root, overwrite=True)
        # the_id = f'{exp_id}.{".".join(File(fig).names(keepExtension=False)[-1:])}'
        the_id = f'{exp_id}.{".".join(File(fig).names(keepExtension=False)[-1:])}'
        log(f'creating figure: {the_id}', stacker=my_stacker)
        children.append(
            TableRow(
                DataCell(HTMLImage(fig.abspath, fix_abs_path=True)),
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