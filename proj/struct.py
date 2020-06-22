from mlib.boot.mutil import main_mod_file, PermaDict, singleton, Folder
@singleton
class PROJ:
    STATE = PermaDict('_metastate.json')
    DOCS_FOLDER = Folder(
        'docs', mker=True
    )
    LOCAL_DOCS_FOLDER = Folder('_docs').mkdir()
    RESOURCES_FOLDER = DOCS_FOLDER['resources']
    FIGS_FOLDER = RESOURCES_FOLDER['figs']
    GITHUB_LFS_IMAGE_ROOT = 'https://media.githubusercontent.com/media/mgroth0/'
    PYCALL_FILE = RESOURCES_FOLDER['pycallgraph.png']
    PYDEPS_OUTPUT = None
    if main_mod_file() is not None:
        PYDEPS_OUTPUT = RESOURCES_FOLDER[
            f'{main_mod_file().name_pre_ext}.svg'
        ]
