import json
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import *
import numpy as np
import pandas as pd

from lang.opers import Eq, Neq, Var
from lang.predicate import Predicate

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

    :param bool_features: Zero-based indices (or names) of columns that define binary (not only T,F or 0,1) features

    :param output_path: Path to output file with columns description (if None will NOT print)

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
            json.dump(asdict(cd), out, indent=4)


def read_cd(read_path: str = 'train_cd.json') -> ColumnsDescription:
    with open(read_path, 'r') as read:
        return ColumnsDescription(**json.load(read))


class PredicateEncoder:
    encoding: Dict = None
    cd: ColumnsDescription = None

    def __init__(self, cd: ColumnsDescription) -> None:
        self.cd = cd

    def fit(self, df: pd.DataFrame,
            output_path='train_encoding.json') -> None:

        """
        Метод создает кодировку предикатов: категориальные переводит в числовые, бинарные в булевы,
        числовые (с плавающей точкой и целочисленные) бьет на интервалы и печатает кодировку в файл

        :param df: pd.DataFrame with train sample
        :param output_path: Path to output file with columns description (if None will NOT print)
        """
        if self.encoding is not None:
            pass

        else:
            cat_encoding, floating_encoding, int_encoding, bool_encoding = None, None, None, None

            if self.cd.cat_features is not None:
                cat_encoding = {}
                for c in self.cd.cat_features:
                    column = df.iloc[:, c]
                    if pd.api.types.is_integer_dtype(column):
                        try:
                            cat_encoding[c] = dict(
                                zip(q := column.dropna().unique().tolist(), q)
                            )
                        except AttributeError:
                            cat_encoding[c] = dict(
                                zip(q := column.dropna().unique().to_numpy().tolist(), q)
                            )
                    elif pd.api.types.is_object_dtype(column):
                        try:
                            cat_encoding[c] = dict(
                                zip(q := column.dropna().unique().tolist(), range(len(q)))
                            )
                        except AttributeError:
                            cat_encoding[c] = dict(
                                zip(q := column.dropna().unique().to_numpy().to_list(), range(len(q)))
                            )
                    elif pd.api.types.is_bool_dtype(column):
                        cat_encoding[c] = {False: 0, True: 1}
                    else:
                        raise TypeError('Categorical features must have types "int", "str" or "bool"')

            if self.cd.bool_features is not None:
                bool_encoding = {}
                for b in self.cd.bool_features:
                    column = df.iloc[:, b]
                    if pd.api.types.is_bool_dtype(column):
                        bool_encoding[b] = {False: False, True: True}
                    elif len(unique := column.dropna().unique()) == 2:
                        bool_encoding[b] = dict(zip(unique, [False, True]))
                    else:
                        raise ValueError('Feature must have only two values')

            if self.cd.floating_features is not None:
                floating_encoding = {}
                for f in self.cd.floating_features:
                    column = df.iloc[:, f]
                    if column.dtype == float:
                        pass  # TODO FLOAT ENCODING, НЕ ЗАБЫВАЙ ПРО NANы
                    else:
                        raise TypeError('Floating features must have type "float"')

            if self.cd.int_features is not None:
                int_encoding = {}
                for i in self.cd.int_features:
                    column = df.iloc[:, i]
                    if column.dtype == int:
                        pass  # TODO CONTINUOUS INT ENCODING
                    else:
                        raise TypeError('Integer features must have type "int"')

            self.encoding = {
                'cat_features': cat_encoding,
                'floating_features': floating_encoding,
                'int_features': int_encoding,
                'bool_features': bool_encoding
            }

            if output_path is not None:
                with open(output_path, 'w') as out:
                    json.dump(self.encoding, out, indent=4)

    def transform(self, df: pd.DataFrame) -> List[List[Union[int, float, bool]]]:
        pass

    def inverse_transfrom(self) -> pd.DataFrame:
        pass

    def read_encoding(self, read_path: str = 'train_encoding.json') -> None:
        with open(read_path, 'r') as read:
            self.encoding = json.load(read)


