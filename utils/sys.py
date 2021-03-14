from os import mkdir
from datetime import datetime


def makedir(path: str) -> str:
    if not path.endswith('/') or not path.endswith('\\'):
        path = path + '/'

    if path.endswith('pcr/'):
        path = f'{path[:1]} {datetime.now().strftime("%Y-%m-%d T %H h")}/'
        mkdir(path=path)
    else:
        try:
            mkdir(path)
        except FileExistsError:
            pass
    return path
