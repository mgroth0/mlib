# **** upload URLs will need to not be static since apparently wolfram can't really handle uploads to the same url over and over. but redirects can be used, and make different kinds of cloud objects too

from wolframclient.language import wl

from mlib.boot.mlog import log
from mlib.boot.mutil import log_invokation, Temp, shell, Folder, File
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

DOCS_FOLDER = Folder('docs')
LOCAL_DOCS_FOLDER = Folder('_docs')

@log_invokation(with_args=True, with_result=True)
def prep_webpage(htmlDoc, web_resources_root):
    DOCS_FOLDER.mkdir()
    DOCS_FOLDER['index.html'].write(htmlDoc.getCode().replace(IMAGE_ROOT_TOKEN, web_resources_root))
    DOCS_FOLDER['style.css'].write(htmlDoc.stylesheet)

    LOCAL_DOCS_FOLDER.mkdir()
    LOCAL_DOCS_FOLDER['index.html'].write(htmlDoc.getCode().replace(
        IMAGE_ROOT_TOKEN,
        File(DOCS_FOLDER).url()
    ))
    LOCAL_DOCS_FOLDER['style.css'].write(htmlDoc.stylesheet)

@log_invokation()
def push_docs():
    shell('git reset').interact()
    shell('git add docs').interact()
    shell('git commit docs -m "auto-gen docs"').interact()
    shell('git push').interact()
