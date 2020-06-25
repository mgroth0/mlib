# **** upload URLs will need to not be static since apparently wolfram can't really handle uploads to the same url over and over. but redirects can be used, and make different kinds of cloud objects too

from wolframclient.language import wl

from mlib.boot.mlog import log
from mlib.boot.mutil import log_invokation
from mlib.proj.struct import pwdf
from mlib.file import File, Folder, Temp
from mlib.shell import shell
from mlib.web.web import IMAGE_ROOT_TOKEN
from mlib.wolf.wolfpy import WOLFRAM

def update_report(new_url, pub_url):
    co = WOLFRAM.cloud_deploy(wl.HTTPRedirect(new_url), url=pub_url, public=True)
    log(f'finished deploying redirect:{co[0]}')

RESOURCES_ROOT = "https://www.wolframcloud.com/obj/mjgroth/Resources/"

@log_invokation(with_args=True, with_result=True)
def upload_wolf_webpage(htmlDoc, wolfFolder, permissions='Private', resource_folder=None, DEV=False):
    if DEV:
        wolfFolder = 'Dev/' + wolfFolder
    with Temp('temp.html', w=htmlDoc.getCode()) as t:
        co = WOLFRAM.copy_file(t, f'{wolfFolder}/index.html', permissions=permissions)
    with Temp('temp.css', w=htmlDoc.stylesheet) as t:
        WOLFRAM.copy_file(t, f'{wolfFolder}/style.css', permissions=permissions)
    if resource_folder is not None:
        WOLFRAM.copy_file(resource_folder, f'Resources/{wolfFolder}', permissions=permissions)
    return co[0]



# REMOTE_ROOT = ''.join(shell('git config --get remote.origin.url').readlines()) + '/blob/master/'

@log_invokation(with_args=True, with_result=True)
def write_webpage(
        htmlDoc,
        docs_folder,
        image_root,
        local_docs_folder
):
    pwdname = pwdf().name

    web_resources_root = f'{image_root}{pwdname}/master/{docs_folder.name}'

    docs_folder.mkdir()
    page_file = docs_folder[f'{htmlDoc.name}.html']
    page_parent = Folder(File(page_file).parentDir)

    page_file.write(htmlDoc.getCode().replace(IMAGE_ROOT_TOKEN, web_resources_root))

    page_parent['style.css'].write(htmlDoc.stylesheet)

    local_docs_folder.mkdir()
    local_page_file = File(local_docs_folder[f'{htmlDoc.name}.html'])
    local_page_parent = Folder(local_page_file.parentDir)
    local_page_file.write(htmlDoc.getCode().replace(
        IMAGE_ROOT_TOKEN,
        File(docs_folder).url()
    ))
    local_page_parent['style.css'].write(htmlDoc.stylesheet)
    if htmlDoc.show:
        local_page_file.open()
    return local_page_file

@log_invokation()
def push_docs():
    shell('git reset').interact()
    shell('git add docs').interact()
    shell('git commit docs -m "auto-gen docs"').interact()
    shell('git push').interact()

