#appendToBody(E.P('hola from signal_manscan.coffee'))

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

last_message_id = 0
current_annos = []
ws = openSocketClient({
    url      : "ws://localhost:9998"
    onopen   : () ->
        @.send("GET_ALL")
        log("Sent message GET_ALL...")
    onmessage: (evt) ->
        data = JSON.parse(evt.data)
        log("Message #{data.id} is received... (#{evt.data.shorten(50)})")
        if last_message_id >= data.id
            log('    ... it was a duplicate')
            return
        last_message_id = data.id
        if data.type == 'TEXT'
            appendToBody(E.Pre(evt.data.afterFirst(':')))
        else if data.type == 'HTML' or data.type == 'PLOT'
            div = E.Div(data.value)
            appendToBody(div)
            arr = div.getElementsByTagName('script')
            for a in arr
                eval(a.innerHTML) # run script inside div
            if data.type == 'PLOT' #after ran script
                dv = div.children[0].children[0]
                dv = mplotly(dv)
                plot_map[dv._fullLayout.title.text] = dv
                if dv == ecg_plt()
                    dv.def {
                        x: () -> @._fullData[0].x
                        y: () -> @._fullData[0].y
                    }
                    current_annos = ecg_plt()._fullLayout.annotations
                    Plotly.relayout(ecg_plt(), {
                        'annotations': current_annos.concat([pointerArrow()])
                    })
                    Y_FACTOR = 5
                    yrange_down_button = E.button('y_range -')
                    yrange_down_button.onclick = ->
                        ecg_plt().animate(
                            newYrange: ecg_plt()._fullLayout.yaxis.range.map((e)->
                                e / Y_FACTOR
                            )
                        )
                    yrange_up_button = E.button('y_range +')
                    yrange_up_button.onclick = ->
                        ecg_plt().animate(
                            newYrange: ecg_plt()._fullLayout.yaxis.range.map((e)->
                                e * Y_FACTOR
                            )
                        )
                    div.appendChild(yrange_down_button)
                    div.appendChild(yrange_up_button)

                    xrange_down_button = E.button('x_range -')
                    xrange_down_button.onclick = ->
                        x_range = ecg_plt()._fullLayout.xaxis.range
                        if x_range[1] - x_range[0] <= 2
                            return
                        x_range[0] += 1
                        x_range[1] -= 1
                        ecg_plt().animate(
                            newXrange: x_range
                        )
                    xrange_up_button = E.button('x_range +')
                    xrange_up_button.onclick = ->
                        x_range = ecg_plt()._fullLayout.xaxis.range
                        if x_range[1] - x_range[0]  >= 10
                            return
                        x_range[0] -= 1
                        x_range[1] += 1
                        ecg_plt().animate(
                            newXrange: x_range
                        )
                    div.appendChild(xrange_down_button)
                    div.appendChild(xrange_up_button)

        else if data.type == 'BUTTON'
            template = document.createElement('template')
            template.innerHTML = data.html
            button = template.content.firstChild
            button.onclick = =>
                log("clicked button #{name}")
                result = JSON.stringify
                    name : button.innerHTML
                    state:
                        pointer: pointer
                @.send("BUTTON:#{result}")
            appendToBody(button)


        else if data.type == 'UPDATE'
            requestedUpdate = false
            u = JSON.parse(data.value)
            if u?
                if isShifting
                    pendingUpdate = u
                else
                    update(u)
        else
#            err('unknown data type: ')
            appendToBody(E.Div(data))
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

windowRect = null

update_callback = null
newStart = null
newStop = null


current_arrow = null

fixArrow = ({refresh} = {}) ->
    refresh ?= false
    arrow = pointerArrow()
    arrow.yref = 'y'
    if refresh or newStart == -1 # happens after going really fast and updating
#        setTimeout(->
        [newXrange, newYRange, newPointer, pointerLine, windowRect, newStart, newStop] = inc_calcs(ecg_plt(), 0)
    #            fixArrow()
    #        , 3000)
    #        new Promise(->)
    #    else
    y = ecg_plt().y().slice(newStart, newStop) #bc at edges pointer is not at center
    newy = y[Math.round(y.length / 2)]
#    log("setting new y to #{newy}")
    arrow.y = newy
    #    ecg_plt().animate(
    #        newAnnotations: [arrow]
    #        dur         : 10
    #    )
    current_arrow = arrow
    Plotly.relayout(ecg_plt(), {
        'annotations': current_annos.concat([arrow])
    })
#fixArrow = log_invokation fixArrow


shift = (pos) ->
    isShifting = true
    inc = increment * pos
    log('about to call inc_calcs')
    [newXrange, newYRange, newPointer, pointerLine, windowRect, newStart, newStop] = inc_calcs(ecg_plt(), inc)
    log('finished inc_calcs')
    pointer = newPointer
    pointerL = pointerLine
    update_check = ({stack} = {}) ->
        stack ?= false
        x = ecg_plt().x()
        x0 = x[0]
        xEnd = x.slice(-1)[0]
        dif = xEnd - x0
        if !pendingUpdate? and (not requestedUpdate) and (pointer > x0 + (dif * (.5 + RELOAD_THRESH)) or pointer < x0 + (dif * (.5 - RELOAD_THRESH)))
            ws.send("GET_UPDATE:#{pointer}")
            requestedUpdate = true
        else if stack
            update_callback = ->
                ws.send("GET_UPDATE:#{pointer}")
                requestedUpdate = true
    update_check = log_invokation update_check
    checkUp = ->
        if stopShifting
            log('stopShifting!')
            #            fixArrow()
            update_check(
                stack: true
            )
            isShifting = false
        fixArrow()
    checkUp = log_invokation checkUp
    log('starting main shift')
    ecg_plt().animate(
#        data_changes: [[2, pointerLine]] #maybe
        newXrange: newXrange
#                    newYRange: newYRange\
        dur      : DUR
        redraw   : false
    ).then((v)->
        log('finished main shift, checking if should update')
        update_check()
        log('finished checking if should update')
    ).then((v)->
        log('in next then (why another?)')
        if pendingUpdate?
            update(pendingUpdate)
    ).then((v) ->
        log('in final then')
        checkUp().then(->
            if not stopShifting
                shift(pos)
        )
    ).catch(checkUp)
shift = log_invokation shift


update = (u) ->
#            ibi_plt has nothing to do with pending update. Its just that it doesnt need to update that often, so this is a way to save resources and its roughly the update frequency that I want
    data = u.data
    current_annos = u.annotations
    ibi_plt().animate
        data_changes: [[1, windowRect]]
    the_update =
        data_changes  : [
            [0, data[0]],
            [1, data[1]],
            [2, data[2]]
        ]
        newAnnotations: current_annos.concat([current_arrow])
        dur: 1
    if u.yrange?
        the_update = merge(the_update, {newYrange: u.yrange})
    ecg_plt().animate(the_update).then((v)->
        fixArrow({refresh: true})
        pendingUpdate = null
        if update_callback?
            update_callback()
            update_callback = null
    ).catch((r)->
        fixArrow({refresh: true})
        pendingUpdate = null
        if update_callback?
            update_callback()
            update_callback = null
    )
update = log_invokation update