from wolframclient.language import wl, wlexpr

from mlib.boot.mlog import err
from mlib.boot.stream import listmap
from mlib.file import File, Folder
from mlib.input import boolinput
from mlib.term import log_invokation
from mlib.wolf.wolfpy import weval
_REGISTERED_SUBROOTS = (
    '/CloudSymbol',
    '/trash'
)
_MAIN_SUBROOT = '/Users'
@log_invokation
def manage():
    cloud_files = weval(wl.CloudObjects(wlexpr('$CloudRootDirectory')))
    for wcf in listmap(File, cloud_files):
        if wcf.abspath in _REGISTERED_SUBROOTS:
            pass
        elif wcf.abspath == _MAIN_SUBROOT:
            @log_invokation(with_args=True, stack=True)
            def recurse_cloud_file(sub_wcf):
                # f = File(f'{sub_wcf.abspath}')
                if not sub_wcf.exists:
                    recurse_cloud_file.my_stacker.done = True
                    if boolinput(f'{sub_wcf} is not mirrored locally, delete cloud file?'):
                        sub_wcf.wc.delete()
                if sub_wcf.wc.isdir:
                    if Folder(sub_wcf)['.CLOUD_FILES.txt'].exists:
                        Folder(sub_wcf)['.CLOUD_FILES.txt'].write(
                            '\n'.join(listmap(
                                lambda e: e.abspath.replace(f'{Folder(sub_wcf).abspath}/', ''),
                                sub_wcf.wc.files)
                            )
                        )
                    else:
                        [recurse_cloud_file(c) for c in sub_wcf.wc.files]
            recurse_cloud_file(wcf)
            recurse_cloud_file.my_stacker.done = True
        else:
            err(f'{wcf.abspath} is not a registered Wolfram Cloud subroot')
