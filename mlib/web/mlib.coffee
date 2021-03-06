onload_funs = []
window.onload = ->
    onload_funs.map((f) -> f())

id = new Proxy({}, {
    get: (target, name) ->
        $('#' + name)[0]
})

tag = new Proxy({}, {
    get: (target, name) ->
        $(name)[0]
})

#noinspection JSUnusedGlobalSymbols
inner = new Proxy({}, {
    get: (target, name) ->
        id[name].innerHTML
})

GET = (url) ->
    Http = new XMLHttpRequest()
    Http.open("GET", url, false) # 3rd param blocks, but this is deprecated
    Http.send()
    Http.responseText
GET_async = (url, onResponse) ->
    Http = new XMLHttpRequest()
    Http.open("GET", url)
    Http.send()
    Http.onreadystatechange = ->
        if Http.readyState is 4
            if Http.status is 200
                onResponse(Http.responseText)
            else
                alert("bad HTTP request: url=#{url},status=#{Http.status},response=#{Http.responseText}")

wcGET = (url) ->
    t = "Unable to acquire kernel"
    t = GET(url) while t.includes("Unable to acquire kernel")
    t
wcGET_async = (url, onResponse) ->
    t = "Unable to acquire kernel"
    GET_async(url, (t) ->
        if t.includes("Unable to acquire kernel")
            wcGET_async(url, onResponse)
        else
            onResponse(t)
    )
Object.defineProperty(String::, "de_quote", {
    value   : `function de_quote() {
        return this.substring(1, this.length - 1)
    }`
    writable: true
})
#noinspection JSUnusedGlobalSymbols
forEachByTag = (tag, cb) => Array.from(document.getElementsByTagName(tag)).forEach(cb)
QueryURL = (url, args_dict) ->
    keys = Object.keys(args_dict)
    if keys.length then url = "#{url}?"
    for k in keys
        url = "#{url}#{encodeURI(k)}=#{encodeURI(args_dict[k])}&"
    if keys.length > 1
        url = url.substring(0, url.length - 1)
    url
