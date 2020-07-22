/*!			//GEN
 * Platform.js			//GEN
 * Copyright 2014-2020 Benjamin Tan			//GEN
 * Copyright 2011-2013 John-David Dalton			//GEN
 * Available under MIT license			//GEN
 */			//GEN
;(function() {			//GEN
    'use strict';			//GEN
			//GEN
    /** Used to determine if values are of the language type `Object`. */			//GEN
    var objectTypes = {			//GEN
        'function': true,			//GEN
        'object': true			//GEN
    };			//GEN
			//GEN
    /** Used as a reference to the global object. */			//GEN
    var root = (objectTypes[typeof window] && window) || this;			//GEN
			//GEN
    /** Backup possible global object. */			//GEN
    var oldRoot = root;			//GEN
			//GEN
    /** Detect free variable `exports`. */			//GEN
    var freeExports = objectTypes[typeof exports] && exports;			//GEN
			//GEN
    /** Detect free variable `module`. */			//GEN
    var freeModule = objectTypes[typeof module] && module && !module.nodeType && module;			//GEN
			//GEN
    /** Detect free variable `global` from Node.js or Browserified code and use it as `root`. */			//GEN
    var freeGlobal = freeExports && freeModule && typeof global == 'object' && global;			//GEN
    if (freeGlobal && (freeGlobal.global === freeGlobal || freeGlobal.window === freeGlobal || freeGlobal.self === freeGlobal)) {			//GEN
        root = freeGlobal;			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * Used as the maximum length of an array-like object.			//GEN
     * See the [ES6 spec](http://people.mozilla.org/~jorendorff/es6-draft.html#sec-tolength)			//GEN
     * for more details.			//GEN
     */			//GEN
    var maxSafeInteger = Math.pow(2, 53) - 1;			//GEN
			//GEN
    /** Regular expression to detect Opera. */			//GEN
    var reOpera = /\bOpera/;			//GEN
			//GEN
    /** Possible global object. */			//GEN
    var thisBinding = this;			//GEN
			//GEN
    /** Used for native method references. */			//GEN
    var objectProto = Object.prototype;			//GEN
			//GEN
    /** Used to check for own properties of an object. */			//GEN
    var hasOwnProperty = objectProto.hasOwnProperty;			//GEN
			//GEN
    /** Used to resolve the internal `[[Class]]` of values. */			//GEN
    var toString = objectProto.toString;			//GEN
			//GEN
    /*--------------------------------------------------------------------------*/			//GEN
			//GEN
    /**			//GEN
     * Capitalizes a string value.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {string} string The string to capitalize.			//GEN
     * @returns {string} The capitalized string.			//GEN
     */			//GEN
    function capitalize(string) {			//GEN
        string = String(string);			//GEN
        return string.charAt(0).toUpperCase() + string.slice(1);			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * A utility function to clean up the OS name.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {string} os The OS name to clean up.			//GEN
     * @param {string} [pattern] A `RegExp` pattern matching the OS name.			//GEN
     * @param {string} [label] A label for the OS.			//GEN
     */			//GEN
    function cleanupOS(os, pattern, label) {			//GEN
        // Platform tokens are defined at:			//GEN
        // http://msdn.microsoft.com/en-us/library/ms537503(VS.85).aspx			//GEN
        // http://web.archive.org/web/20081122053950/http://msdn.microsoft.com/en-us/library/ms537503(VS.85).aspx			//GEN
        var data = {			//GEN
            '10.0': '10',			//GEN
            '6.4':  '10 Technical Preview',			//GEN
            '6.3':  '8.1',			//GEN
            '6.2':  '8',			//GEN
            '6.1':  'Server 2008 R2 / 7',			//GEN
            '6.0':  'Server 2008 / Vista',			//GEN
            '5.2':  'Server 2003 / XP 64-bit',			//GEN
            '5.1':  'XP',			//GEN
            '5.01': '2000 SP1',			//GEN
            '5.0':  '2000',			//GEN
            '4.0':  'NT',			//GEN
            '4.90': 'ME'			//GEN
        };			//GEN
        // Detect Windows version from platform tokens.			//GEN
        if (pattern && label && /^Win/i.test(os) && !/^Windows Phone /i.test(os) &&			//GEN
            (data = data[/[\d.]+$/.exec(os)])) {			//GEN
            os = 'Windows ' + data;			//GEN
        }			//GEN
        // Correct character case and cleanup string.			//GEN
        os = String(os);			//GEN
			//GEN
        if (pattern && label) {			//GEN
            os = os.replace(RegExp(pattern, 'i'), label);			//GEN
        }			//GEN
			//GEN
        os = format(			//GEN
            os.replace(/ ce$/i, ' CE')			//GEN
                .replace(/\bhpw/i, 'web')			//GEN
                .replace(/\bMacintosh\b/, 'Mac OS')			//GEN
                .replace(/_PowerPC\b/i, ' OS')			//GEN
                .replace(/\b(OS X) [^ \d]+/i, '$1')			//GEN
                .replace(/\bMac (OS X)\b/, '$1')			//GEN
                .replace(/\/(\d)/, ' $1')			//GEN
                .replace(/_/g, '.')			//GEN
                .replace(/(?: BePC|[ .]*fc[ \d.]+)$/i, '')			//GEN
                .replace(/\bx86\.64\b/gi, 'x86_64')			//GEN
                .replace(/\b(Windows Phone) OS\b/, '$1')			//GEN
                .replace(/\b(Chrome OS \w+) [\d.]+\b/, '$1')			//GEN
                .split(' on ')[0]			//GEN
        );			//GEN
			//GEN
        return os;			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * An iteration utility for arrays and objects.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {Array|Object} object The object to iterate over.			//GEN
     * @param {Function} callback The function called per iteration.			//GEN
     */			//GEN
    function each(object, callback) {			//GEN
        var index = -1,			//GEN
            length = object ? object.length : 0;			//GEN
			//GEN
        if (typeof length == 'number' && length > -1 && length <= maxSafeInteger) {			//GEN
            while (++index < length) {			//GEN
                callback(object[index], index, object);			//GEN
            }			//GEN
        } else {			//GEN
            forOwn(object, callback);			//GEN
        }			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * Trim and conditionally capitalize string values.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {string} string The string to format.			//GEN
     * @returns {string} The formatted string.			//GEN
     */			//GEN
    function format(string) {			//GEN
        string = trim(string);			//GEN
        return /^(?:webOS|i(?:OS|P))/.test(string)			//GEN
            ? string			//GEN
            : capitalize(string);			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * Iterates over an object's own properties, executing the `callback` for each.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {Object} object The object to iterate over.			//GEN
     * @param {Function} callback The function executed per own property.			//GEN
     */			//GEN
    function forOwn(object, callback) {			//GEN
        for (var key in object) {			//GEN
            if (hasOwnProperty.call(object, key)) {			//GEN
                callback(object[key], key, object);			//GEN
            }			//GEN
        }			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * Gets the internal `[[Class]]` of a value.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {*} value The value.			//GEN
     * @returns {string} The `[[Class]]`.			//GEN
     */			//GEN
    function getClassOf(value) {			//GEN
        return value == null			//GEN
            ? capitalize(value)			//GEN
            : toString.call(value).slice(8, -1);			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * Host objects can return type values that are different from their actual			//GEN
     * data type. The objects we are concerned with usually return non-primitive			//GEN
     * types of "object", "function", or "unknown".			//GEN
     *			//GEN
     * @private			//GEN
     * @param {*} object The owner of the property.			//GEN
     * @param {string} property The property to check.			//GEN
     * @returns {boolean} Returns `true` if the property value is a non-primitive, else `false`.			//GEN
     */			//GEN
    function isHostType(object, property) {			//GEN
        var type = object != null ? typeof object[property] : 'number';			//GEN
        return !/^(?:boolean|number|string|undefined)$/.test(type) &&			//GEN
            (type == 'object' ? !!object[property] : true);			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * Prepares a string for use in a `RegExp` by making hyphens and spaces optional.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {string} string The string to qualify.			//GEN
     * @returns {string} The qualified string.			//GEN
     */			//GEN
    function qualify(string) {			//GEN
        return String(string).replace(/([ -])(?!$)/g, '$1?');			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * A bare-bones `Array#reduce` like utility function.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {Array} array The array to iterate over.			//GEN
     * @param {Function} callback The function called per iteration.			//GEN
     * @returns {*} The accumulated result.			//GEN
     */			//GEN
    function reduce(array, callback) {			//GEN
        var accumulator = null;			//GEN
        each(array, function(value, index) {			//GEN
            accumulator = callback(accumulator, value, index, array);			//GEN
        });			//GEN
        return accumulator;			//GEN
    }			//GEN
			//GEN
    /**			//GEN
     * Removes leading and trailing whitespace from a string.			//GEN
     *			//GEN
     * @private			//GEN
     * @param {string} string The string to trim.			//GEN
     * @returns {string} The trimmed string.			//GEN
     */			//GEN
    function trim(string) {			//GEN
        return String(string).replace(/^ +| +$/g, '');			//GEN
    }			//GEN
			//GEN
    /*--------------------------------------------------------------------------*/			//GEN
			//GEN
    /**			//GEN
     * Creates a new platform object.			//GEN
     *			//GEN
     * @memberOf platform			//GEN
     * @param {Object|string} [ua=navigator.userAgent] The user agent string or			//GEN
     *  context object.			//GEN
     * @returns {Object} A platform object.			//GEN
     */			//GEN
    function parse(ua) {			//GEN
			//GEN
        /** The environment context object. */			//GEN
        var context = root;			//GEN
			//GEN
        /** Used to flag when a custom context is provided. */			//GEN
        var isCustomContext = ua && typeof ua == 'object' && getClassOf(ua) != 'String';			//GEN
			//GEN
        // Juggle arguments.			//GEN
        if (isCustomContext) {			//GEN
            context = ua;			//GEN
            ua = null;			//GEN
        }			//GEN
			//GEN
        /** Browser navigator object. */			//GEN
        var nav = context.navigator || {};			//GEN
			//GEN
        /** Browser user agent string. */			//GEN
        var userAgent = nav.userAgent || '';			//GEN
			//GEN
        ua || (ua = userAgent);			//GEN
			//GEN
        /** Used to flag when `thisBinding` is the [ModuleScope]. */			//GEN
        var isModuleScope = isCustomContext || thisBinding == oldRoot;			//GEN
			//GEN
        /** Used to detect if browser is like Chrome. */			//GEN
        var likeChrome = isCustomContext			//GEN
            ? !!nav.likeChrome			//GEN
            : /\bChrome\b/.test(ua) && !/internal|\n/i.test(toString.toString());			//GEN
			//GEN
        /** Internal `[[Class]]` value shortcuts. */			//GEN
        var objectClass = 'Object',			//GEN
            airRuntimeClass = isCustomContext ? objectClass : 'ScriptBridgingProxyObject',			//GEN
            enviroClass = isCustomContext ? objectClass : 'Environment',			//GEN
            javaClass = (isCustomContext && context.java) ? 'JavaPackage' : getClassOf(context.java),			//GEN
            phantomClass = isCustomContext ? objectClass : 'RuntimeObject';			//GEN
			//GEN
        /** Detect Java environments. */			//GEN
        var java = /\bJava/.test(javaClass) && context.java;			//GEN
			//GEN
        /** Detect Rhino. */			//GEN
        var rhino = java && getClassOf(context.environment) == enviroClass;			//GEN
			//GEN
        /** A character to represent alpha. */			//GEN
        var alpha = java ? 'a' : '\u03b1';			//GEN
			//GEN
        /** A character to represent beta. */			//GEN
        var beta = java ? 'b' : '\u03b2';			//GEN
			//GEN
        /** Browser document object. */			//GEN
        var doc = context.document || {};			//GEN
			//GEN
        /**			//GEN
         * Detect Opera browser (Presto-based).			//GEN
         * http://www.howtocreate.co.uk/operaStuff/operaObject.html			//GEN
         * http://dev.opera.com/articles/view/opera-mini-web-content-authoring-guidelines/#operamini			//GEN
         */			//GEN
        var opera = context.operamini || context.opera;			//GEN
			//GEN
        /** Opera `[[Class]]`. */			//GEN
        var operaClass = reOpera.test(operaClass = (isCustomContext && opera) ? opera['[[Class]]'] : getClassOf(opera))			//GEN
            ? operaClass			//GEN
            : (opera = null);			//GEN
			//GEN
        /*------------------------------------------------------------------------*/			//GEN
			//GEN
        /** Temporary variable used over the script's lifetime. */			//GEN
        var data;			//GEN
			//GEN
        /** The CPU architecture. */			//GEN
        var arch = ua;			//GEN
			//GEN
        /** Platform description array. */			//GEN
        var description = [];			//GEN
			//GEN
        /** Platform alpha/beta indicator. */			//GEN
        var prerelease = null;			//GEN
			//GEN
        /** A flag to indicate that environment features should be used to resolve the platform. */			//GEN
        var useFeatures = ua == userAgent;			//GEN
			//GEN
        /** The browser/environment version. */			//GEN
        var version = useFeatures && opera && typeof opera.version == 'function' && opera.version();			//GEN
			//GEN
        /** A flag to indicate if the OS ends with "/ Version" */			//GEN
        var isSpecialCasedOS;			//GEN
			//GEN
        /* Detectable layout engines (order is important). */			//GEN
        var layout = getLayout([			//GEN
            { 'label': 'EdgeHTML', 'pattern': 'Edge' },			//GEN
            'Trident',			//GEN
            { 'label': 'WebKit', 'pattern': 'AppleWebKit' },			//GEN
            'iCab',			//GEN
            'Presto',			//GEN
            'NetFront',			//GEN
            'Tasman',			//GEN
            'KHTML',			//GEN
            'Gecko'			//GEN
        ]);			//GEN
			//GEN
        /* Detectable browser names (order is important). */			//GEN
        var name = getName([			//GEN
            'Adobe AIR',			//GEN
            'Arora',			//GEN
            'Avant Browser',			//GEN
            'Breach',			//GEN
            'Camino',			//GEN
            'Electron',			//GEN
            'Epiphany',			//GEN
            'Fennec',			//GEN
            'Flock',			//GEN
            'Galeon',			//GEN
            'GreenBrowser',			//GEN
            'iCab',			//GEN
            'Iceweasel',			//GEN
            'K-Meleon',			//GEN
            'Konqueror',			//GEN
            'Lunascape',			//GEN
            'Maxthon',			//GEN
            { 'label': 'Microsoft Edge', 'pattern': '(?:Edge|Edg|EdgA|EdgiOS)' },			//GEN
            'Midori',			//GEN
            'Nook Browser',			//GEN
            'PaleMoon',			//GEN
            'PhantomJS',			//GEN
            'Raven',			//GEN
            'Rekonq',			//GEN
            'RockMelt',			//GEN
            { 'label': 'Samsung Internet', 'pattern': 'SamsungBrowser' },			//GEN
            'SeaMonkey',			//GEN
            { 'label': 'Silk', 'pattern': '(?:Cloud9|Silk-Accelerated)' },			//GEN
            'Sleipnir',			//GEN
            'SlimBrowser',			//GEN
            { 'label': 'SRWare Iron', 'pattern': 'Iron' },			//GEN
            'Sunrise',			//GEN
            'Swiftfox',			//GEN
            'Vivaldi',			//GEN
            'Waterfox',			//GEN
            'WebPositive',			//GEN
            { 'label': 'Yandex Browser', 'pattern': 'YaBrowser' },			//GEN
            { 'label': 'UC Browser', 'pattern': 'UCBrowser' },			//GEN
            'Opera Mini',			//GEN
            { 'label': 'Opera Mini', 'pattern': 'OPiOS' },			//GEN
            'Opera',			//GEN
            { 'label': 'Opera', 'pattern': 'OPR' },			//GEN
            'Chromium',			//GEN
            'Chrome',			//GEN
            { 'label': 'Chrome', 'pattern': '(?:HeadlessChrome)' },			//GEN
            { 'label': 'Chrome Mobile', 'pattern': '(?:CriOS|CrMo)' },			//GEN
            { 'label': 'Firefox', 'pattern': '(?:Firefox|Minefield)' },			//GEN
            { 'label': 'Firefox for iOS', 'pattern': 'FxiOS' },			//GEN
            { 'label': 'IE', 'pattern': 'IEMobile' },			//GEN
            { 'label': 'IE', 'pattern': 'MSIE' },			//GEN
            'Safari'			//GEN
        ]);			//GEN
			//GEN
        /* Detectable products (order is important). */			//GEN
        var product = getProduct([			//GEN
            { 'label': 'BlackBerry', 'pattern': 'BB10' },			//GEN
            'BlackBerry',			//GEN
            { 'label': 'Galaxy S', 'pattern': 'GT-I9000' },			//GEN
            { 'label': 'Galaxy S2', 'pattern': 'GT-I9100' },			//GEN
            { 'label': 'Galaxy S3', 'pattern': 'GT-I9300' },			//GEN
            { 'label': 'Galaxy S4', 'pattern': 'GT-I9500' },			//GEN
            { 'label': 'Galaxy S5', 'pattern': 'SM-G900' },			//GEN
            { 'label': 'Galaxy S6', 'pattern': 'SM-G920' },			//GEN
            { 'label': 'Galaxy S6 Edge', 'pattern': 'SM-G925' },			//GEN
            { 'label': 'Galaxy S7', 'pattern': 'SM-G930' },			//GEN
            { 'label': 'Galaxy S7 Edge', 'pattern': 'SM-G935' },			//GEN
            'Google TV',			//GEN
            'Lumia',			//GEN
            'iPad',			//GEN
            'iPod',			//GEN
            'iPhone',			//GEN
            'Kindle',			//GEN
            { 'label': 'Kindle Fire', 'pattern': '(?:Cloud9|Silk-Accelerated)' },			//GEN
            'Nexus',			//GEN
            'Nook',			//GEN
            'PlayBook',			//GEN
            'PlayStation Vita',			//GEN
            'PlayStation',			//GEN
            'TouchPad',			//GEN
            'Transformer',			//GEN
            { 'label': 'Wii U', 'pattern': 'WiiU' },			//GEN
            'Wii',			//GEN
            'Xbox One',			//GEN
            { 'label': 'Xbox 360', 'pattern': 'Xbox' },			//GEN
            'Xoom'			//GEN
        ]);			//GEN
			//GEN
        /* Detectable manufacturers. */			//GEN
        var manufacturer = getManufacturer({			//GEN
            'Apple': { 'iPad': 1, 'iPhone': 1, 'iPod': 1 },			//GEN
            'Alcatel': {},			//GEN
            'Archos': {},			//GEN
            'Amazon': { 'Kindle': 1, 'Kindle Fire': 1 },			//GEN
            'Asus': { 'Transformer': 1 },			//GEN
            'Barnes & Noble': { 'Nook': 1 },			//GEN
            'BlackBerry': { 'PlayBook': 1 },			//GEN
            'Google': { 'Google TV': 1, 'Nexus': 1 },			//GEN
            'HP': { 'TouchPad': 1 },			//GEN
            'HTC': {},			//GEN
            'LG': {},			//GEN
            'Microsoft': { 'Xbox': 1, 'Xbox One': 1 },			//GEN
            'Motorola': { 'Xoom': 1 },			//GEN
            'Nintendo': { 'Wii U': 1,  'Wii': 1 },			//GEN
            'Nokia': { 'Lumia': 1 },			//GEN
            'Samsung': { 'Galaxy S': 1, 'Galaxy S2': 1, 'Galaxy S3': 1, 'Galaxy S4': 1 },			//GEN
            'Sony': { 'PlayStation': 1, 'PlayStation Vita': 1 }			//GEN
        });			//GEN
			//GEN
        /* Detectable operating systems (order is important). */			//GEN
        var os = getOS([			//GEN
            'Windows Phone',			//GEN
            'KaiOS',			//GEN
            'Android',			//GEN
            'CentOS',			//GEN
            { 'label': 'Chrome OS', 'pattern': 'CrOS' },			//GEN
            'Debian',			//GEN
            { 'label': 'DragonFly BSD', 'pattern': 'DragonFly' },			//GEN
            'Fedora',			//GEN
            'FreeBSD',			//GEN
            'Gentoo',			//GEN
            'Haiku',			//GEN
            'Kubuntu',			//GEN
            'Linux Mint',			//GEN
            'OpenBSD',			//GEN
            'Red Hat',			//GEN
            'SuSE',			//GEN
            'Ubuntu',			//GEN
            'Xubuntu',			//GEN
            'Cygwin',			//GEN
            'Symbian OS',			//GEN
            'hpwOS',			//GEN
            'webOS ',			//GEN
            'webOS',			//GEN
            'Tablet OS',			//GEN
            'Tizen',			//GEN
            'Linux',			//GEN
            'Mac OS X',			//GEN
            'Macintosh',			//GEN
            'Mac',			//GEN
            'Windows 98;',			//GEN
            'Windows '			//GEN
        ]);			//GEN
			//GEN
        /*------------------------------------------------------------------------*/			//GEN
			//GEN
        /**			//GEN
         * Picks the layout engine from an array of guesses.			//GEN
         *			//GEN
         * @private			//GEN
         * @param {Array} guesses An array of guesses.			//GEN
         * @returns {null|string} The detected layout engine.			//GEN
         */			//GEN
        function getLayout(guesses) {			//GEN
            return reduce(guesses, function(result, guess) {			//GEN
                return result || RegExp('\\b' + (			//GEN
                    guess.pattern || qualify(guess)			//GEN
                ) + '\\b', 'i').exec(ua) && (guess.label || guess);			//GEN
            });			//GEN
        }			//GEN
			//GEN
        /**			//GEN
         * Picks the manufacturer from an array of guesses.			//GEN
         *			//GEN
         * @private			//GEN
         * @param {Array} guesses An object of guesses.			//GEN
         * @returns {null|string} The detected manufacturer.			//GEN
         */			//GEN
        function getManufacturer(guesses) {			//GEN
            return reduce(guesses, function(result, value, key) {			//GEN
                // Lookup the manufacturer by product or scan the UA for the manufacturer.			//GEN
                return result || (			//GEN
                    value[product] ||			//GEN
                    value[/^[a-z]+(?: +[a-z]+\b)*/i.exec(product)] ||			//GEN
                    RegExp('\\b' + qualify(key) + '(?:\\b|\\w*\\d)', 'i').exec(ua)			//GEN
                ) && key;			//GEN
            });			//GEN
        }			//GEN
			//GEN
        /**			//GEN
         * Picks the browser name from an array of guesses.			//GEN
         *			//GEN
         * @private			//GEN
         * @param {Array} guesses An array of guesses.			//GEN
         * @returns {null|string} The detected browser name.			//GEN
         */			//GEN
        function getName(guesses) {			//GEN
            return reduce(guesses, function(result, guess) {			//GEN
                return result || RegExp('\\b' + (			//GEN
                    guess.pattern || qualify(guess)			//GEN
                ) + '\\b', 'i').exec(ua) && (guess.label || guess);			//GEN
            });			//GEN
        }			//GEN
			//GEN
        /**			//GEN
         * Picks the OS name from an array of guesses.			//GEN
         *			//GEN
         * @private			//GEN
         * @param {Array} guesses An array of guesses.			//GEN
         * @returns {null|string} The detected OS name.			//GEN
         */			//GEN
        function getOS(guesses) {			//GEN
            return reduce(guesses, function(result, guess) {			//GEN
                var pattern = guess.pattern || qualify(guess);			//GEN
                if (!result && (result =			//GEN
                        RegExp('\\b' + pattern + '(?:/[\\d.]+|[ \\w.]*)', 'i').exec(ua)			//GEN
                )) {			//GEN
                    result = cleanupOS(result, pattern, guess.label || guess);			//GEN
                }			//GEN
                return result;			//GEN
            });			//GEN
        }			//GEN
			//GEN
        /**			//GEN
         * Picks the product name from an array of guesses.			//GEN
         *			//GEN
         * @private			//GEN
         * @param {Array} guesses An array of guesses.			//GEN
         * @returns {null|string} The detected product name.			//GEN
         */			//GEN
        function getProduct(guesses) {			//GEN
            return reduce(guesses, function(result, guess) {			//GEN
                var pattern = guess.pattern || qualify(guess);			//GEN
                if (!result && (result =			//GEN
                        RegExp('\\b' + pattern + ' *\\d+[.\\w_]*', 'i').exec(ua) ||			//GEN
                        RegExp('\\b' + pattern + ' *\\w+-[\\w]*', 'i').exec(ua) ||			//GEN
                        RegExp('\\b' + pattern + '(?:; *(?:[a-z]+[_-])?[a-z]+\\d+|[^ ();-]*)', 'i').exec(ua)			//GEN
                )) {			//GEN
                    // Split by forward slash and append product version if needed.			//GEN
                    if ((result = String((guess.label && !RegExp(pattern, 'i').test(guess.label)) ? guess.label : result).split('/'))[1] && !/[\d.]+/.test(result[0])) {			//GEN
                        result[0] += ' ' + result[1];			//GEN
                    }			//GEN
                    // Correct character case and cleanup string.			//GEN
                    guess = guess.label || guess;			//GEN
                    result = format(result[0]			//GEN
                        .replace(RegExp(pattern, 'i'), guess)			//GEN
                        .replace(RegExp('; *(?:' + guess + '[_-])?', 'i'), ' ')			//GEN
                        .replace(RegExp('(' + guess + ')[-_.]?(\\w)', 'i'), '$1 $2'));			//GEN
                }			//GEN
                return result;			//GEN
            });			//GEN
        }			//GEN
			//GEN
        /**			//GEN
         * Resolves the version using an array of UA patterns.			//GEN
         *			//GEN
         * @private			//GEN
         * @param {Array} patterns An array of UA patterns.			//GEN
         * @returns {null|string} The detected version.			//GEN
         */			//GEN
        function getVersion(patterns) {			//GEN
            return reduce(patterns, function(result, pattern) {			//GEN
                return result || (RegExp(pattern +			//GEN
                    '(?:-[\\d.]+/|(?: for [\\w-]+)?[ /-])([\\d.]+[^ ();/_-]*)', 'i').exec(ua) || 0)[1] || null;			//GEN
            });			//GEN
        }			//GEN
			//GEN
        /**			//GEN
         * Returns `platform.description` when the platform object is coerced to a string.			//GEN
         *			//GEN
         * @name toString			//GEN
         * @memberOf platform			//GEN
         * @returns {string} Returns `platform.description` if available, else an empty string.			//GEN
         */			//GEN
        function toStringPlatform() {			//GEN
            return this.description || '';			//GEN
        }			//GEN
			//GEN
        /*------------------------------------------------------------------------*/			//GEN
			//GEN
        // Convert layout to an array so we can add extra details.			//GEN
        layout && (layout = [layout]);			//GEN
			//GEN
        // Detect product names that contain their manufacturer's name.			//GEN
        if (manufacturer && !product) {			//GEN
            product = getProduct([manufacturer]);			//GEN
        }			//GEN
        // Clean up Google TV.			//GEN
        if ((data = /\bGoogle TV\b/.exec(product))) {			//GEN
            product = data[0];			//GEN
        }			//GEN
        // Detect simulators.			//GEN
        if (/\bSimulator\b/i.test(ua)) {			//GEN
            product = (product ? product + ' ' : '') + 'Simulator';			//GEN
        }			//GEN
        // Detect Android products.			//GEN
        // Browsers on Android devices typically provide their product IDS after "Android;"			//GEN
        // up to "Build" or ") AppleWebKit".			//GEN
        // Example:			//GEN
        // "Mozilla/5.0 (Linux; Android 8.1.0; Moto G (5) Plus) AppleWebKit/537.36			//GEN
        // (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36"			//GEN
        if (/\bAndroid\b/.test(os) && !product &&			//GEN
            (data = /\bAndroid[^;]*;(.*?)(?:Build|\) AppleWebKit)\b/i.exec(ua))) {			//GEN
            product = trim(data[1])			//GEN
                    // Replace any language codes (eg. "en-US").			//GEN
                    .replace(/^[a-z]{2}-[a-z]{2};\s*/i, '')			//GEN
                || null;			//GEN
        }			//GEN
        // Detect Opera Mini 8+ running in Turbo/Uncompressed mode on iOS.			//GEN
        if (name == 'Opera Mini' && /\bOPiOS\b/.test(ua)) {			//GEN
            description.push('running in Turbo/Uncompressed mode');			//GEN
        }			//GEN
        // Detect IE Mobile 11.			//GEN
        if (name == 'IE' && /\blike iPhone OS\b/.test(ua)) {			//GEN
            data = parse(ua.replace(/like iPhone OS/, ''));			//GEN
            manufacturer = data.manufacturer;			//GEN
            product = data.product;			//GEN
        }			//GEN
        // Detect iOS.			//GEN
        else if (/^iP/.test(product)) {			//GEN
            name || (name = 'Safari');			//GEN
            os = 'iOS' + ((data = / OS ([\d_]+)/i.exec(ua))			//GEN
                ? ' ' + data[1].replace(/_/g, '.')			//GEN
                : '');			//GEN
        }			//GEN
        // Detect Kubuntu.			//GEN
        else if (name == 'Konqueror' && /^Linux\b/i.test(os)) {			//GEN
            os = 'Kubuntu';			//GEN
        }			//GEN
        // Detect Android browsers.			//GEN
        else if ((manufacturer && manufacturer != 'Google' &&			//GEN
            ((/Chrome/.test(name) && !/\bMobile Safari\b/i.test(ua)) || /\bVita\b/.test(product))) ||			//GEN
            (/\bAndroid\b/.test(os) && /^Chrome/.test(name) && /\bVersion\//i.test(ua))) {			//GEN
            name = 'Android Browser';			//GEN
            os = /\bAndroid\b/.test(os) ? os : 'Android';			//GEN
        }			//GEN
        // Detect Silk desktop/accelerated modes.			//GEN
        else if (name == 'Silk') {			//GEN
            if (!/\bMobi/i.test(ua)) {			//GEN
                os = 'Android';			//GEN
                description.unshift('desktop mode');			//GEN
            }			//GEN
            if (/Accelerated *= *true/i.test(ua)) {			//GEN
                description.unshift('accelerated');			//GEN
            }			//GEN
        }			//GEN
        // Detect UC Browser speed mode.			//GEN
        else if (name == 'UC Browser' && /\bUCWEB\b/.test(ua)) {			//GEN
            description.push('speed mode');			//GEN
        }			//GEN
        // Detect PaleMoon identifying as Firefox.			//GEN
        else if (name == 'PaleMoon' && (data = /\bFirefox\/([\d.]+)\b/.exec(ua))) {			//GEN
            description.push('identifying as Firefox ' + data[1]);			//GEN
        }			//GEN
        // Detect Firefox OS and products running Firefox.			//GEN
        else if (name == 'Firefox' && (data = /\b(Mobile|Tablet|TV)\b/i.exec(ua))) {			//GEN
            os || (os = 'Firefox OS');			//GEN
            product || (product = data[1]);			//GEN
        }			//GEN
        // Detect false positives for Firefox/Safari.			//GEN
        else if (!name || (data = !/\bMinefield\b/i.test(ua) && /\b(?:Firefox|Safari)\b/.exec(name))) {			//GEN
            // Escape the `/` for Firefox 1.			//GEN
            if (name && !product && /[\/,]|^[^(]+?\)/.test(ua.slice(ua.indexOf(data + '/') + 8))) {			//GEN
                // Clear name of false positives.			//GEN
                name = null;			//GEN
            }			//GEN
            // Reassign a generic name.			//GEN
            if ((data = product || manufacturer || os) &&			//GEN
                (product || manufacturer || /\b(?:Android|Symbian OS|Tablet OS|webOS)\b/.test(os))) {			//GEN
                name = /[a-z]+(?: Hat)?/i.exec(/\bAndroid\b/.test(os) ? os : data) + ' Browser';			//GEN
            }			//GEN
        }			//GEN
        // Add Chrome version to description for Electron.			//GEN
        else if (name == 'Electron' && (data = (/\bChrome\/([\d.]+)\b/.exec(ua) || 0)[1])) {			//GEN
            description.push('Chromium ' + data);			//GEN
        }			//GEN
        // Detect non-Opera (Presto-based) versions (order is important).			//GEN
        if (!version) {			//GEN
            version = getVersion([			//GEN
                '(?:Cloud9|CriOS|CrMo|Edge|Edg|EdgA|EdgiOS|FxiOS|HeadlessChrome|IEMobile|Iron|Opera ?Mini|OPiOS|OPR|Raven|SamsungBrowser|Silk(?!/[\\d.]+$)|UCBrowser|YaBrowser)',			//GEN
                'Version',			//GEN
                qualify(name),			//GEN
                '(?:Firefox|Minefield|NetFront)'			//GEN
            ]);			//GEN
        }			//GEN
        // Detect stubborn layout engines.			//GEN
        if ((data =			//GEN
                layout == 'iCab' && parseFloat(version) > 3 && 'WebKit' ||			//GEN
                /\bOpera\b/.test(name) && (/\bOPR\b/.test(ua) ? 'Blink' : 'Presto') ||			//GEN
                /\b(?:Midori|Nook|Safari)\b/i.test(ua) && !/^(?:Trident|EdgeHTML)$/.test(layout) && 'WebKit' ||			//GEN
                !layout && /\bMSIE\b/i.test(ua) && (os == 'Mac OS' ? 'Tasman' : 'Trident') ||			//GEN
                layout == 'WebKit' && /\bPlayStation\b(?! Vita\b)/i.test(name) && 'NetFront'			//GEN
        )) {			//GEN
            layout = [data];			//GEN
        }			//GEN
        // Detect Windows Phone 7 desktop mode.			//GEN
        if (name == 'IE' && (data = (/; *(?:XBLWP|ZuneWP)(\d+)/i.exec(ua) || 0)[1])) {			//GEN
            name += ' Mobile';			//GEN
            os = 'Windows Phone ' + (/\+$/.test(data) ? data : data + '.x');			//GEN
            description.unshift('desktop mode');			//GEN
        }			//GEN
        // Detect Windows Phone 8.x desktop mode.			//GEN
        else if (/\bWPDesktop\b/i.test(ua)) {			//GEN
            name = 'IE Mobile';			//GEN
            os = 'Windows Phone 8.x';			//GEN
            description.unshift('desktop mode');			//GEN
            version || (version = (/\brv:([\d.]+)/.exec(ua) || 0)[1]);			//GEN
        }			//GEN
        // Detect IE 11 identifying as other browsers.			//GEN
        else if (name != 'IE' && layout == 'Trident' && (data = /\brv:([\d.]+)/.exec(ua))) {			//GEN
            if (name) {			//GEN
                description.push('identifying as ' + name + (version ? ' ' + version : ''));			//GEN
            }			//GEN
            name = 'IE';			//GEN
            version = data[1];			//GEN
        }			//GEN
        // Leverage environment features.			//GEN
        if (useFeatures) {			//GEN
            // Detect server-side environments.			//GEN
            // Rhino has a global function while others have a global object.			//GEN
            if (isHostType(context, 'global')) {			//GEN
                if (java) {			//GEN
                    data = java.lang.System;			//GEN
                    arch = data.getProperty('os.arch');			//GEN
                    os = os || data.getProperty('os.name') + ' ' + data.getProperty('os.version');			//GEN
                }			//GEN
                if (rhino) {			//GEN
                    try {			//GEN
                        version = context.require('ringo/engine').version.join('.');			//GEN
                        name = 'RingoJS';			//GEN
                    } catch(e) {			//GEN
                        if ((data = context.system) && data.global.system == context.system) {			//GEN
                            name = 'Narwhal';			//GEN
                            os || (os = data[0].os || null);			//GEN
                        }			//GEN
                    }			//GEN
                    if (!name) {			//GEN
                        name = 'Rhino';			//GEN
                    }			//GEN
                }			//GEN
                else if (			//GEN
                    typeof context.process == 'object' && !context.process.browser &&			//GEN
                    (data = context.process)			//GEN
                ) {			//GEN
                    if (typeof data.versions == 'object') {			//GEN
                        if (typeof data.versions.electron == 'string') {			//GEN
                            description.push('Node ' + data.versions.node);			//GEN
                            name = 'Electron';			//GEN
                            version = data.versions.electron;			//GEN
                        } else if (typeof data.versions.nw == 'string') {			//GEN
                            description.push('Chromium ' + version, 'Node ' + data.versions.node);			//GEN
                            name = 'NW.js';			//GEN
                            version = data.versions.nw;			//GEN
                        }			//GEN
                    }			//GEN
                    if (!name) {			//GEN
                        name = 'Node.js';			//GEN
                        arch = data.arch;			//GEN
                        os = data.platform;			//GEN
                        version = /[\d.]+/.exec(data.version);			//GEN
                        version = version ? version[0] : null;			//GEN
                    }			//GEN
                }			//GEN
            }			//GEN
            // Detect Adobe AIR.			//GEN
            else if (getClassOf((data = context.runtime)) == airRuntimeClass) {			//GEN
                name = 'Adobe AIR';			//GEN
                os = data.flash.system.Capabilities.os;			//GEN
            }			//GEN
            // Detect PhantomJS.			//GEN
            else if (getClassOf((data = context.phantom)) == phantomClass) {			//GEN
                name = 'PhantomJS';			//GEN
                version = (data = data.version || null) && (data.major + '.' + data.minor + '.' + data.patch);			//GEN
            }			//GEN
            // Detect IE compatibility modes.			//GEN
            else if (typeof doc.documentMode == 'number' && (data = /\bTrident\/(\d+)/i.exec(ua))) {			//GEN
                // We're in compatibility mode when the Trident version + 4 doesn't			//GEN
                // equal the document mode.			//GEN
                version = [version, doc.documentMode];			//GEN
                if ((data = +data[1] + 4) != version[1]) {			//GEN
                    description.push('IE ' + version[1] + ' mode');			//GEN
                    layout && (layout[1] = '');			//GEN
                    version[1] = data;			//GEN
                }			//GEN
                version = name == 'IE' ? String(version[1].toFixed(1)) : version[0];			//GEN
            }			//GEN
            // Detect IE 11 masking as other browsers.			//GEN
            else if (typeof doc.documentMode == 'number' && /^(?:Chrome|Firefox)\b/.test(name)) {			//GEN
                description.push('masking as ' + name + ' ' + version);			//GEN
                name = 'IE';			//GEN
                version = '11.0';			//GEN
                layout = ['Trident'];			//GEN
                os = 'Windows';			//GEN
            }			//GEN
            os = os && format(os);			//GEN
        }			//GEN
        // Detect prerelease phases.			//GEN
        if (version && (data =			//GEN
                /(?:[ab]|dp|pre|[ab]\d+pre)(?:\d+\+?)?$/i.exec(version) ||			//GEN
                /(?:alpha|beta)(?: ?\d)?/i.exec(ua + ';' + (useFeatures && nav.appMinorVersion)) ||			//GEN
                /\bMinefield\b/i.test(ua) && 'a'			//GEN
        )) {			//GEN
            prerelease = /b/i.test(data) ? 'beta' : 'alpha';			//GEN
            version = version.replace(RegExp(data + '\\+?$'), '') +			//GEN
                (prerelease == 'beta' ? beta : alpha) + (/\d+\+?/.exec(data) || '');			//GEN
        }			//GEN
        // Detect Firefox Mobile.			//GEN
        if (name == 'Fennec' || name == 'Firefox' && /\b(?:Android|Firefox OS|KaiOS)\b/.test(os)) {			//GEN
            name = 'Firefox Mobile';			//GEN
        }			//GEN
        // Obscure Maxthon's unreliable version.			//GEN
        else if (name == 'Maxthon' && version) {			//GEN
            version = version.replace(/\.[\d.]+/, '.x');			//GEN
        }			//GEN
        // Detect Xbox 360 and Xbox One.			//GEN
        else if (/\bXbox\b/i.test(product)) {			//GEN
            if (product == 'Xbox 360') {			//GEN
                os = null;			//GEN
            }			//GEN
            if (product == 'Xbox 360' && /\bIEMobile\b/.test(ua)) {			//GEN
                description.unshift('mobile mode');			//GEN
            }			//GEN
        }			//GEN
        // Add mobile postfix.			//GEN
        else if ((/^(?:Chrome|IE|Opera)$/.test(name) || name && !product && !/Browser|Mobi/.test(name)) &&			//GEN
            (os == 'Windows CE' || /Mobi/i.test(ua))) {			//GEN
            name += ' Mobile';			//GEN
        }			//GEN
        // Detect IE platform preview.			//GEN
        else if (name == 'IE' && useFeatures) {			//GEN
            try {			//GEN
                if (context.external === null) {			//GEN
                    description.unshift('platform preview');			//GEN
                }			//GEN
            } catch(e) {			//GEN
                description.unshift('embedded');			//GEN
            }			//GEN
        }			//GEN
            // Detect BlackBerry OS version.			//GEN
        // http://docs.blackberry.com/en/developers/deliverables/18169/HTTP_headers_sent_by_BB_Browser_1234911_11.jsp			//GEN
        else if ((/\bBlackBerry\b/.test(product) || /\bBB10\b/.test(ua)) && (data =			//GEN
                (RegExp(product.replace(/ +/g, ' *') + '/([.\\d]+)', 'i').exec(ua) || 0)[1] ||			//GEN
                version			//GEN
        )) {			//GEN
            data = [data, /BB10/.test(ua)];			//GEN
            os = (data[1] ? (product = null, manufacturer = 'BlackBerry') : 'Device Software') + ' ' + data[0];			//GEN
            version = null;			//GEN
        }			//GEN
            // Detect Opera identifying/masking itself as another browser.			//GEN
        // http://www.opera.com/support/kb/view/843/			//GEN
        else if (this != forOwn && product != 'Wii' && (			//GEN
            (useFeatures && opera) ||			//GEN
            (/Opera/.test(name) && /\b(?:MSIE|Firefox)\b/i.test(ua)) ||			//GEN
            (name == 'Firefox' && /\bOS X (?:\d+\.){2,}/.test(os)) ||			//GEN
            (name == 'IE' && (			//GEN
                (os && !/^Win/.test(os) && version > 5.5) ||			//GEN
                /\bWindows XP\b/.test(os) && version > 8 ||			//GEN
                version == 8 && !/\bTrident\b/.test(ua)			//GEN
            ))			//GEN
        ) && !reOpera.test((data = parse.call(forOwn, ua.replace(reOpera, '') + ';'))) && data.name) {			//GEN
            // When "identifying", the UA contains both Opera and the other browser's name.			//GEN
            data = 'ing as ' + data.name + ((data = data.version) ? ' ' + data : '');			//GEN
            if (reOpera.test(name)) {			//GEN
                if (/\bIE\b/.test(data) && os == 'Mac OS') {			//GEN
                    os = null;			//GEN
                }			//GEN
                data = 'identify' + data;			//GEN
            }			//GEN
            // When "masking", the UA contains only the other browser's name.			//GEN
            else {			//GEN
                data = 'mask' + data;			//GEN
                if (operaClass) {			//GEN
                    name = format(operaClass.replace(/([a-z])([A-Z])/g, '$1 $2'));			//GEN
                } else {			//GEN
                    name = 'Opera';			//GEN
                }			//GEN
                if (/\bIE\b/.test(data)) {			//GEN
                    os = null;			//GEN
                }			//GEN
                if (!useFeatures) {			//GEN
                    version = null;			//GEN
                }			//GEN
            }			//GEN
            layout = ['Presto'];			//GEN
            description.push(data);			//GEN
        }			//GEN
        // Detect WebKit Nightly and approximate Chrome/Safari versions.			//GEN
        if ((data = (/\bAppleWebKit\/([\d.]+\+?)/i.exec(ua) || 0)[1])) {			//GEN
            // Correct build number for numeric comparison.			//GEN
            // (e.g. "532.5" becomes "532.05")			//GEN
            data = [parseFloat(data.replace(/\.(\d)$/, '.0$1')), data];			//GEN
            // Nightly builds are postfixed with a "+".			//GEN
            if (name == 'Safari' && data[1].slice(-1) == '+') {			//GEN
                name = 'WebKit Nightly';			//GEN
                prerelease = 'alpha';			//GEN
                version = data[1].slice(0, -1);			//GEN
            }			//GEN
            // Clear incorrect browser versions.			//GEN
            else if (version == data[1] ||			//GEN
                version == (data[2] = (/\bSafari\/([\d.]+\+?)/i.exec(ua) || 0)[1])) {			//GEN
                version = null;			//GEN
            }			//GEN
            // Use the full Chrome version when available.			//GEN
            data[1] = (/\b(?:Headless)?Chrome\/([\d.]+)/i.exec(ua) || 0)[1];			//GEN
            // Detect Blink layout engine.			//GEN
            if (data[0] == 537.36 && data[2] == 537.36 && parseFloat(data[1]) >= 28 && layout == 'WebKit') {			//GEN
                layout = ['Blink'];			//GEN
            }			//GEN
            // Detect JavaScriptCore.			//GEN
            // http://stackoverflow.com/questions/6768474/how-can-i-detect-which-javascript-engine-v8-or-jsc-is-used-at-runtime-in-androi			//GEN
            if (!useFeatures || (!likeChrome && !data[1])) {			//GEN
                layout && (layout[1] = 'like Safari');			//GEN
                data = (data = data[0], data < 400 ? 1 : data < 500 ? 2 : data < 526 ? 3 : data < 533 ? 4 : data < 534 ? '4+' : data < 535 ? 5 : data < 537 ? 6 : data < 538 ? 7 : data < 601 ? 8 : '8');			//GEN
            } else {			//GEN
                layout && (layout[1] = 'like Chrome');			//GEN
                data = data[1] || (data = data[0], data < 530 ? 1 : data < 532 ? 2 : data < 532.05 ? 3 : data < 533 ? 4 : data < 534.03 ? 5 : data < 534.07 ? 6 : data < 534.10 ? 7 : data < 534.13 ? 8 : data < 534.16 ? 9 : data < 534.24 ? 10 : data < 534.30 ? 11 : data < 535.01 ? 12 : data < 535.02 ? '13+' : data < 535.07 ? 15 : data < 535.11 ? 16 : data < 535.19 ? 17 : data < 536.05 ? 18 : data < 536.10 ? 19 : data < 537.01 ? 20 : data < 537.11 ? '21+' : data < 537.13 ? 23 : data < 537.18 ? 24 : data < 537.24 ? 25 : data < 537.36 ? 26 : layout != 'Blink' ? '27' : '28');			//GEN
            }			//GEN
            // Add the postfix of ".x" or "+" for approximate versions.			//GEN
            layout && (layout[1] += ' ' + (data += typeof data == 'number' ? '.x' : /[.+]/.test(data) ? '' : '+'));			//GEN
            // Obscure version for some Safari 1-2 releases.			//GEN
            if (name == 'Safari' && (!version || parseInt(version) > 45)) {			//GEN
                version = data;			//GEN
            } else if (name == 'Chrome' && /\bHeadlessChrome/i.test(ua)) {			//GEN
                description.unshift('headless');			//GEN
            }			//GEN
        }			//GEN
        // Detect Opera desktop modes.			//GEN
        if (name == 'Opera' &&  (data = /\bzbov|zvav$/.exec(os))) {			//GEN
            name += ' ';			//GEN
            description.unshift('desktop mode');			//GEN
            if (data == 'zvav') {			//GEN
                name += 'Mini';			//GEN
                version = null;			//GEN
            } else {			//GEN
                name += 'Mobile';			//GEN
            }			//GEN
            os = os.replace(RegExp(' *' + data + '$'), '');			//GEN
        }			//GEN
        // Detect Chrome desktop mode.			//GEN
        else if (name == 'Safari' && /\bChrome\b/.exec(layout && layout[1])) {			//GEN
            description.unshift('desktop mode');			//GEN
            name = 'Chrome Mobile';			//GEN
            version = null;			//GEN
			//GEN
            if (/\bOS X\b/.test(os)) {			//GEN
                manufacturer = 'Apple';			//GEN
                os = 'iOS 4.3+';			//GEN
            } else {			//GEN
                os = null;			//GEN
            }			//GEN
        }			//GEN
        // Newer versions of SRWare Iron uses the Chrome tag to indicate its version number.			//GEN
        else if (/\bSRWare Iron\b/.test(name) && !version) {			//GEN
            version = getVersion('Chrome');			//GEN
        }			//GEN
        // Strip incorrect OS versions.			//GEN
        if (version && version.indexOf((data = /[\d.]+$/.exec(os))) == 0 &&			//GEN
            ua.indexOf('/' + data + '-') > -1) {			//GEN
            os = trim(os.replace(data, ''));			//GEN
        }			//GEN
        // Ensure OS does not include the browser name.			//GEN
        if (os && os.indexOf(name) != -1 && !RegExp(name + ' OS').test(os)) {			//GEN
            os = os.replace(RegExp(' *' + qualify(name) + ' *'), '');			//GEN
        }			//GEN
        // Add layout engine.			//GEN
        if (layout && !/\b(?:Avant|Nook)\b/.test(name) && (			//GEN
            /Browser|Lunascape|Maxthon/.test(name) ||			//GEN
            name != 'Safari' && /^iOS/.test(os) && /\bSafari\b/.test(layout[1]) ||			//GEN
            /^(?:Adobe|Arora|Breach|Midori|Opera|Phantom|Rekonq|Rock|Samsung Internet|Sleipnir|SRWare Iron|Vivaldi|Web)/.test(name) && layout[1])) {			//GEN
            // Don't add layout details to description if they are falsey.			//GEN
            (data = layout[layout.length - 1]) && description.push(data);			//GEN
        }			//GEN
        // Combine contextual information.			//GEN
        if (description.length) {			//GEN
            description = ['(' + description.join('; ') + ')'];			//GEN
        }			//GEN
        // Append manufacturer to description.			//GEN
        if (manufacturer && product && product.indexOf(manufacturer) < 0) {			//GEN
            description.push('on ' + manufacturer);			//GEN
        }			//GEN
        // Append product to description.			//GEN
        if (product) {			//GEN
            description.push((/^on /.test(description[description.length - 1]) ? '' : 'on ') + product);			//GEN
        }			//GEN
        // Parse the OS into an object.			//GEN
        if (os) {			//GEN
            data = / ([\d.+]+)$/.exec(os);			//GEN
            isSpecialCasedOS = data && os.charAt(os.length - data[0].length - 1) == '/';			//GEN
            os = {			//GEN
                'architecture': 32,			//GEN
                'family': (data && !isSpecialCasedOS) ? os.replace(data[0], '') : os,			//GEN
                'version': data ? data[1] : null,			//GEN
                'toString': function() {			//GEN
                    var version = this.version;			//GEN
                    return this.family + ((version && !isSpecialCasedOS) ? ' ' + version : '') + (this.architecture == 64 ? ' 64-bit' : '');			//GEN
                }			//GEN
            };			//GEN
        }			//GEN
        // Add browser/OS architecture.			//GEN
        if ((data = /\b(?:AMD|IA|Win|WOW|x86_|x)64\b/i.exec(arch)) && !/\bi686\b/i.test(arch)) {			//GEN
            if (os) {			//GEN
                os.architecture = 64;			//GEN
                os.family = os.family.replace(RegExp(' *' + data), '');			//GEN
            }			//GEN
            if (			//GEN
                name && (/\bWOW64\b/i.test(ua) ||			//GEN
                (useFeatures && /\w(?:86|32)$/.test(nav.cpuClass || nav.platform) && !/\bWin64; x64\b/i.test(ua)))			//GEN
            ) {			//GEN
                description.unshift('32-bit');			//GEN
            }			//GEN
        }			//GEN
        // Chrome 39 and above on OS X is always 64-bit.			//GEN
        else if (			//GEN
            os && /^OS X/.test(os.family) &&			//GEN
            name == 'Chrome' && parseFloat(version) >= 39			//GEN
        ) {			//GEN
            os.architecture = 64;			//GEN
        }			//GEN
			//GEN
        ua || (ua = null);			//GEN
			//GEN
        /*------------------------------------------------------------------------*/			//GEN
			//GEN
        /**			//GEN
         * The platform object.			//GEN
         *			//GEN
         * @name platform			//GEN
         * @type Object			//GEN
         */			//GEN
        var platform = {};			//GEN
			//GEN
        /**			//GEN
         * The platform description.			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.description = ua;			//GEN
			//GEN
        /**			//GEN
         * The name of the browser's layout engine.			//GEN
         *			//GEN
         * The list of common layout engines include:			//GEN
         * "Blink", "EdgeHTML", "Gecko", "Trident" and "WebKit"			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.layout = layout && layout[0];			//GEN
			//GEN
        /**			//GEN
         * The name of the product's manufacturer.			//GEN
         *			//GEN
         * The list of manufacturers include:			//GEN
         * "Apple", "Archos", "Amazon", "Asus", "Barnes & Noble", "BlackBerry",			//GEN
         * "Google", "HP", "HTC", "LG", "Microsoft", "Motorola", "Nintendo",			//GEN
         * "Nokia", "Samsung" and "Sony"			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.manufacturer = manufacturer;			//GEN
			//GEN
        /**			//GEN
         * The name of the browser/environment.			//GEN
         *			//GEN
         * The list of common browser names include:			//GEN
         * "Chrome", "Electron", "Firefox", "Firefox for iOS", "IE",			//GEN
         * "Microsoft Edge", "PhantomJS", "Safari", "SeaMonkey", "Silk",			//GEN
         * "Opera Mini" and "Opera"			//GEN
         *			//GEN
         * Mobile versions of some browsers have "Mobile" appended to their name:			//GEN
         * eg. "Chrome Mobile", "Firefox Mobile", "IE Mobile" and "Opera Mobile"			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.name = name;			//GEN
			//GEN
        /**			//GEN
         * The alpha/beta release indicator.			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.prerelease = prerelease;			//GEN
			//GEN
        /**			//GEN
         * The name of the product hosting the browser.			//GEN
         *			//GEN
         * The list of common products include:			//GEN
         *			//GEN
         * "BlackBerry", "Galaxy S4", "Lumia", "iPad", "iPod", "iPhone", "Kindle",			//GEN
         * "Kindle Fire", "Nexus", "Nook", "PlayBook", "TouchPad" and "Transformer"			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.product = product;			//GEN
			//GEN
        /**			//GEN
         * The browser's user agent string.			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.ua = ua;			//GEN
			//GEN
        /**			//GEN
         * The browser/environment version.			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type string|null			//GEN
         */			//GEN
        platform.version = name && version;			//GEN
			//GEN
        /**			//GEN
         * The name of the operating system.			//GEN
         *			//GEN
         * @memberOf platform			//GEN
         * @type Object			//GEN
         */			//GEN
        platform.os = os || {			//GEN
			//GEN
            /**			//GEN
             * The CPU architecture the OS is built for.			//GEN
             *			//GEN
             * @memberOf platform.os			//GEN
             * @type number|null			//GEN
             */			//GEN
            'architecture': null,			//GEN
			//GEN
            /**			//GEN
             * The family of the OS.			//GEN
             *			//GEN
             * Common values include:			//GEN
             * "Windows", "Windows Server 2008 R2 / 7", "Windows Server 2008 / Vista",			//GEN
             * "Windows XP", "OS X", "Linux", "Ubuntu", "Debian", "Fedora", "Red Hat",			//GEN
             * "SuSE", "Android", "iOS" and "Windows Phone"			//GEN
             *			//GEN
             * @memberOf platform.os			//GEN
             * @type string|null			//GEN
             */			//GEN
            'family': null,			//GEN
			//GEN
            /**			//GEN
             * The version of the OS.			//GEN
             *			//GEN
             * @memberOf platform.os			//GEN
             * @type string|null			//GEN
             */			//GEN
            'version': null,			//GEN
			//GEN
            /**			//GEN
             * Returns the OS string.			//GEN
             *			//GEN
             * @memberOf platform.os			//GEN
             * @returns {string} The OS string.			//GEN
             */			//GEN
            'toString': function() { return 'null'; }			//GEN
        };			//GEN
			//GEN
        platform.parse = parse;			//GEN
        platform.toString = toStringPlatform;			//GEN
			//GEN
        if (platform.version) {			//GEN
            description.unshift(version);			//GEN
        }			//GEN
        if (platform.name) {			//GEN
            description.unshift(name);			//GEN
        }			//GEN
        if (os && name && !(os == String(os).split(' ')[0] && (os == name.split(' ')[0] || product))) {			//GEN
            description.push(product ? '(' + os + ')' : 'on ' + os);			//GEN
        }			//GEN
        if (description.length) {			//GEN
            platform.description = description.join(' ');			//GEN
        }			//GEN
        return platform;			//GEN
    }			//GEN
			//GEN
    /*--------------------------------------------------------------------------*/			//GEN
			//GEN
    // Export platform.			//GEN
    var platform = parse();			//GEN
			//GEN
    // Some AMD build optimizers, like r.js, check for condition patterns like the following:			//GEN
    if (typeof define == 'function' && typeof define.amd == 'object' && define.amd) {			//GEN
        // Expose platform on the global object to prevent errors when platform is			//GEN
        // loaded by a script tag in the presence of an AMD loader.			//GEN
        // See http://requirejs.org/docs/errors.html#mismatch for more details.			//GEN
        root.platform = platform;			//GEN
			//GEN
        // Define as an anonymous module so platform can be aliased through path mapping.			//GEN
        define(function() {			//GEN
            return platform;			//GEN
        });			//GEN
    }			//GEN
    // Check for `exports` after `define` in case a build optimizer adds an `exports` object.			//GEN
    else if (freeExports && freeModule) {			//GEN
        // Export for CommonJS support.			//GEN
        forOwn(platform, function(value, key) {			//GEN
            freeExports[key] = value;			//GEN
        });			//GEN
    }			//GEN
    else {			//GEN
        // Export to the global object.			//GEN
        root.platform = platform;			//GEN
    }			//GEN
}.call(this));			//GEN
