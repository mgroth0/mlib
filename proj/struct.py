from mlib.boot.mutil import main_mod_file, PermaDict, singleton, Folder
@singleton
class PROJ:
    STATE = PermaDict('_metastate.json')
    DOCS_FOLDER = Folder('docs')
    LOCAL_DOCS_FOLDER = Folder('_docs')
    RESOURCES_FOLDER = DOCS_FOLDER['resources']
    FIGS_FOLDER = RESOURCES_FOLDER.mkdirs()['figs'].mkdirs()
    GITHUB_LFS_IMAGE_ROOT = 'https://media.githubusercontent.com/media/mgroth0/'
    PYCALL_FILE = RESOURCES_FOLDER['pycallgraph.png']
    PYDEPS_OUTPUT = RESOURCES_FOLDER[
        f'{main_mod_file().name_pre_ext}.svg'
    ]