Object.defineProperty(Element::, "setText", {
    value   : (t) ->
        switch @.tagName
            when "P" then @.innerHTML = t
            when "TEXTAREA" then @.value = t
            else
                throw "setText not coded for #{@.tagName}"
    writable: true
})
Object.defineProperty(Element::, "disappear", {
    value   : (just_hide) ->
        if !just_display? or not just_display
            if @fade_timer?
                clearInterval(@fade_timer)
                @fade_timer = null
            if @unfadetimer?
                clearInterval(@unfadetimer)
                @unfadetimer = null
        @.op = 0
        if (@.style.display != 'none')
            @._default_display = getComputedStyle(@).display
        if just_hide? and just_hide
            @.style.visibility = 'hidden'
        else
            @.style.display = 'none'
    writable: true
})
Object.defineProperty(Element::, "setFadeInterval", {
    value   : (interval) ->
        @fadeInterval = interval
    writable: true
})
Object.defineProperty(Element::, "fade", {
    value   : (onFinish, just_hide) ->
        if !@fadeInterval?
            @fadeInterval = 50
        if (!@fade_timer?) and @style.display != 'none' and @style.visibility != 'hidden'
            if @unfadetimer?
                clearInterval(@unfadetimer)
                @unfadetimer = null
            else
                @op = 1 # initial opacity
            @fade_timer = setInterval(=>
                if @op <= 0.01
                    @op = 0
                    clearInterval(@fade_timer)
                    if @just_hide? and just_hide
                        @style.visibility = 'hidden'
                    else
                        @.disappear()
                    @fade_timer = null
                    if onFinish?
                        onFinish()
                @op -= Math.max(@op * 0.1, 0)
            , @fadeInterval)
        else
            if onFinish?
                onFinish()
    writable: true
})
Object.defineProperty(Element::, "appear", {
    value   : (just_display, but_hidden)->
        if !just_display? or not just_display
            if @fade_timer?
                clearInterval(@fade_timer)
                @fade_timer = null
            if @unfadetimer?
                clearInterval(@unfadetimer)
                @unfadetimer = null
            @.op = 1
        if but_hidden? and but_hidden
            @.style.visibility = 'hidden'
        if @.style.display is 'none'
            if @.hasAttribute('data-display')
                @.style.display = @.getAttribute('data-display')
            else if (@._default_display)
                @.style.display = @._default_display
            else @.style.display = 'block'
    writable: true
})
Object.defineProperty(Element::, "unfade", {
    value   : (onFinish) ->
        if !@fadeInterval?
            @fadeInterval = 50
        if (!@unfadetimer?) and (@fade_timer? or @.style.display == 'none' or @.style.visibility == 'hidden')
            if @fade_timer?
                clearInterval(@fade_timer)
                @fade_timer = null
            else
                @op = 0 # initial opacity
            @.appear(true)
            if @.style.visibility == 'hidden'
                @.style.visibility = 'visible'
            @unfadetimer = setInterval(=>
                if @op >= 1
                    clearInterval(@unfadetimer)
                    @unfadetimer = null
                    if onFinish?
                        onFinish()
                @op += Math.max(Math.min(@op * 0.1, 1), 0.01)
            , @fadeInterval)
        else
            if onFinish?
                onFinish()
    writable: true
})
Object.defineProperty(Element::, "op", {
    get: () ->
        Number(@.style.opacity)
    set: (op) ->
        @.style.opacity = op
        @.style.filter = 'alpha(opacity=' + op * 100 + ")"
# writable: true
})
Object.defineProperty(Element::, "alternate", {
    value   : (htmls, period) ->
        this._stop_alternating = false
        i = 0
        alt_recurse = =>
            this.innerHTML = htmls[i]
            if i is (htmls.length - 1)
                i = 0
            else
                i++
            setTimeout(=>
                if !this._stop_alternating
                    alt_recurse()
            , period)
        alt_recurse()
    writable: true
})
Object.defineProperty(Element::, "stop_alternating", {
    value   : () ->
        this._stop_alternating = true
    writable: true
})
Object.defineProperty(Element::, "type", {
    value   : (ss, onFinish) ->
        s = ss.charAt(0)
        for i in [1..ss.length - 1]
            if ss.charAt(i) is ' '
                s = s + ' '
            else
                s = s + '&nbsp'
        i = 0
        @type_timer = setInterval(=>
            @innerHTML = s
            if i is ss.length - 1
                clearInterval(@type_timer)
                if onFinish? then onFinish()
            i += 1
            if s.substr(i, 5) == '&nbsp'
                s = (s.substring(0, i) + ss.charAt(i) + s.substring(i + 5))
            else
                s = s.substring(0, i) + ss.charAt(i) + s.substring(i + 1)
        , 20)
    writable: true
})
path_join = (...args) ->
    args.map((part, i) ->
        if i == 0 then part.trim().replace(/[\/]*$/g, '') else part.trim().replace(/(^[\/]*|[\/]*$)/g, '')).filter((x) -> x.length).join('/')


tic = Date.now()
retic = () ->
    tic = Date.now()
log = (s) ->
    toc = Date.now()
    console.log("[#{(toc - tic) / 1000}]#{s}")

bool = (s) -> JSON.parse s.toLowerCase()

keydown = (f) ->
    $(document).keydown (e) ->
#        log("#{e.key} down")
        f(e)
keyup = (f) ->
    $(document).keyup (e) ->
#        log("#{e.key} up")
        f(e)

Key = (keyCode, str) -> {keyCode, str}
SPACE_BAR = Key(32, "Space Bar")
RIGHT_ARROW = Key(39, "Right Arrow Key")
LEFT_ARROW = Key(37, "Left Arrow Key")
UP_ARROW = Key(38, "Right Arrow Key")
DOWN_ARROW = Key(40, "Left Arrow Key")
S_KEY = Key(83, "S Key")
C_KEY = Key(67, "C Key")
N_KEY = Key(78, "N Key")
#noinspection JSUnusedGlobalSymbols
just_email_href_stuff = ->
#  id.link.href = "#{id.link.href}body=#{encodeURI(template)}"


openFullscreen = (DOM_e) ->
    if (DOM_e.requestFullscreen)
        DOM_e.requestFullscreen()
    else if (DOM_e.mozRequestFullScreen)  #/* Firefox */
        DOM_e.mozRequestFullScreen()
    else if (DOM_e.webkitRequestFullscreen)  #/* Chrome, Safari and Opera */
        DOM_e.webkitRequestFullscreen()
    else if (DOM_e.msRequestFullscreen)  #/* IE/Edge */
        DOM_e.msRequestFullscreen()

