from datetime import datetime
from os import mkdir
from typing import Any

from numpy import nan
from pandas import NA


def makedir(path: str) -> str:
    if not path.endswith('/') or not path.endswith('\\'):
        path = path + '/'

    if path.endswith('pcr/'):  ## SOME BUGS TODO
        path = f'{path[:1]} {datetime.now().strftime("%Y-%m-%d T %H h")}/'
        mkdir(path=path)
    else:
        try:
            mkdir(path)
        except FileExistsError:
            pass
    return path


def is_none(x: Any) -> bool:
    if x is None or x is nan or x is NA:
        return True
    else:
        return False


def split(arr, buckets):
    # buckets - num of arrays to split

    split_size = len(arr) // buckets

    n = len(arr) - buckets * split_size  # num of arrays to keep split_size+1 elems

    split_arrs = []

    j = 0  #
    k = 0  #

    # filling arrays with split_size elems
    for i in range(buckets - n):
        s_arr = []
        for t in range(split_size):
            s_arr.append(arr[k])
            k += 1
        split_arrs.append(s_arr)

    # filling arrays with split_size+1 elems
    for i in range(n):
        s_arr = []
        for t in range(split_size):
            s_arr.append(arr[k])
            k += 1
        s_arr.append(arr[k])
        k += 1
        split_arrs.append(s_arr)

    return split_arrs
