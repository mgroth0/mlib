# @singleton
from abc import abstractmethod
from collections import Counter
import numpy as np
from mlib.boot import log
from mlib.boot.stream import objarray, concat, make2d, listmap
from mlib.fig.makefigslib import MakeFigsBackend
from mlib.math import isreal
from mlib.wolf.bar import bar
from mlib.wolf.line import line
from mlib.wolf.scatter import scatter
from mlib.wolf.wolf_lang import *

class WolfMakeFigsBackend(MakeFigsBackend):
    @classmethod
    @abstractmethod
    def tableItem(cls, o, background):
        return Item(
            Text(o),
            Background(background)
        )

    @classmethod
    def table(cls, fd, force_wolf=True): return super().table(fd, force_wolf)

    @classmethod
    def color(cls, *rgb): return Color(*rgb)
    @classmethod
    def none(cls): return wlexpr('None')
    @classmethod
    def line(cls, fd): return line(fd)
    @classmethod
    def scatter(cls, fd): return scatter(fd)
    @classmethod
    def bar(cls, fd):
        # breakpoint()
        return bar(fd)
    @classmethod
    def image(cls, fd):
        log('making image')
        im = wl.Image(str(fd.x).replace('[', '{').replace(']', '}'))  # "Byte"
        im = str(im).replace("'", "")
        from mlib.wolf.wolfpy import weval
        im = weval(im)
        log('made image')
        return im


    @classmethod
    def export_fd(cls, makes, fd, overwrite):
        rrr = [(cls.addLayer(vis), fd.imgFile) for vis in makes]
        # breakpoint()
        return rrr
    @classmethod
    def makeAllPlots(cls, figDats, overwrite):
        import asyncio
        from wolframclient.evaluation import WolframEvaluatorPool
        wolfram_expressions = super().makeAllPlots(figDats, overwrite)
        wolfram_expressions2 = []
        for w in wolfram_expressions:
            # ww = wl.Show(w[0])
            ww = wl.Show(listmap(lambda x: x[0], w))
            # file = w[1]
            file = w[0][1].abspath
            wolfram_expressions2 += [wl.UsingFrontEnd(wl.Export(file, ww, ImageSize(1000)))]

        async def runasync():
            log('running runasync')
            async with WolframEvaluatorPool() as pool:
                countr = Counter(a=1)
                async def logAfter(wlexp, c, total):
                    await pool.evaluate(wlexp)
                    log(f'Finished making {c["a"]}/{total} figures')
                    c['a'] += 1
                tasks = []
                for exp in wolfram_expressions2:
                # for exp in wolfram_expressions:
                    tasks += [logAfter(exp, countr, len(figDats))]
                # breakpoint()
                await asyncio.wait(tasks)
        asyncio.run(runasync())





def defaultPlotOptions(fd):
    maxY = wl.All if fd.maxY is None or fd.maxY == 'inf' or not isreal(fd.maxY) else float(fd.maxY)
    minY = wl.All if fd.minY is None or fd.minY == 'inf' or not isreal(fd.minY) else float(fd.minY)
    maxX = wl.All if fd.maxX is None or fd.maxX == '-inf' or not isreal(fd.maxX) else float(fd.maxX)
    minX = wl.All if fd.minX is None or fd.minX == 'inf' or not isreal(fd.minX) else float(fd.minX)

    if maxY != wl.All and minY != wl.All:
        diff = maxY - minY
        pad = diff * (fd.y_pad_percent / 100)
        maxY = maxY + pad
        minY = minY - pad

    if maxX != wl.All and minX != wl.All:
        #     forced padding for labels
        diff = maxX - minX
        pad = diff * 0.2
        maxX = maxX + pad

    return [
        PlotLabel(Style(fd.title, FontSize(fd.title_size))),
        PlotRange([[minX, maxX], [minY, maxY]]),
        LabelStyle(bgi),
        Background(bg),
        FrameTicksStyle(Directive(bgi, 10)),
        AxesStyle(Directive(Large, bgi)),
        IntervalMarkersStyle(bgi),
        # (*    {{Large, bgi}, {Large, bgi}}*)
        Frame(True),
        FrameStyle([
            [
                #     left
                Directive(Opacity(1), FontOpacity(1), FontSize(fd.label_size)),
                #     right
                Directive(Opacity(0), FontOpacity(1), FontSize(fd.label_size))
            ],
            [
                #     bottom
                Directive(Opacity(1), FontOpacity(1), FontSize(fd.label_size)),
                #     top
                Directive(Opacity(0), FontOpacity(1), FontSize(fd.label_size))
            ]
        ]),
        LabelStyle([bgi, FontWeight("Bold"), FontSize(fd.label_size)])
    ]

# import sys
# exps = sys.argv[1].split(',')


# doesnt work, gives error:  'mappingproxy' object does not support item assignment
# def singleton(cls):
#     names_funcs = inspect.getmembers(OptionParser, predicate=inspect.isfunction)
#     for n, f in names_funcs:
#         cls.__dict__[n] = classmethod(f)
#     return cls


def importImage(file, caption=None):
    im = wl.Image(wl.Import(file), ImageSize(500))
    if caption:
        return wl.Labeled(im, caption, wl.Right)
    return im


def OneWayOfShowingARaster(rast, gl):
    return ListLinePlot([],
                        Prolog(rast),
                        NoTicks,
                        PlotRange([[0, gl], [0, gl]]),
                        ImageSize(1000),
                        AspectRatio()
                        )



def LinePlotGrid(line_values, triangle=False):
    gl = line_values[-1]
    listpoints = []

    for i in line_values:
        if triangle:
            listpoints += [[[i, 0], [i, gl - i]]]
            listpoints += [[[0, i], [gl - i, i]]]
        else:
            listpoints += [[[i, 0], [i, gl]]]
            listpoints += [[[0, i], [gl, i]]]
    lines = ListLinePlot(listpoints,
                         PlotStyle([
                             [FadedOrangeMaybe, Dashed],
                             [Yellow, Dashed]
                         ]),
                         NoTicks,
                         PlotRange([[0, gl], [0, gl]]),
                         ImageSize(1000),
                         AspectRatio(),

                         background=Background(
                             # wl.Red
                             wlexpr('None')
                         )
                         )
    return lines


def addHeaderLabels(mat, top, side):
    data = objarray(mat, 2)
    # noinspection PyTypeChecker
    data = concat(
        make2d(
            [None, Item(Text(
                side,
                fontSize=30,
                direction=ROTATE_90
                # direction=[0,1]
            ))] + ((np.repeat([SpanFromAbove],
                              len(data) - 2).tolist()) if len(data) > 2 else [])
        ).T,
        data, axis=1)
    # noinspection PyTypeChecker
    data = np.insert(data, 0, [
        None, None,
        Item(Text(top, fontSize=30))
    ] + ((np.repeat([SpanFromLeft], len(data[0]) - 3).tolist()) if len(data[0]) > 2 else [])

                     , axis=0)
    return data
