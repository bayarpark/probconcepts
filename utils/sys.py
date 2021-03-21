from os import mkdir
from datetime import datetime


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
