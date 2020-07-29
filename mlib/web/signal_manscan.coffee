appendToBody(E.P('hola from signal_manscan.coffee'))

ecg_plt = () -> plot_map[Object.keys(plot_map).find((e)->e.includes('ECG'))]
ibi_plt = () -> plot_map[Object.keys(plot_map).find((e)->e.includes('IBI'))]

pendingUpdate = null
requestedUpdate = false

pointerArrow = () ->
    x        : 0.5
    y        : 0.5
    yanchor  : 'middle'
    ax       : 0
    ay       : -200
    axref    : 'paper'
    xref     : 'paper'
    yref     : 'paper'
    text     : 'pointer'
    showarrow: true
    arrowhead: 1

ws = openSocketClient({
    url      : "ws://localhost:9998"
    onopen   : () ->
        @.send("GET_ALL")
        log("Message is sent...")
    onmessage: (evt) ->
        log("Message is received... (#{evt.data.shorten(50)})")
        if evt.data.startsWith('TEXT')
            appendToBody(E.Pre(evt.data.afterFirst(':')))
        else if evt.data.startsWith('HTML') or evt.data.startsWith('PLOT')
            div = E.Div(evt.data.afterFirst(':'))
            appendToBody(div)
            arr = div.getElementsByTagName('script')
            for a in arr
                eval(a.innerHTML) # run script inside div
            if evt.data.startsWith('PLOT') #after ran script
                dv = div.children[0].children[0]
                dv = mplotly(dv)
                plot_map[dv._fullLayout.title.text] = dv
                if dv == ecg_plt()
                    dv.def {
                        x: () -> @._fullData[0].x
                        y: () -> @._fullData[0].y
                    }
                    Plotly.relayout(ecg_plt(), {
                        'annotations': [pointerArrow()]
                    })
        else if evt.data.startsWith('UPDATE')
            requestedUpdate = false
            u = JSON.parse(evt.data.afterFirst(':'))
            if u?
                pendingUpdate = u
        else
            appendToBody(E.Div(evt.data))
    onclose  : ->
        alert("Connection is closed...")
})
pointer = 0
pointerL = null
stopShifting = false
isShifting = false

increment = 1 / 100

keydown (e) ->
    if e.keyCode == SPACE_BAR.keyCode
        1 + 1
    else if [LEFT_ARROW.keyCode, RIGHT_ARROW.keyCode].includes(e.keyCode)
        if not isShifting
            retic()
            log('finished retic')
            inc = 1
            if e.keyCode == LEFT_ARROW.keyCode
                inc = -1
            stopShifting = false
            shift(inc)
    else if [UP_ARROW.keyCode, DOWN_ARROW.keyCode].includes(e.keyCode)
        if e.keyCode == UP_ARROW.keyCode
            increment *= 10
        else
            increment /= 10
keyup (e) ->
    if [LEFT_ARROW.keyCode, RIGHT_ARROW.keyCode].includes(e.keyCode)
        stopShifting = true



DUR = 10
RELOAD_THRESH = 0.25



shift = (pos) ->
    log('top of shift()')
    isShifting = true
    inc = increment * pos
    log('about to call inc_calcs')
    [newXrange, newYRange, newPointer, pointerLine, windowRect, newStart, newStop] = inc_calcs(ecg_plt(), inc)
    log('finished inc_calcs')
    pointer = newPointer
    pointerL = pointerLine
    checkUp = ->
        log('in checkUp')
        if stopShifting
            arrow = pointerArrow()
            arrow.yref = 'y'
            y = ecg_plt().y().slice(newStart, newStop)
            arrow.y = y[Math.round(y.length / 2)]
            #            ecg_plt().animate(
            ##                data_changes: [[2, pointerLine]]
            #                newAnnotations: [arrow]
            #                dur         : 10
            #            )
            Plotly.relayout(ecg_plt(), {
                'annotations': [arrow]
            })
            isShifting = false
    log('starting main shift')
    ecg_plt().animate(
#        data_changes: [[2, pointerLine]] #maybe
        newXrange: newXrange
#                    newYRange: newYRange\
        dur      : DUR
        redraw   : false
    ).then((v)->
        log('finished main shift, checking if should update')
        x = ecg_plt().x()
        x0 = x[0]
        xEnd = x.slice(-1)[0]
        dif = xEnd - x0
        if !pendingUpdate? and (not requestedUpdate) and (pointer > x0 + (dif * (.5 + RELOAD_THRESH)) or pointer < x0 + (dif * (.5 - RELOAD_THRESH)))
            ws.send("GET_UPDATE:#{pointer}")
            requestedUpdate = true
        #            1+1
        log('finished checking if should update')
    ).then((v)->
        log('in next then (why another?)')
        if pendingUpdate?
#            ibi_plt has nothing to do with pending update. Its just that it doesnt need to update that often, so this is a way to save resources and its roughly the update frequency that I want
            ibi_plt().animate
                data_changes: [[1, windowRect]]
            ecg_plt().animate(
                data_changes: [
                    [0, pendingUpdate[0]],
                    [1, pendingUpdate[1]]
                ]
                dur         : 1
            ).then((v)->
                pendingUpdate = null
            )
    ).then((v) ->
        log('in final then')
        checkUp()
        if not stopShifting
            shift(pos)
    ).catch(checkUp)
    log('bottom of shift')