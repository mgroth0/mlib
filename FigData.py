from typing import Optional

from matplotlib import pyplot as plt, rcParams

from mlib.boot.mlog import log
from mlib.boot.mutil import arr, isreal, kmscript, bitwise_and
import numpy
inf = numpy.inf
from mlib.JsonSerializable import JsonSerializable, FigSet

from mlib.boot.mutil import make2d
class PlotOrSomething(JsonSerializable):
    def __init__(self, title='', make=False):
        self.title = title
        self.title_size = 80
        self.make = make



def Scat(*args, **kwargs):
    return FigData(*args, item_type='scatter', **kwargs)

_CurrentFigSet: Optional[FigSet] = None

class MultiPlot:

    def __init__(self, *args):
        self.plots = args

        ylab = ''
        xlab = ''
        hideYTicks = False
        title = ''
        xmin = inf
        ymin = inf
        ymax = inf

        xmax = inf
        # noinspection PyProtectedMember
        AUTO_Y = any(map(lambda a_plot: a_plot._ylim == 'auto', args))
        for p in args:
            if len(p.y_label) > len(ylab):
                ylab = p.y_label
            if len(p.x_label) > len(xlab):
                xlab = p.x_label
            if len(p.title) > len(title):
                title = p.title
            if p.hideYTicks:
                hideYTicks = True
            xmin = min(xmin, p.minX)
            xmax = max(xmax, p.maxX)

        for p in args:
            p.y_label = ylab
            p.x_label = xlab
            p.minX = xmin
            p.maxX = xmax
            p.title = title
            p.hideYTicks = hideYTicks
        for p in args:
            if AUTO_Y:
                p.fixAutoLims()
            ymin = min(ymin, p.minY)
            ymax = max(ymax, p.maxY)
        # [[args[j].minY,args[j].maxY] for j in [0,1,2]]
        for p in args:
            p.minY = ymin
            p.maxY = ymax
    def __getitem__(self, item):
        return self.plots.__getitem__(item)
    def __len__(self): return self.plots.__len__()
    def __iter__(self):
        return self.plots.__iter__()

def Line(*args, **kwargs):
    return FigData(*args, item_type='line', **kwargs)


def makefig(subplots=None, plotarg=''):
    log('making figure')
    if subplots is None:
        subplots = _CurrentFigSet.viss
    subplots = arr(subplots)
    rcParams['figure.figsize'] = 6, 8
    rcParams["savefig.dpi"] = 200
    with plt.style.context('dark_background'):
        # if len(subplots.shape) != 2:
        if len(subplots.shape) == 1:
            ncol = 1
        else:
            ncol = subplots.shape[1]
        nrow = subplots.shape[0]
        subplots = make2d(subplots)
        fig, axs = plt.subplots(ncols=ncol, nrows=nrow)
        if len(axs.shape) == 1:
            # noinspection PyUnresolvedReferences
            axs.shape = (axs.shape[0], 1)
        for r, row in enumerate(subplots):
            for c, fd in enumerate(row):
                if isinstance(fd, MultiPlot):
                    [d.show(axs[r, c]) for d in fd]
                else:
                    fd.show(axs[r, c])
        # fig.tight_layout()
        fig.tight_layout(pad=3.0)
        # fig.tight_layout(pad=10.0)

        if 'GUI' in plotarg:
            plt.show()
        if 'IMAGE' in plotarg:
            plt.savefig('_plot.png')
    if 'IMAGE' in plotarg:
        showInPreview()

def addToCurrentFigSet(plot):
    global _CurrentFigSet
    if _CurrentFigSet is None:
        _CurrentFigSet = FigSet()
    _CurrentFigSet.viss.append(plot)

class FigData(PlotOrSomething):

    def __init__(self, y=None, x=None, item_type='', item_color=None, add=True,
                 xlim=None,
                 ylim=None,
                 title='',
                 ylabel='',
                 xlabel='',
                 hideYTicks=False
                 ):
        super().__init__(title)

        if ylim is None:
            ylim = [inf, -inf]
        if xlim is None:
            xlim = [inf, -inf]
        if item_color is None:
            item_color = []
        if x is None:
            x = []
        if y is None:
            y = []
        self._ylim = ylim
        if ylim != 'auto':
            self.minY = self._ylim[0]
            self.maxY = self._ylim[1]

        self.hideYTicks = hideYTicks

        self.item_type = item_type

        self.x = x  # % can be {}
        self.y = y
        self.err = []

        self.x_label = xlabel
        self.y_label = ylabel

        self.y_log_scale = False

        self.y_axis = 'LEFT'
        if isinstance(xlim, slice):
            xlim = [xlim.start, xlim.stop]
        self.minX = xlim[0]
        self.maxX = xlim[1]

        self.y_ticks = None

        self.y_pad_percent = 10
        self.item_colors = item_color  # %row=item,cols=rbg

        self.delta_bar_idx = None
        self.delta_val = None

        self.make_legend = False

        self.scatter_texts = []
        self.scatter_shape = None

        self.scat_point_size = 100
        self.bar_sideways_labels = True

        self.label_size = 40

        # %        text_font_size = 80
        # %        texts = {}
        # %        text_coords %row=text,c1=x,c2=y

        self.patches = []

        self.callout_x = None
        self.callout = None

        self.caption = None

        if add:
            addToCurrentFigSet(self)


    def fixAutoLims(self):
        if self._ylim == 'auto':
            rel_y = arr(self.y)[bitwise_and(arr(self.x) >= self.minX, arr(self.x) < self.maxX)]
            dif = 0.1 * (max(rel_y) - min(rel_y))
            self.minY = min(rel_y) - dif
            self.maxY = max(rel_y) + dif


    def resetMinsAndMaxes(self):
        self.minX = min(self.x)
        self.maxX = max(self.x)
        self.minY = min(self.y)
        self.maxY = max(self.y)

    def show(self, axis=None):
        if axis is None:
            axis = plt
        if self.item_type == 'line':
            c = self.item_colors
            if not c:
                c = 'w'
            if len(self.x) > 0:
                axis.plot(arr(self.x).flatten(), arr(self.y).flatten(), c=c)
            else:
                axis.plot(arr(self.y).flatten(), c=c)
        elif self.item_type == 'scatter':
            # log('plotting scatterplot')
            axis.scatter(self.x, self.y, color=self.item_colors)
        axis.set_title(self.title)
        if isreal(self.minX) and isreal(self.maxX):
            axis.set_xlim([self.minX, self.maxX])
        if isreal(self.minY) and isreal(self.maxY):
            axis.set_ylim([self.minY, self.maxY])
        axis.set_ylabel(self.y_label)
        axis.set_xlabel(self.x_label)
        if self.hideYTicks:
            axis.set_yticks([])
            # axis.tick_params(
            #     axis='y',     # changes apply to the x-axis
            #     which='both', # both major and minor ticks are affected
            #     bottom=False, # ticks along the bottom edge are off
            #     top=False,    # ticks along the top edge are off
            #     labelbottom=False) # labels along the bottom edge are off

        if axis == plt:
            plt.savefig(
                'plot.png'
                # ,facecolor='black'
            )

def showInPreview(): kmscript("83575D89-FCCD-4F0A-8573-752C0EFDB881")
