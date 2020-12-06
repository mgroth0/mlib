from numpy import count_nonzero

from mlib.boot.mlog import err
from mlib.boot.stream import arr, bitwise_and
from mlib.math import sqrt
def binary_results(y_true, y_pred):
    y_true = arr(y_true)
    y_pred = arr(y_pred)
    if any(arr(y_true) > 1) or any(arr(y_pred) > 1):
        err('binary results cannot be done when there are more than two classes')
    neg = 0
    pos = 1
    P = count_nonzero(y_true == pos)
    N = count_nonzero(y_true == neg)
    TP = count_nonzero(bitwise_and(y_pred == pos, y_true == pos))
    FP = count_nonzero(bitwise_and(y_pred == pos, y_true == neg))
    TN = count_nonzero(bitwise_and(y_pred == neg, y_true == neg))
    FN = count_nonzero(bitwise_and(y_pred == neg, y_true == pos))
    return TP, FP, TN, FN, P, N

def multi_results(y_true, y_pred):
    y_true = arr(y_true)
    y_pred = arr(y_pred)
    C = 0
    I = 0
    for i in range(len(y_true)):
        if y_true[i] == y_pred[i]:
            C += 1
        else:
            I += 1
    return C, I

def mcc_basic(TP, FP, TN, FN):
    denom = sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
    if denom == 0: denom = 1
    rrr = (TP * TN - FP * FN) / denom
    return rrr
def error_rate_basic(FP, FN, P, N):
    return (FP + FN) / (P + N)
