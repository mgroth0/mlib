from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

from scipy import signal
from scipy.signal import lfilter
import scipy.signal
import numpy as np

from mlib.boot import log
from mlib.boot.lang import isstr
from mlib.boot.mlog import err
from mlib.boot.stream import listfilt, arr, ndims, isnan, append, arrayfun, invert, bitwise_and, itr


def safestd(v):
    if len(v) > 0:
        return np.std(arr(np.vectorize(float)(v)))
    else:
        return None

def xcorr(x, y, Fs, lagSecs=30):
    log('in xcorr')

    maxlags = np.floor(Fs * lagSecs)

    x = x - np.mean(x)
    y = y - np.mean(y)

    x = x.flatten()
    y = y.flatten()

    Nx = len(x)
    if Nx != len(y):
        raise ValueError('x and y must be equal length')

    ccc = np.correlate(x, y, mode='full')

    if maxlags is None:
        maxlags = Nx - 1

    if maxlags >= Nx or maxlags < 1:
        raise ValueError('maxlags must be None or strictly positive < %d' % Nx)

    # zero_lag_idx = int((len(ccc) - 1) / 2)
    ccc = ccc[int(Nx - 1 - maxlags):int(Nx + maxlags)]

    # denom = sqrt((x[zero_lag_idx]**2) * y[zero_lag_idx]**2)
    denom = sqrt(np.correlate(x, x, mode='full')[len(x) - 1] * np.correlate(y, y, mode='full')[len(y) - 1])

    if denom == 0:
        return None, None, None, None, None
    for idx, cc in enumerate(ccc):
        ccc[idx] = cc * 1 / denom

    mx = max(ccc)
    mn = min(ccc)
    mx_latency = ccc.tolist().index(mx)
    mn_latency = ccc.tolist().index(mn)

    # [max_mi,i] = max(abs(xc));
    mx_latency_secs = (mx_latency - (maxlags + 1)) / Fs
    mn_latency_secs = (mn_latency - (maxlags + 1)) / Fs

    return ccc, mx, mn, mx_latency_secs, mn_latency_secs




def sigfig(number, ndigits):
    testnumber = abs(number)
    if testnumber == 0:
        return 0
    ref = 1
    roundn = ndigits
    while testnumber >= ref:
        roundn -= 1
        ref = ref * 10
    ref = 0.1
    while testnumber <= ref:
        roundn += 1
        ref = ref / 10
    return round(number, roundn)



# numpy thinks infinity is real, i dont think so
def isreal(n):
    if n is None or abs(n) == np.inf:
        return False
    return np.isreal(n)

def minreal(*nums):
    nums = listfilt(lambda x: isreal(x), nums)
    if len(nums) > 0:
        return min(nums)
def maxreal(*nums):
    nums = listfilt(lambda x: isreal(x), nums)
    if len(nums) > 0:
        return max(nums)


def nanmean(lll):
    if ndims(lll) > 2:
        err('no ready')
    elif ndims(lll) == 2:
        rrr = arr()
        for i in range(0, lll.shape[1]):
            colu = list(filter(lambda x: not isnan(x), lll[:, i]))
            rrr += safemean(colu)
    else:  # 1-d
        lll = list(filter(lambda x: not isnan(x), lll))
        rrr = safemean(lll)
    # noinspection PyUnboundLocalVariable
    return rrr


def sqrt(ar):
    return np.sqrt(ar)



def nanstd(lll):
    # l = list(filter(lambda x: not isnan(x),l))
    lll = arr(lll)
    lll = lll[np.invert(isnan(lll))]
    if len(lll) > 0:
        # tolist needed because dtype is obj sometimes for some reason ????
        lll = lll[np.invert(isinf(lll.tolist()))]
    rr = safestd(lll)
    return rr

def safeStandardErr(lll):
    return safestd(lll) / sqrt(len(lll))




# just prevents stupid warning when taking mean of empty list
def safemean(v):
    import statistics
    if isinstance(v, (int, float)):
        return v
    if len(v) > 0:
        if isinstance(v, np.ndarray):
            v = v.flatten()
        v = list(filter(lambda x: x != 'Excluded', v))
        if isinstance(v[0], str):
            v = list(map(float, v))
        return statistics.mean(map(float, v))
    else:
        return None


def isinf(v):
    if v is None:
        return False
    return arr(np.isinf(v))




def simple_downsample(aa, ds):
    bb = arr()
    for i in range(0, len(aa), ds):
        bb = append(bb, aa[i])
    return bb
    # if mod(len(aa),ds) == 0:
    #     a = np.array([1.,2,6,2,1,7])
    #     return a.reshape(-1, ds).mean(axis=1)
    # else:
    #     pad_size = math.ceil(float(len(aa)) / ds) * ds - len(aa)
    #     b_padded = np.append(aa, np.zeros(pad_size) * np.NaN)
    #     return scipy.nanmean(b_padded.reshape(-1,ds), axis=1)

def nandiv(a, v):
    r = arr()
    for i in itr(a):
        if isnan(a[i]):
            r = append(r, None)
        else:
            r = append(r, a[i] / v)
    return r




