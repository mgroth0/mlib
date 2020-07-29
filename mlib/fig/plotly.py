from collections import Iterable

from mlib.math import TimeSeries
import plotly.graph_objs as go

from mlib.term import log_invokation


@log_invokation
def line(
        title,
        a: TimeSeries,
        displayModeBar=False,
        staticPlot=True,
        line_args=None,
        fig_args=None,
        layout=None
):
    if layout is None: layout = {}
    if fig_args is None: fig_args = {}
    if line_args is None: line_args = {}
    data = [go.Scatter(
        x=a.t,
        y=a.y,
        # labels={
        #     'x': a.t_unit.name,
        #     'y': a.y_unit
        # },
        # **line_args
    )]
    layout = go.Layout(
        template='plotly_dark',
        title=title,
        # yaxis=dict(autorange=True),
        **layout
    )
    # fig.plotly_relayout(layout)
    fig = go.Figure(
        data=data,
        layout=layout,
        **line_args
    )
    fig.update_layout(
        xaxis_title=a.t_unit.name,
        yaxis_title=a.y_unit
    )
    return _get_fig(
        fig,
        displayModeBar=displayModeBar,
        staticPlot=staticPlot,
        **fig_args
    )

@log_invokation
def line_scatter(
        title,
        ts: TimeSeries,
        tp: Iterable,
        tp_ref=None,
        displayModeBar=False,
        staticPlot=True,
        line_args=None,
        fig_args=None,
        layout=None
):
    if layout is None: layout = {}
    if fig_args is None: fig_args = {}
    if line_args is None: line_args = {}

    if tp_ref is None:
        tp_ref = ts
    data = [
        go.Scatter(
            x=ts.t,
            y=ts.y,
            line=dict(
                width=1,
                color='#FF0000'
                # shape='spline'
            )
        ),
        go.Scatter(
            x=tp_ref.t[tp],
            y=tp_ref.y[tp],
            mode='markers',
            marker=dict(
                color='#0000B4',
                size=20  # default 6
            )
        )
    ]
    layout = go.Layout(
        template='plotly_dark',
        title=title,
        # yaxis=dict(autorange=True),
        **layout
    )
    fig = go.Figure(
        data=data,
        layout=layout,
        **line_args
    )
    fig.update_layout(
        xaxis_title=ts.t_unit.name,
        yaxis_title=ts.y_unit,

        xaxis=dict(
            # the real reason im doing this is because in the animations, the ticks are annoyingly flickering. maybe if I hard-set this it will fix that problem.
            tickmode='linear',
            tick0=0,
            dtick=1
        )
    )
    return _get_fig(
        fig,
        displayModeBar=displayModeBar,
        staticPlot=staticPlot,
        **fig_args
    )

def _get_fig(
        fig,
        displayModeBar=False,
        staticPlot=True,
        **fig_args
):
    return fig.to_html(
        config={
            'displaylogo'   : False,
            'displayModeBar': displayModeBar,
            'staticPlot'    : staticPlot
        },
        include_plotlyjs=False,
        full_html=False,
        **fig_args
    )
