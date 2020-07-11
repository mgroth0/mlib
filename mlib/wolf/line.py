from wolframclient.language import wlexpr, wl

from lib.wolf.wolf_figs import defaultPlotOptions
from mlib.boot.mlog import log
from mlib.boot.stream import ziplist
from mlib.wolf.wolf_lang import LabelingFunction, Rule, Color, Callout, Background, Appearance, LeaderSize, ListLinePlot

def line(fd):
    x = fd.x
    y = fd.y
    log('creating a line with length: ' + str(len(fd.y)))

    # if DS is not None and len(x) > DS:
    #     ds = floor(len(x) / DS)
    #     x = simple_downsample(x, ds)
    #     y = simple_downsample(y, ds)
    #
    #     log("downsampled")
    calcedMinY = min(list(filter(lambda x: x is not None, y)))
    calcedMaxY = max(list(filter(lambda x: x is not None, y)))

    map_expr = wlexpr('{#1, #2} &')

    ops = defaultPlotOptions(fd)

    if fd.callout is not None:
        ops += [
            LabelingFunction(wlexpr(
                f'If[#1[[1]] == {fd.callout_x}, Callout[",{fd.callout}", Above ,LabelStyle->{{10,Bold,White}},Background->Black]] &'
            ))
        ]

    if fd.item_colors is not None:
        ops.append(Rule(wl.PlotStyle, Color(*fd.item_colors)))

    # data = wl.MapThread(map_expr, [x, y])
    # err('we had to remove weval for pool debug')
    # data = weval(data)
    # data = list(data)

    data = ziplist(x,y)

    if len(y) > 2:
        print('\tcallout for ' + str(data[-1]))
        col = fd.item_colors
        print('\tcolor: ' + str(col))
        col = Color(*fd.item_colors)

        data[-1] = Callout(
            data[-1],
            fd.y_label,
            data[-1],  # pos
            Background(col),
            Appearance('Balloon'),
            LeaderSize(
                [
                    5,
                    wlexpr('180 Degree'),
                    1
                ]
            )
        )

    return ListLinePlot(data
                     ,
                        defaultPlotOptions(fd),
                        ops,
                     )


    if 'Asana' in fd.title:
        return ListLinePlot(fd.x, fd.y, defaultPlotOptions(fd), "todo: log scale if y_log_scale")

    if firstLine:
        fd2 = viss[1]
        x2 = fd2.x
        y2 = fd2.y
        # if DS is not None and len(x) > DS:
        #     ds = floor(len(x2) / DS)
        #     x2 = simple_downsample(x2, ds)
        #     y2 = downsample(y2, ds)
    #
    #     TwoAxisListLinePlot of fd and x2/y2?
    # rectangele for x? patches?