def iseven(n):
    return n % 2 == 0


def parse_inf(o):
    if not isstr(o):
        return o
    else:
        if o == 'inf':
            return np.inf
        elif o == '-inf':
            return -np.inf




def demean(lll):
    mean = np.mean(lll)
    return lll - mean

def normalized(lll):
    return lll / np.std(lll)

DOC = None
def init_shadow():
    global DOC
    from mlib.web.shadow import Shadow
    DOC = Shadow(
        include_index_link=False,
        bib='hep_bib.yml'
    )
    DOC.h2(
        'Preprocessing 2',
        style={'text-align': 'center'}
    )

# DOC: START
def nopl_high(raw, Fs):
    # this is used later in find_local_maxima()
    sig_nopl_high = bandstop(raw, 59, 61, Fs, 1)  # basic power line removal
    sig_nopl_high = highpass(sig_nopl_high, 1, Fs)
    # DOC:CITE[perakakis2019]DOC:CITE[carvalho2002] (both used 4th order. I used 1st order by mistake but should change it to 4th order in next version.)
    return sig_nopl_high
# DOC: STOP


def highpass(data, Hz, Fs, order=1):
    nyq = 0.5 * Fs
    normal_cutoff = Hz / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    sig = signal.filtfilt(b, a, data)
    return sig

def nopl(data, Fs):
    return bandstop(data, 59, 61, Fs, 1)

def lowpass(data, lowcut, Fs, order=1):
    nyq = 0.5 * Fs
    low = lowcut / nyq
    # noinspection PyTupleAssignmentBalance
    i, u = butter(order, low, btype='lowpass')
    y = lfilter(i, u, data)
    return y


# def notch(data,bad_freq,Fs,order):
#     width =
#     return bandstop(data, lowcut, highcut, fs, order)

def bandstop(data, lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(order, [low, high], btype='bandstop')
    y = lfilter(b, a, data)
    return y

def difffun(lamb, ar):
    newlist = arrayfun(lamb, ar)
    diffs = arr()
    for idx, e in enumerate(newlist):
        if idx == 0:
            last_e = e
            continue
        # noinspection PyUnboundLocalVariable
        diffs += e - last_e
        last_e = e
    return diffs



# noinspection PyUnusedLocal
def slope(m, x, y):
    from scipy.stats import linregress
    # log('slope1')
    # try:
    not_nans = invert(isnan(y))
    # except Exception as e:
    if np.count_nonzero(not_nans) < 2:
        return None
    not_infs = invert(isinf(y))
    x = x[bitwise_and(not_nans, not_infs)]
    y = y[bitwise_and(not_nans, not_infs)]
    # from PyMat import matfun
    # coefs = matfun(m,'polyfit', x, y, 1)
    # coefs = arr(coefs)
    # log('slopeR')
    # return coefs[0,0]
    # noinspection PyUnresolvedReferences
    return linregress(x, y).slope

# prevent ide bug causing need for "noinspection PyTupleAssignmentBalance" everywhere
def butter(N, Wn, btype='low', analog=False, output='ba', fs=None):
    # noinspection PyTupleAssignmentBalance
    b, a = scipy.signal.butter(N, Wn, btype=btype, analog=analog, output=output, fs=fs)

    return b, a


def unitscale_demean_fun(array):
    div = ((max(array) - min(array)) / 2.)
    me = np.mean(array)
    def norm(other_array):
        r = other_array / div
        r = r - me
        return r
    return norm

def unitscale_demean(array):
    fun = unitscale_demean_fun(array)
    return fun(array)

def ntrue(*args):
    return sum(args)

class TimeUnit(Enum):
    MS = auto()
    SEC = auto()
    MIN = auto()
    HOUR = auto()

@dataclass
class TimeSeries:
    y: Union[list, np.ndarray]
    t: Union[list, np.ndarray]
    y_unit: str
    t_unit: TimeUnit

    def __post_init__(self):
        self.est_t_per_sample = (self.t[-1] - self.t[0]) / len(self.t)

    def ds(self, n):
        return TimeSeries(
            y=simple_downsample(self.y, n),
            t=simple_downsample(self.t, n),
            y_unit=self.y_unit,
            t_unit=self.t_unit,
        )

    def __getitem__(self, item):
        return TimeSeries(
            y=self.y[item],
            t=self.t[item],
            y_unit=self.y_unit,
            t_unit=self.t_unit,
        )

    def time_slice(self, start, stop):
        start_i = np.argwhere(self.t >= start)[0][0]
        stop_i = np.argwhere(self.t >= stop)[0][0]
        return self[start_i:stop_i]

    def time_slice_apx(self, start, stop):
        start_i = int(round(start / self.est_t_per_sample))
        stop_i = int(round(stop / self.est_t_per_sample))
        return self[start_i:stop_i]

@dataclass
class TimePoints:
    t: Union[list, np.ndarray]
    t_unit: TimeUnit

def autoYRange(ar):
    mn = min(ar)
    mx = max(ar)
    dif = mx - mn
    ten = dif * 0.1
    mn = mn - ten
    mx = mx + ten
    return mn, mx
