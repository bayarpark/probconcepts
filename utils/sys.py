from os import mkdir
from datetime import datetime


def makedir(path: str) -> None:
    if not path.endswith('/') or not path.endswith('\\'):
        path = path + '/'

    if path.endswith('pcr/'):
        mkdir(path=f'{path[:1]} {datetime.now().strftime("%Y-%m-%d T %H h")}/')
    else:
        try:
            mkdir(path)
        except FileExistsError:
            pass