class PredicateTable:
    df: pd.DataFrame = None
    cd: ColumnsDescription = None
    pe: PredicateEncoder = None
    table: Dict[int, List[Tuple[Predicate, Predicate]]] = None  # TODO REFORMAT

    def __init__(self,
                 pe: PredicateEncoder = None,
                 df: pd.DataFrame = None,
                 cd: ColumnsDescription = None) -> None:
        self.pe = pe
        self.df = df
        self.cd = cd

    def __iter__(self) -> Iterator:
        q = []
        for v1 in self.table.values():
            for v2 in v1:
                for p in v2:
                    if p.use:
                        q.append(p)

        return iter(q)

    def drop(self, p: Predicate) -> 'PredicateTable':
        if self.table is None:
            raise AttributeError("Generate PT first")

        new_pe = PredicateTable()
        new_pe.table = deepcopy(self.table)
        if True:  # p.vartype == Var.Nom or p.vartype == Var.Bool:
            if p.is_positive():
                for p_tuple in new_pe.table[p.ident]:
                    if p_tuple[0] != p:
                        p_tuple[0].use = False
                    else:
                        p_tuple[0].use = False
                        p_tuple[1].use = False
            else:
                for p_tuple in new_pe.table[p.ident]:
                    if p_tuple[1] == p:
                        p_tuple[1].use = False
                        p_tuple[0].use = False
        # else:
        #    pass  # TODO

        return new_pe

    def generate_pt(self) -> None:

        """

        """

        if self.pe is None:
            if self.cd is not None and self.df is not None:
                self.pe = PredicateEncoder(cd=self.cd)
                self.pe.fit(df=self.df)
            else:
                raise AttributeError('To generate PredicateTable you need ')

        self.table = {}
        if self.pe.encoding is None:
            raise AttributeError('Please, read or generate encoding first')

        if (cat := self.pe.encoding['cat_features']) is not None:
            for feature_num, feature_vals in cat.items():
                self.table[feature_num] = [
                    (
                        Predicate(ident=feature_num, vartype=Var.Nom, operation=Eq(val)),
                        Predicate(ident=feature_num, vartype=Var.Nom, operation=Neq(val))
                    )
                    for val in feature_vals.values()
                ]

        if (boolf := self.pe.encoding['bool_features']) is not None:
            for (feature_num, feature_vals) in boolf.items():
                self.table[feature_num] = [
                    (
                        Predicate(ident=feature_num, vartype=Var.Bool, operation=Eq(True)),
                        Predicate(ident=feature_num, vartype=Var.Bool, operation=Eq(False))
                    )
                ]

        if self.pe.encoding['floating_features'] is not None:
            pass  # TODO

        if self.pe.encoding['int_features'] is not None:
            pass  # TODO


"""

########## Sample implementation ##########

"""


class Sample:
    data: List = None
    pt: PredicateTable = None
    pe: PredicateEncoder = None
    cd: ColumnsDescription = None
    shape: Tuple[int, int] = None

    def __init__(self,
                 data: pd.DataFrame,
                 pe: PredicateEncoder = None,
                 cd: ColumnsDescription = None,
                 # if you want create cd in Sample:
                 label: Union[str, int] = None,
                 cat_features: Iterable[Union[int, str]] = None,
                 floating_features: Iterable[Union[int, str]] = None,
                 int_features: Iterable[Union[int, str]] = None,
                 bool_features: Iterable[Union[int, str]] = None,
                 cd_output_path: Union[str, None] = 'train_cd.json',
                 # if you want create encoding in Sample:
                 encoding_output_path: Union[str, None] = 'train_encode.json'
                 ) -> None:

        if cd is None:
            cd = create_cd(df=data, label=label,
                           cat_features=cat_features,
                           floating_features=floating_features,
                           int_features=int_features,
                           bool_features=bool_features,
                           output_path=cd_output_path)
        self.cd = cd
        if pe is None:
            self.pe = PredicateEncoder(cd=cd)
            self.pe.fit(df=data, output_path=encoding_output_path)
        else:
            self.pe = pe

        data = data.copy()

        if cd is not None:
            self.cd = cd
        else:
            self.cd = create_cd(data, label, cat_features, floating_features,
                                int_features, bool_features, cd_output_path)

        # Replace cat_features
        if (cf := self.pe.encoding.get('cat_features')) is not None:
            for column, to_replace_dict in cf.items():
                data.iloc[:, column] = data.iloc[:, column].map(to_replace_dict).astype('Int64')

        # Replace bool_features
        if (bf := self.pe.encoding.get('bool_features')) is not None:
            for column, to_replace_dict in bf.items():
                data.iloc[:, column] = data.iloc[:, column].map(to_replace_dict).astype('boolean')

        self.shape = data.shape
        self.data = data.values.tolist()

        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if (el := self.data[i][j]) is pd.NA or el is np.nan:
                    self.data[i][j] = None


def missing_cat_bool_typecast(df: pd.DataFrame, cd: ColumnsDescription) -> pd.DataFrame:
    """
    NOTICE: DANGER ACTION!
    """
    new_df = df.copy()
    if cd.cat_features is not None:
        for cf in cd.cat_features:
            if any((col := df.iloc[:, cf]).isna()):
                if pd.api.types.is_float_dtype(col):
                    new_df.iloc[:, cf] = col.astype('Int64')
                else:
                    new_df.iloc[:, cf] = col.astype(object)

    if cd.bool_features is not None:
        for bf in cd.bool_features:
            if any((col := df.iloc[:, bf]).isna()):
                new_df.iloc[:, bf] = col.astype(object)

    return new_df
