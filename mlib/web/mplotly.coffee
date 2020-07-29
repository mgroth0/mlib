plot_map = {}

mplotly = (dv) ->
    dv.def {
        animate: ({
            data_changes
            newXrange,
            newYrange,
            newAnnotations,
            dur,
            redraw
        }) ->
            log('setting up animation')
            duration = 500

            if dur?
                duration = dur

            rd = true
            if redraw?
                rd = redraw

            if data_changes? and (data_changes.length > 0)?
                data = []
                for d in @._fullData
                    data.push({x: d.x, y: d.y})
                for [i, d] in data_changes
                    if data.length <= i
                        Plotly.addTraces(dv, d)
                        data.push(d)
                    else
                        data[i] = d

            layout = {}
            if newXrange?
                layout.xaxis = {range: newXrange}
            if newYrange?
                layout.yaxis = {range: newYrange}
            if newAnnotations?
                layout.annotations = newAnnotations

            if !data_changes? or (data_changes.length == 0)
                update = {layout: layout}
            else if (not newXrange?) and (not newYrange?) and (not newAnnotations?)
                update = {data: data}
            else
                update = {data  : data, layout: layout}
            log('calling actual animation')
            Plotly.animate(@, update, {
                transition:
                    duration: duration
                    easing  : 'linear'
                frame:
                    duration: duration
                    redraw: rd
            })
    }

inc_calcs =  (ecg_plt, inc) ->
    newXrange = ecg_plt._fullLayout.xaxis.range.map(
        (e) -> e + inc
    )
    newStart = ecg_plt._fullData[0].x.findIndex((e) -> e >= newXrange[0])
    newStop = ecg_plt._fullData[0].x.findIndex((e) -> e >= newXrange[1])
    newY = ecg_plt._fullData[0].y.slice(newStart, newStop)
    newYRange = autoYRange(newY)

    windowRect = {
        x: [newXrange[1], newXrange[1], newXrange[0], newXrange[0]]
        y: [4000, 0, 0, 4000]
    }

    newPointer = ((newXrange[1] - newXrange[0]) / 2.0) + newXrange[0]
    pointerLine = {
        x: [newPointer, newPointer],
        y: [-1, 1]
    }
    return [newXrange, newYRange, newPointer, pointerLine,windowRect,newStart,newStop]
