import atexit
import os

from mlib.file import url, File, pwdf
from mlib.proj.struct import Project
from mlib.term import greens
from mlib.web.html import HTMLPage

def write_index_webpage(
        htmlDoc: HTMLPage,
        root,
        resource_root_file,
        upload_resources=True,
        WOLFRAM=False,
        DEV=False
):
    resource_root_rel = File(resource_root_file).rel_to(root)

    assert root.edition_local['.'].abspath == root.edition_local.abspath

    assert root[resource_root_rel].rel_to(root['.']) == resource_root_rel

    assert root[resource_root_rel].abspath == resource_root_file.abspath

    write_sub_webpage(
        htmlDoc=htmlDoc,
        index_root=root,
        rel_resource_root=resource_root_rel,
        rel_root='.',
        upload_resources=upload_resources,
        WOLFRAM=WOLFRAM,
        DEV=DEV
    )


def write_sub_webpage(
        htmlDoc: HTMLPage,
        index_root,
        rel_resource_root,
        rel_root,
        upload_resources=True,
        WOLFRAM=False,
        DEV=False
):
    resource_root_rel = index_root[rel_resource_root].rel_to(index_root[rel_root])
    resource_root_file = index_root[rel_resource_root]
    r = f'\n~~Created Webpage: {htmlDoc.name}~~\n'
    title = r
    if WOLFRAM:
        if upload_resources:
            resource_root_file.wc.push_public()
        if DEV:
            index_root.edition_wolf_dev[rel_root].make_webpage(htmlDoc, resource_root_file.wcurl, resource_root_rel)
            index_root.edition_wolf_dev[rel_root].wc.push_public()
            r += f'\tPublic(DEV):{index_root.edition_wolf_dev[rel_root].wcurl}\n'
        else:
            index_root.edition_wolf_pub[rel_root].make_webpage(htmlDoc, resource_root_file.wcurl, resource_root_rel)
            index_root.edition_wolf_pub[rel_root].wc.push_public()
            r += f'\tPublic:{index_root.edition_wolf_pub[rel_root].wcurl}\n'

    index_root.edition_git[rel_root].make_webpage(
        htmlDoc,
        resource_root=os.path.join(Project.GITHUB_LFS_IMAGE_ROOT, resource_root_file.rel_to(pwdf())),
        resource_root_rel=os.path.join(Project.GITHUB_LFS_IMAGE_ROOT, resource_root_file.rel_to(pwdf())),
        force_fix_to_abs=False
    )

    r += f'\tFor GitHub:{index_root.edition_git[rel_root].url}\n'

    index_root.edition_local[rel_root].make_webpage(htmlDoc, url(resource_root_file), resource_root_rel)

    local_page = index_root.edition_local[rel_root][htmlDoc.name + '.html']

    r += f'\tLocal:{local_page.url}\n'

    r += '~' * (len(title) - 2)

    print(greens(r))

    if htmlDoc.show:
        atexit.register(
            local_page.open
        )
