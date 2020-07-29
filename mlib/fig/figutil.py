import numpy as np

from mlib.boot.stream import make2d, arr, sort_human

def add_headers_to_mat(ar2d, row_headers, col_headers, alphabetize=False):
    ar2d = np.concatenate((make2d(col_headers), arr(ar2d)), axis=0)
    row_headers = make2d(np.insert(row_headers, 0, None)).T
    cmat = np.concatenate((row_headers, ar2d), axis=1)
    if alphabetize:
        cmat[1:] = sort_human(cmat[1:])
        temp = np.transpose(arr(cmat))
        temp[1:] = sort_human(temp[1:])
        cmat = np.transpose(arr(temp))
    return cmat


