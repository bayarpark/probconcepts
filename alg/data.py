import json
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import *
import numpy as np
import pandas as pd
from copy import copy

from lang.opers import Eq, Neq, Var, Oper, Opers
from lang.predicate import Predicate
from lang.regularity import Regularity

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
    type_dict: Dict[str, Var] = None


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

    def get_col_type(col: str) -> str:
        if bool_features is not None and col2ind[col] in bool_features:
            return 'B'
        elif cat_features is not None and col2ind[col] in cat_features:
            return 'C'
        elif int_features is not None and col2ind[col] in int_features:
            return 'I'
        elif floating_features is not None and col2ind[col] in floating_features:
            return 'F'

    type_dict = {col: get_col_type(col) for col in df.columns}
    cat_features = to_ind(cat_features)
    floating_features = to_ind(floating_features)
    int_features = to_ind(int_features)
    bool_features = to_ind(bool_features)
    cd = ColumnsDescription(label=label,
                            features=col2ind,
                            cat_features=cat_features,
                            floating_features=floating_features,
                            int_features=int_features,
                            bool_features=bool_features,
                            type_dict=type_dict)

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

    def transform(self, obj: Union[
                    pd.DataFrame, pd.Series, Predicate, Any]
                  ) -> Union[pd.DataFrame, pd.Series, Predicate, Any]:

        if isinstance(obj, pd.DataFrame):
            transformed_obj = obj.copy(deep=True)

            # Replace cat_features
            if (cf := self.encoding.get('cat_features')) is not None:
                for column, to_replace_dict in cf.items():
                    transformed_obj.iloc[:, column] = obj.iloc[:, column].map(to_replace_dict).astype('Int64')

            # Replace bool_features
            if (bf := self.encoding.get('bool_features')) is not None:
                for column, to_replace_dict in bf.items():
                    transformed_obj.iloc[:, column] = obj.iloc[:, column].map(to_replace_dict).astype('boolean')

            return transformed_obj

        elif isinstance(obj, pd.Series):
            pass  # TODO
        elif isinstance(obj, Predicate):
            if Var.iscat(obj.vtype):
                tmp_op = copy(obj.operation)
                tmp_op.params = self.encoding['cat_features'][self.cd.features[obj.name]][obj.operation.params]
                transformed_pr = Predicate(
                    ident=self.cd.features[obj.name],
                    vtype=obj.vtype,
                    operation=tmp_op)

            elif Var.isbin(obj.vtype):
                tmp_op = copy(obj.operation)
                tmp_op.params = self.encoding['bool_features'][self.cd.features[obj.name]][obj.operation.params]
                transformed_pr = Predicate(
                    ident=self.cd.features[obj.name],
                    vtype=obj.vtype,
                    operation=tmp_op)

            elif Var.isint(obj.vtype):
                transformed_pr = Predicate(
                    ident=self.cd.features[obj.name],
                    vtype=obj.vtype,
                    operation=obj.operation)

            elif Var.isreal(obj.vtype):
                transformed_pr = Predicate(
                    ident=self.cd.features[obj.name],
                    vtype=obj.vtype,
                    operation=obj.operation)
            else:
                raise TypeError('Unexpected type')

            return transformed_pr

        elif isinstance(obj, Regularity):
            transformed_rg = Regularity(
                self.transform(obj.conclusion),
                [self.transform(p) for p in obj.premise]
            )
            return transformed_rg
        else:
            raise TypeError(f'{type(obj)} type is untransformable')

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
    used_predicate: Dict[int, List[List[bool]]] = None

    def __init__(self,
                 pe: PredicateEncoder = None,
                 df: pd.DataFrame = None,
                 cd: ColumnsDescription = None) -> None:
        self.pe = pe
        self.df = df
        self.cd = cd

    def __iter__(self) -> Iterator:
        for k, v in self.table.items():
            for k_used in range(len(v_used := self.used_predicate[k])):
                if v_used[k_used][0]:
                    yield self.table[k][k_used][0]
                if v_used[k_used][1]:
                    yield self.table[k][k_used][1]

    def init(self, p: Predicate) -> 'PredicateTable':
        if self.table is None:
            raise AttributeError("Generate PT first")

        new_pe = PredicateTable()
        new_pe.table = self.table
        new_pe.used_predicate = deepcopy(self.used_predicate)

        for k in range(len(lp := new_pe.table[p.ident])):
            if p == lp[k][0] or p == lp[k][0]:
                new_pe.used_predicate[p.ident][k][0] = False
                new_pe.used_predicate[p.ident][k][1] = False

        return new_pe

    def drop(self, p: Predicate) -> 'PredicateTable':
        """
        Метод запрещает использование предиката p при
        """
        if self.table is None:
            raise AttributeError("Generate PT first")

        new_pe = PredicateTable()
        new_pe.table = self.table
        new_pe.used_predicate = deepcopy(self.used_predicate)

        if p.is_positive():
            for k in range(len(upr := new_pe.used_predicate[p.ident])):
                if p != new_pe.table[p.ident][k][0]:
                    upr[k][0] = False
                else:
                    upr[k][0] = False
                    upr[k][1] = False
        else:
            for k in range(len(upr := new_pe.used_predicate[p.ident])):
                if new_pe.table[p.ident][k][1] == p:
                    upr[k][1] = False
                    upr[k][0] = False

        return new_pe

    def fit(self) -> None:

        """
        Метод создает кодировку предикатов на выборке. В результате работы в self.encoding
        записывается таблица со всевозможными предикатами и их отрицаниями
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
                        Predicate(ident=feature_num, vtype=Var.Cat, operation=Eq(val)),
                        Predicate(ident=feature_num, vtype=Var.Cat, operation=Neq(val))
                    )
                    for val in feature_vals.values()
                ]

        if (boolf := self.pe.encoding['bool_features']) is not None:
            for (feature_num, feature_vals) in boolf.items():
                self.table[feature_num] = [
                    (
                        Predicate(ident=feature_num, vtype=Var.Bool, operation=Eq(True)),
                        Predicate(ident=feature_num, vtype=Var.Bool, operation=Eq(False))
                    )
                ]

        if self.pe.encoding['floating_features'] is not None:
            pass  # TODO

        if self.pe.encoding['int_features'] is not None:
            pass  # TODO

        # create a special table for using flags
        self.used_predicate = {k: [[True, True] for _ in range(len(self.table[k]))] for k in self.table.keys()}


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

        self.pt = PredicateTable(self.pe, data)
        self.pt.fit()
        self.shape = data.shape
        self.data = self.pe.transform(data)
        self.data = self.data.values.tolist()

        replace_missing_values(self.data, self.shape)


def replace_missing_values(data: List[List],
                           shape: Tuple[int, int] = None) -> None:

    for i in range(shape[0]):
        for j in range(shape[1]):
            if (el := data[i][j]) is pd.NA or el is np.nan:
                data[i][j] = None


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
