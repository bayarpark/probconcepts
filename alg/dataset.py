import json
from dataclasses import dataclass, asdict
from typing import *
import pandas as pd


"""

########## Column markup implementation ##########

"""


@dataclass
class ColumnsDescription:
    label: int = None
    features: Dict[str, int] = None
    cat_features: List[int] = None
    floating_features: List[int] = None
    int_features: List[int] = None
    bool_features: List[int] = None


def create_cd(df: pd.DataFrame,
              label: Union[str, int] = None,
              cat_features: Iterable[Union[int, str]] = None,
              floating_features: Iterable[Union[int, str]] = None,
              int_features: Iterable[Union[int, str]] = None,
              bool_features: Iterable[Union[int, str]] = None,
              output_path: str = 'train_cd.json'
              ) -> ColumnsDescription:
    """

    :param df: pandas.DataFrame

    :param label: A zero-based index of the column that defines the target variable (only for classification)

    :param cat_features: Zero-based indices (or names) of columns that define categorical features

    :param floating_features: Zero-based indices (or names) of columns that define numeric (floating) features

    :param int_features: Zero-based indices (or names) of columns that define numeric (integer) features

    :param bool_features: Zero-based indices (or names) of columns that define bool (0/1) features

    :param output_path: Path to output file with columns description (if None

    :returns: ColumnsDescription
    """

    col2ind = dict(zip(list(df), list(range(len(list(df))))))

    def to_ind(t_features: Union[None, Iterable[Union[int, str]]]) -> Union[None, List[int]]:
        if t_features is None:
            return None

        t_features_ind = []
        for f in t_features:
            if isinstance(f, int):
                if 0 <= f < len(col2ind):
                    t_features_ind.append(f)
                else:
                    raise IndexError('feature index out of range')
            elif isinstance(f, str):
                try:
                    t_features_ind.append(col2ind[f])
                except KeyError:
                    raise IndexError(f'Unknown column name {f}')
            else:
                raise TypeError('Unexpected type for index. Expected types: int and str')

        return t_features_ind

    if isinstance(label, int) and label is not None:
        if not (0 <= label < len(col2ind)):
            raise IndexError('feature index out of range')
    elif isinstance(label, str) and label is not None:
        try:
            label = col2ind[label]
        except KeyError:
            raise IndexError(f'Unknown column name {label}')
    elif label is not None:
        raise TypeError('Unexpected type for index. Expected types: int and str')
    else:
        pass

    cat_features = to_ind(cat_features)
    floating_features = to_ind(floating_features)
    int_features = to_ind(int_features)
    bool_features = to_ind(bool_features)

    cd = ColumnsDescription(label=label,
                            features=col2ind,
                            cat_features=cat_features,
                            floating_features=floating_features,
                            int_features=int_features,
                            bool_features=bool_features)

    write_cd(cd, output_path)

    return cd


def write_cd(cd: ColumnsDescription, write_path: str = 'train_cd.json') -> None:
    if write_path is None:
        pass
    else:
        with open(write_path, 'w') as out:
            json.dump(asdict(cd), out)


def read_cd(read_path: str = 'train_cd.json') -> ColumnsDescription:
    with open(read_path, 'r') as read:
        return ColumnsDescription(**json.load(read))


"""

########## Sample implementation ##########

"""

class Sample:
    def __init__(self,
                 data: pd.DataFrame,
                 cd: ColumnsDescription = None,
                 label: Union[str, int] = None,
                 cat_features: Iterable[Union[int, str]] = None,
                 floating_features: Iterable[Union[int, str]] = None,
                 int_features: Iterable[Union[int, str]] = None,
                 bool_features: Iterable[Union[int, str]] = None,
                 cd_output_path: str = 'train_cd.json'
                 ) -> None:
        self.data = data

        if cd is not None:
            self.cd = cd
        else:
            self.cd = create_cd()
