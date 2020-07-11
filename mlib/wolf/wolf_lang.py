from wolframclient.language import wl, wlexpr



def Symbol(*args): return wl.Symbol(*args)
def Part(*args): return wl.Part(*args)
def StringSplit(*args): return wl.StringSplit(*args)
def Import(*args): return wl.Import(*args)
def Apply(*args): return wl.Apply(*args)
def CloudExport(*args): return wl.CloudExport(*args)
def Sequence(*args): return wl.Sequence(*args)
def If(*args): return wl.If(*args)
def Equal(*args): return wl.Equal(*args)

def APIFunction(*args): return wl.APIFunction(*args)
def Function(*args): return wl.Function(*args)
def ImportString(*args): return wl.ImportString(*args)

def CloudDeploy(*args): return wl.CloudDeploy(*args)
def CloudObject(*args): return wl.CloudObject(*args)
def CloudObjects(*args): return wl.CloudObjects(*args)
def CloudDirectory(*args): return wl.CloudDirectory(*args)
def FileExistsQ(*args): return wl.FileExistsQ(*args)
def DirectoryQ(*args): return wl.DirectoryQ(*args)

# from wolfpy import WOLFRAM

Right = wl.Right
def Rule(one, two): return wl.Rule(one, two)
def Color(*rgb): return wl.RGBColor(rgb)
Black = wl.Black
White = wl.White

bg = Black
bgi = White

Blue = wl.Blue
Red = wl.Red
Yellow = wl.Yellow
Pink = wl.Pink
FadedOrangeMaybe = Color(1, 1, 0, 0.75)

Large = wl.Large

Dashed = wl.Dashed

def Rotate(o, r): return wl.Rotate(o, r)

SpanFromLeft = wl.SpanFromLeft
SpanFromAbove = wl.SpanFromAbove
SpanFromBoth = wl.SpanFromBoth
Center = wl.Center
Top = wl.Top
Bottom = wl.Bottom
Left = wl.Left


def Alignment(a): return wl.Rule(wl.Alignment, a)
Centered = Alignment(Center)



def Background(color=Black, g=None, b=None):
    if g is not None: color = Color(color, g, b)
    return Rule(wl.Background, color)
_Default_Background = Background()
def LeaderSize(s): return Rule(wl.LeaderSize, s)
def Appearance(a): return Rule(wl.Appearance, a)
def Dividers(divs): return Rule(wl.Dividers, divs)
def Frame(fram): return Rule(wl.Frame, fram)

def LabelStyle(s): return Rule(wl.LabelStyle, s)

def FrameTicksStyle(s): return Rule(wl.FrameTicksStyle, s)
def AxesStyle(s): return Rule(wl.AxesStyle, s)
def IntervalMarkersStyle(s): return Rule(wl.IntervalMarkersStyle, s)
def FrameStyle(s): return Rule(wl.FrameStyle, s)

def Item(*o, background=_Default_Background, align=Centered): return wl.Item(*o, background, align)


def Ticks(t): return wl.Rule(wl.Ticks, t)
NoTicks = Ticks([[], []])
def TicksStyle(c): return wl.Rule(wl.TicksStyle, c)


def Raster(*o, background=_Default_Background): return wl.Raster(*o, background)


def Graphics(*o, background=_Default_Background): return wl.Graphics(*o, background)
def Scaled(*o): return wl.Scaled(*o)

def AspectRatio(r=1): return Rule(wl.AspectRatio, r)
def ImageSize(*size):
    if not size:
        size = 1000
    return Rule(wl.ImageSize, size)
def ImagePadding(pad): return Rule(wl.ImagePadding, pad)
def ImageResolution(res=100): return Rule(wl.ImageResolution, res)

def RasterSize(ras=500): return Rule(wl.RasterSize, ras)


def Grid(*args, background=_Default_Background): return wl.Grid(*args, background)
def GraphicsGrid(*args, background=_Default_Background): return wl.GraphicsGrid(*args, background)
def ListLinePlot(*args, background=_Default_Background): return wl.ListLinePlot(*args, background)

def Inset(
        obj,
        pos=(0, 0),
        opos=(Center, Center),
        scale=(1, 1),
        # dirs,
        background=_Default_Background

):
    return wl.Inset(obj, pos, opos, scale, background)

# Rasterize = WOLFRAM.session.function(wl.Rasterize)
# Directive = WOLFRAM.session.function(wl.Directive)
# Opacity = WOLFRAM.session.function(wl.Opacity)
# Style = WOLFRAM.session.function(wl.Style)
# Callout = WOLFRAM.session.function(wl.Callout)

def Rasterize(*args): return wl.Rasterize(*args)
def Directive(*args): return wl.Directive(*args)
def Opacity(*args): return wl.Opacity(*args)
def Style(*args): return wl.Style(*args)
def Callout(*args): return wl.Callout(*args)

def FontWeight(w): return Rule(wl.FontWeight, w)
def FontOpacity(o): return Rule(wl.FontOpacity, o)

def PlotLabel(l): return Rule(wl.PlotLabel, l)
def PlotRange(rang): return Rule(wl.PlotRange, rang)
def PlotStyle(style): return Rule(wl.PlotStyle, style)
def Prolog(pl): return Rule(wl.Prolog, pl)
def FontSize(size=20): return Rule(wl.Fontsize, size)


def LabelingFunction(args): return Rule(wl.LabelingFunction, args)




ROTATE_90 = -1
def Text(s, fontSize=20, coords=(0, 0), offset=(0, 0), direction=(1, 0), color=wl.White):
    s = str(s)
    if (direction == (1, 0) or direction == ROTATE_90) and offset == (0, 0) and coords == (0, 0):
        # not specifying these makes Text function differently and actually work in some contexts, unfortunately


        t = wl.Style(
            wl.Text(s),
            color,
            FontSize(fontSize),
        )

    else:
        t = wl.Style(
            wl.Text(
                s,
                coords,
                offset,
                direction,
            ),
            color,
            FontSize(fontSize)
        )
    if direction == ROTATE_90:
        t = Rotate(Rasterize(
            t,
            Background(),
            RasterSize(200),
            # ImageSize()
        ), wlexpr('90 Degree'))

    return t

