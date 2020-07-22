from mlib.JsonSerializable import obj
from mlib.boot import log
from mlib.fig.makefigslib import MPLFigsBackend
from mlib.term import log_invokation

@log_invokation(with_args=True)
def makefigs(
        root,
        fig_backend,
        overwrite=False
):
    figDats = [
        {
            'dataFile': mfig,
            'imgFile' : mfig.resrepext('png')
        } for mfig in root.glob('**/*.mfig')
    ]
    log(f'{len(figDats)=}')
    if fig_backend == 'wolfram':
        from mlib.wolf.wolf_figs import WolfMakeFigsBackend
        backend = WolfMakeFigsBackend
    else:
        backend = MPLFigsBackend
    figDats = [obj(fd) for fd in figDats if overwrite or not fd['imgFile'].exists]
    backend.makeAllPlots(figDats, overwrite)
