import copy

import pandas
import scipy

from mlib.boot.mutil import *
class obj(object):

    def toDict(self):
        d = self.__dict__
        for key, value in d.items():
            if isinstance(value, obj):
                d[key] = value.toDict()
            elif isinstsafe(value, JsonSerializable):
                d[key] = json.loads(value.to_json())
            elif is_non_str_itr(value):
                if len(arr(value).shape) == 0:
                    d[key] = []
                elif len(list(value)) > 0 and isinstance(list(value)[0], obj):
                    d[key] = [v.toDict() for v in value]
                elif len(list(value)) > 0 and isinstsafe(list(value)[0], JsonSerializable):
                    d[key] = [json.loads(v.to_json()) for v in value]
        return d

    def __init__(self, d, forceNP=False):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                new = [obj(x, forceNP) if isinstance(x, dict) else x for x in b]
                if forceNP:
                    new = arr(new)
                setattr(self, a, new)
            # isinstance(b, wolframclient.language.expression.WLFunction):
            elif 'WLFunction' in cn(b):
                if 'Rational[' in str(b):
                    b = str(b).split('[')[1]
                    b = str(b).split(']')[0]
                    top = b.split(',')[0].strip()
                    bot = b.split(',')[1].strip()
                    setattr(self, a, float(top) / float(bot))
                else:
                    setattr(self, a, b)

            else:
                setattr(self, a, obj(b, forceNP) if isinstance(b, dict) else b)
    def fixInfs(self):
        for k, v in listitems(self.__dict__):
            if v in ['inf', '-inf']:
                self.__dict__[k] = parse_inf(v)
            elif isinstance(v,obj):
                v.fixInfs()
        return self

def jsonReprCP(o):
    # log('jsonReprCP of a ' + str(type(o)))
    if isinstsafe(o, np.ndarray):
        o = o.tolist()
    if not isitr(o) and isnan(o):
        return None
    if o == np.inf or o == -np.inf:
        return str(o)
    if isinstance(o, str) or isinstance(o, float) or isinstance(o, int) or o is None:
        return o
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, np.float32):
        return float(o)

    if isitr(o) and not isinstance(o, str):
        cp = []
        for vv in o:
            cp.append(jsonReprCP(vv))
        return cp

    cp = copy.deepcopy(o)
    for v in cp.__dict__:
        val = getattr(cp, v)
        if isitr(val) and not isinstance(val, str):
            newval = []
            for vv in val:
                newval.append(jsonReprCP(vv))
            setattr(cp, v, newval)
        if not isitr(val) and (val == np.inf or val == -np.inf):
            setattr(cp, v, str(val))
        if isinstance(val, np.int64):
            setattr(cp, v, int(val))
        if not isitr(val) and pandas.isnull(val):
            setattr(cp, v, None)
        if isinstance(val, JsonSerializable):
            setattr(cp, v, jsonReprCP(val).__dict__)
        if isitr(val) and not isempty(val) and isinstance(val[0], JsonSerializable):
            newval = []
            for i in itr(val):
                newval.append(jsonReprCP(val[i]).__dict__)
            setattr(cp, v, newval)
    return cp

class JsonSerializable:
    def to_json(self):
        cp = jsonReprCP(self)
        return json.dumps(cp, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class FigSet(JsonSerializable):
    def __init__(self, *viss):
        self.viss = list(viss)

    def __setitem__(self, key, value):
        self.viss[key] = value

    def __getitem__(self, item):
        return self.viss[item]

    def statBrackets(self, data, pairs):
        means = []
        import mlib.FigData as FigData
        for d in data:
            means.append(safemean(d))
        lastBracketHeight = 0
        for pair in pairs:
            g1 = pair[0]
            g2 = pair[1]
            bracketStart = means[g1] * 1.2 if means[g1] > means[g2] else means[g2] * 1.2
            bracketHeight = means[g1] * 1.5 if means[g1] > means[g2] else means[g2] * 1.5

            # fix heights (was optional)
            if lastBracketHeight != 0:
                bracketHeight = max([bracketHeight, lastBracketHeight * 1.1])
                lastBracketHeight = bracketHeight

            bracketFig = FigData.FigData()
            bracketFig.item_type = 'line'
            bracketFig.x = [g1, g1, g1 + .5 * (g2 - g1), g2, g2]
            def plus1(x): return x + 1
            bracketFig.x = list(map(plus1, bracketFig.x))
            bracketFig.y = [bracketStart, bracketHeight, bracketHeight, bracketHeight, bracketStart]
            bracketFig.callout_x = (g1 + .5 * (g2 - g1)) + 1

            bracketFig.callout = str(
                scipy.stats.ttest_ind(data[g1], data[g2])[1]
            )
            self.viss.append(bracketFig)
