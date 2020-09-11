from wolframclient.language import wl

# import mlib.wolf.makefigslib
# from wolfpy import weval
from mlib.fig import makefigslib

def scatter(fd):
    color_y = []
    cols = []
    for xx, yy, col in zip(fd.x, fd.y, fd.item_colors):
        cc = wl.RGBColor(col)
        cols.append(cc)
        color_y.append(
            wl.Labeled([xx, yy], wl.Style(fd.scatter_shape if fd.scatter_shape is not None else ".", cc, 40),
                       wl.Center))

    return wl.ListPlot(color_y,
                    makefigslib.defaultPlotOptions(fd)
                    )


    return weval('''
    If[fd[["item_type"]]=="scatter",(
        If[Not2isNull[DS] && Length@x > DS, (
            ds = Floor[Length@x / DS];
        x = Downsample[x, ds];
        y = Downsample[y, ds];
        )];
    ListPlot[
    (
    log["here1: " <> ToString@Dimensions@x <> "|" <> ToString@Dimensions@y <> "|" <> ToString@Dimensions@fd[["item_colors"]] <> "|" <> ToString@Dimensions@fd[["scatter_texts"]]];
    
    log["here2: " <> ToString@x];
    
    dat =
    If[Length@fd[["item_colors"]] > 0,
    MapThread[Style[{#1,#2},RGBColor[#3]]&,{x, y,fd[["item_colors"]]}]
    ,MapThread[{#1, #2} &, {x, y}]];
    
    
    
    (*                log["here2:" <> ToString@fd];*)
    If[Length@fd[["scatter_texts"]]>0,(
        log["here3"];
    dat = If[Length@fd[["item_colors"]] > 0,
    
    MapThread[Style[Callout[#1,#2,Right,LabelStyle->RGBColor[#3]],RGBColor[#3]]&,{dat,fd[["scatter_texts"]],fd[["item_colors"]]}],
    
    MapThread[Callout[#1,#2,Right]&,{dat,fd[["scatter_texts"]]}]
    
    ];
    )];
    log["here4"];
    dat
    ),
    defaultPlotOptions[fd],
    FrameLabel -> {fd[["x_label"]], fd[["y_label"]]}
    ]
    )
    ''')