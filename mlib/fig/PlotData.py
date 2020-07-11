from matplotlib import pyplot as plt, rcParams
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from numpy import inf

from mlib.boot.mutil import arr, isreal, bitwise_and, maxreal, minreal
from mlib.file import File
from mlib.km import showInPreview
from mlib.term import log_invokation
from mlib.JsonSerializable import JsonSerializable
from mlib.boot.mutil import make2d

PLT_BAR_W = 0.3

class FigData(JsonSerializable):
    def __init__(self, title='', make=False):
        self.title = title
        self.title_size = 80
        self.make = make

class PlotData(FigData):

    def __init__(self, y=None, x=None, item_type='', item_color=None,
                 xlim=None,
                 ylim=None,
                 title='',
                 ylabel='',
                 xlabel='',
                 hideYTicks=False,
                 xticks=None,
                 legend=None
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
        self.xticks = xticks
        self.y = y
        self.err = []

        self.legend = legend

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


    def fixAutoLims(self):
        if self._ylim == 'auto':
            rel_y = arr(self.y)[
                bitwise_and(
                    arr(self.x) >= self.minX,
                    arr(self.x) < self.maxX
                )
            ]
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
                plot = axis.plot(arr(self.x).flatten(), arr(self.y).flatten(), c=c)
            else:
                plot = axis.plot(arr(self.y).flatten(), c=c)
        elif self.item_type == 'scatter':
            # log('plotting scatterplot')
            plot = axis.scatter(self.x, self.y, color=self.item_colors)
        elif self.item_type == 'bar':
            plot = axis.bar(
                self.x,
                self.y,
                tick_label=self.xticks,
                width=PLT_BAR_W,
                align='center',
                color=self.item_colors
            )
        elif self.item_type == 'box':
            plot = axis.boxplot(
                self.y,
                positions=self.x,
                showmeans=True,
                labels=self.xticks,
                widths=PLT_BAR_W,
                boxprops={'color': self.item_colors},
                flierprops={'markerfacecolor': self.item_colors},
                capprops={'color': self.item_colors},
                whiskerprops={'color': self.item_colors},
            )
            if self.xticks[0] != '':
                axis.set_xticks(self.x)
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

        if self.legend:
            axis.legend(
                handles=self.legend,
                loc='lower left'
            )

        assert axis != plt
        # if axis == plt:
        #     plt.savefig(
        #         'plot.png'
        # #         ,facecolor='black'
        #     )

class MultiPlot:

    def __init__(self, *plots):
        self.plots = plots

        ylab = ''
        xlab = ''
        hideYTicks = False
        title = ''
        xmin = inf
        ymin = inf
        ymax = inf

        xmax = inf

        # noinspection PyProtectedMember
        AUTO_Y = any(map(lambda a_plot: a_plot._ylim == 'auto', plots))
        for p in plots:
            if p.y_label is not None and len(p.y_label) > len(ylab):
                ylab = p.y_label
            if p.x_label is not None and len(p.x_label) > len(xlab):
                xlab = p.x_label
            if p.title is not None and len(p.title) > len(title):
                title = p.title
            if p.hideYTicks:
                hideYTicks = True
            xmin = maxreal(xmin, p.minX)
            xmax = minreal(xmax, p.maxX)

        for p in plots:
            p.y_label = ylab
            p.x_label = xlab
            if xmin is not None: p.minX = xmin
            if xmax is not None: p.maxX = xmax
            p.title = title
            p.hideYTicks = hideYTicks
        for p in plots:
            if AUTO_Y:
                p.fixAutoLims()
            ymin = maxreal(ymin, p.minY)
            ymax = minreal(ymax, p.maxY)
        # [[args[j].minY,args[j].maxY] for j in [0,1,2]]
        for p in plots:
            if ymin is not None: p.minY = ymin
            if ymax is not None: p.maxY = ymax
    def __getitem__(self, item):
        return self.plots.__getitem__(item)
    def __len__(self): return self.plots.__len__()
    def __iter__(self):
        return self.plots.__iter__()

def DoubleBarOrBox(*bars, legend):
    assert len(bars) == 2  # make it work for 1 or >2 later

    bars[1].x = bars[1].x + PLT_BAR_W
    bars[1].xticks = ['' for _ in bars[1].xticks]  # is this necessary?
    bars[0].item_colors = 'b'
    bars[1].item_colors = 'g'

    mb = MultiPlot(*bars)

    handles = [
        Line2D([0], [0], color='b', lw=4, label=legend[0]),
        Line2D([0], [0], color='g', lw=4, label=legend[1]),
    ]

    bars[1].legend = handles

    return mb

def make1fig(fig, file): return makefig([[fig]], file)

@log_invokation
def makefig(
        subplots,
        file=None,
        show=False
):
    assert subplots is not None
    subplots = arr(subplots, ndims=2)
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
        fig, axs = plt.subplots(ncols=ncol, nrows=nrow, squeeze=False)

        if len(axs.shape) == 1:
            # noinspection PyUnresolvedReferences
            axs.shape = (axs.shape[0], 1)
        for r, row in enumerate(subplots):
            for c, fd in enumerate(row):
                if isinstance(fd, MultiPlot):
                    [d.show(axs[r, c]) for d in fd]
                else:
                    fd.show(axs[r, c])
        fig.tight_layout(pad=3.0)
        if file is None:
            plt.show()
        else:
            File(file).mkparents()
            plt.savefig(file)
            plt.clf()
            if show:
                showInPreview(imageFile=File(file).abspath)
            return File(file)