tap = (o, fn) -> fn(o); o
merge = (xs...) ->
    if xs?.length > 0
        tap {}, (m) -> m[k] = v for k, v of x for x in xs

#ipapi doesnt allow CORS
#myIP = ->
#    JSON.parse(GET('https://ipapi.co/json/')).ip
#myIP_async = (handler) ->
#    GET_async('https://ipapi.co/json/',(t)->
#        handler(JSON.parse(t).ip)
#    )
_parse_ip = (raw) ->
    raw.split('\n').filter((l) -> l.startsWith('ip'))[0].replace('ip=', '')
myIP = ->
    _parse_ip(GET('https://www.cloudflare.com/cdn-cgi/trace'))
myIP_async = (handler) ->
    GET_async('https://www.cloudflare.com/cdn-cgi/trace', (t)->
        handler(_parse_ip(t))
    )

center_str = (str, marker) ->
    mi = str.indexOf(marker) + 1
    while mi < (str.length / 2 + 0.5)
        str = '&nbsp' + str
        mi = str.indexOf(marker) + 1
    while mi > (str.length / 2 + 0.5)
        str = str + '&nbsp'
        mi = str.indexOf(marker) + 1
    if str.length % 2 == 0
        str.replace(marker, '&nbsp')
    else
        str.replace(marker, '')

appendToBody = (e) ->
    tag.body.appendChild(e)

E = new Proxy({}, {
    get: (target, name) ->
        (my_inner) ->
            e = document.createElement(name)
            e.innerHTML = my_inner
            e
})

Object.defineProperty(String::, "afterFirst", {
    value   : `function afterFirst(c) {
        return this.substring(this.indexOf(c) + 1)
    }`
    writable: true
})
Object.defineProperty(String::, "beforeFirst", {
    value   : `function afterFirst(c) {
        return this.substring(0, this.indexOf(c) + 1)
    }`
    writable: true
})


openTab = (evt, tabName) ->
    tabcontent = document.getElementsByClassName("tabcontent")
    for content in tabcontent
        content.setFadeInterval(5)
        #        content.fade()
        content.disappear()

    tablinks = document.getElementsByClassName("tablinks")
    for link in tablinks
        link.className = link.className.replace(" active", "")

    evt.currentTarget.className += " active"
    #    id[tabName].unfade()
    id[tabName].appear()
    for c in id[tabName].children[0].children
        if c.children.length > 0 and c.children[0].className.includes('plotly-graph-div')
#            hopefully this will fix the weird bug that causes these plots to regularly hide thier lines
            Plotly.relayout(c.children[0], {
#                'xaxis.autorange': true,
#                'yaxis.autorange': true
            });
#            and c.children[0].className?

openSocketClient = ({url, onopen, onmessage, onclose}) ->
    ws = new WebSocket(url)
    ws.onopen = -> onopen.call(ws)
    ws.onmessage = onmessage
    ws.onclose = onclose
    ws


autoYRange = (ar) ->
    mn = Math.min(ar)
    mx = Math.max(ar)
    dif = mx - mn
    ten = dif * 0.1
    mn = mn - ten
    mx = mx + ten
    return [mn, mx]

Object.defineProperty(String::, "shorten", {
    value   : `function shorten(maxlen) {
        if (this.length <= maxlen) {return this} else {return this.slice(0, maxlen) + ' ... '}
    }`
    writable: true
})

Object.defineProperty(Object::, "def", {
    value: `function def(functions) {
        for (fun_name in functions) {
            Object.defineProperty(this, fun_name, {
                value: functions[fun_name]
            })
        }
        return this
    }`
})

log_invokation = (f) ->
    ff = (...args) ->
        s = f.name + '()'
        log("Invoking #{s}...")
        r = f(...args)
        log("Finished #{s}!")
        return r
    ff.name = f.name
    return ff

extend = (object, properties) ->
    for key, val of properties
        object[key] = val
    object

merge = (...objects) ->
    r = {}
    for o in objects
        extend(r, o)
    r