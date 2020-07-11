import os

from mlib.JsonSerializable import obj
from mlib.boot import log
from mlib.boot.mutil import log_return
from mlib.fig.makefigslib import MPLFigsBackend
from mlib.file import File, Folder
from mlib.term import log_invokation

@log_invokation(with_args=True)
def makefigs(cfg, overwrite=False):
    root = cfg.root
    figDats = getFigDats(root)
    if cfg.fig_backend == 'wolfram':
        from mlib.wolf.wolf_figs import WolfMakeFigsBackend
        backend = WolfMakeFigsBackend
    else:
        backend = MPLFigsBackend
    figDats = [obj(fd) for fd in figDats]
    figDats = [fd for fd in figDats if overwrite or not fd.pngExists]
    backend.makeAllPlots(figDats, overwrite)
    log('finished making plots!')




# def lastFigurableFolder(compiled=False):
#     figurableFolds = File('_figs/figs_dnn').files()
#     if not compiled:
#         figurableFolds = listfilt(lambda f: 'compile' not in f.name, figurableFolds)
#     return figurableFolds[-1].abspath if len(figurableFolds) > 0 else None

@log_return(as_count=True)
def getFigDats(ROOT_FOLDER):
    ROOT_FOLDER = Folder(ROOT_FOLDER)
    files = []
    ids = []
    folders = []
    pngFiles = []
    fig_exps = []

    # global this_exps
    possible_exps = dict()
    for name in ROOT_FOLDER.paths:
        if '.DS_Store' in name or 'metadata.json' in name: continue
        this_exp = os.path.basename(name)
        possible_exps[this_exp] = False

        for nam in ROOT_FOLDER[name].paths:
            #     if os.path.basename(name) in exps:
            for subname in ROOT_FOLDER[name][nam].paths:
                if subname.endswith("fs.json"):
                    files.append(subname)
                    ids.append(subname.split("/")[-1].replace("_fs.json", ""))
                    # folders.append(ROOT_FOLDER + "/" + subname.split("/")[-2])

                    folders.append(ROOT_FOLDER.resolve(this_exp).resolve(subname.split("/")[-2]).abspath)
                    fig_exps.append(this_exp)

    figDats = [{"file": File(file), "folder": folder, "id": id, "exp": exp} for file, folder, id, exp in
               zip(files, folders, ids, fig_exps)]

    for name in ROOT_FOLDER.paths:
        if '.DS_Store' in name or 'metadata.json' in name: continue
        for nam in ROOT_FOLDER[name].paths:
            # if os.path.basename(name) in exps:
            for subname in ROOT_FOLDER[name][nam].paths:
                if subname.endswith(".png"):
                    pngFiles.append(subname)

    pngIDs = [x.split("/")[-1] for x in pngFiles]

    for idx, fd in enumerate(figDats):
        fd["imgFileName"] = fd["id"] + ".png"
        fd["imgFile"] = fd["folder"] + "/" + fd["imgFileName"]
        fd["pngExists"] = File(fd["imgFile"]).exists
        if not possible_exps[fd['exp']]: possible_exps[fd['exp']] = not fd["pngExists"]

    # for key in list(possible_exps.keys()):
    #     if possible_exps[key]:
    #         this_exps = this_exps + ',' + key

    return figDats

# this_exps = ''
