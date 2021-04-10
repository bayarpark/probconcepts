from copy import copy, deepcopy

import pandas as pd

from .data import PredicateTable
from ..lang.opers import *
from ..lang.predicate import Predicate
from ..lang.regularity import Regularity
from ..utils.sys import is_none


class Object:
    table: Dict[int, Set[Predicate]] = None
    pt: PredicateTable = None

    # TODO add transform mode
    def __init__(self, data: Union[pd.Series, Dict],
                 pt: PredicateTable = None,
                 identifier: Union[str, int] = None) -> None:
        self.id = identifier
        if pt is None and type(data) is dict:
            self.table = data
        else:
            self.pt = pt
            self.table = {
                pt.pe.cd.features[col]: {
                    pt.pe.transform(
                        Predicate(col,
                                  vtype=Var(pt.pe.cd.type_dict[col]),
                                  opt='=',
                                  params=data[col]
                                  )
                    )
                } for col in data.keys() if not is_none(data[col])
            }

    def __iter__(self) -> Iterator:
        for k, v in self.table.items():
            for p in v:
                yield p

    def check_contradiction(self) -> bool:
        # contradiction if object contains p and ~p
        for feature in self.table.keys():
            for pr in self.table[feature]:
                if ~pr in self.table[feature]:
                    return True
        return False

    def completion(self, pt: PredicateTable = None) -> None:
        if self.pt is None and pt is None:
            raise TypeError("self.pt is empty. second argument 'pt' is required")
        elif pt is not None:
            self.pt = pt
        # add all neg predicates for each pos predicate
        for feature in self.table.keys():
            new_features = set()
            for pr in self.table[feature]:
                new_features.add(pr)
                if pr.is_positive():
                    for pr_tuple in self.pt.table[feature]:
                        if pr_tuple[0] != pr:
                            new_features.add(pr_tuple[1])

            self.table[feature] = new_features

    def decompletion(self) -> None:
        # delete all neg predicates
        new_table = {}
        for feature in self.table.keys():
            pos_pr = set()
            for pr in self.table[feature]:
                if pr.is_positive() or pr.vtype == Var.Bool:
                    pos_pr.add(pr)
            if len(pos_pr) != 0:
                new_table[feature] = pos_pr

        self.table = new_table

    def rule_applicability(self, reg: Regularity) -> bool:
        # проверяет, применимо ли правило к объекту, т.е.   #TODO add transform mode
        # reg.premise подмножество self
        for pr in reg.premise:
            if (pr_set := self.table.get(pr.ident)) is not None and pr not in pr_set:
                return False
        return True

    def add(self, p: Predicate) -> 'Object':
        # добавляет предикат в объект и возвращает копию    #TODO need deepcopy?
        new_obj = Object(deepcopy(self.table))
        if (new_pr_set := new_obj.table.get(p.ident)) is not None:
            new_pr_set.add(p)
        else:
            new_obj.table[p.ident] = {p}

        return new_obj

    def delete(self, p: Predicate) -> 'Object':
        # удаляет предикат из объекта
        # first check is table contains predicate       #TODO add error
        if p not in self.table[p.ident]:
            raise ValueError("Attempt to delete a nonexistent predicate")

        new_obj = Object(deepcopy(self.table))
        new_obj.table[p.ident].remove(p)
        return new_obj

    def update(self, p: Predicate) -> None:
        self.table[p.ident].add(p)

    def remove(self, p: Predicate) -> None:
        self.table[p.ident].remove(p)

    @staticmethod
    def from_dict(new_dict: Dict) -> 'Object':
        return Object(data={k: set(map(lambda x: Predicate.from_dict(x), v)) for k, v in new_dict['data'].items()},
                      identifier=new_dict['id'])

    def to_dict(self) -> Dict:
        return {'data': {k: list(map(lambda x: x.to_dict(), v)) for k, v in self.table.items()}, 'id': self.id}

    def __inverse_transform__(self, pe) -> 'Object':
        return Object(data={k: set(map(pe.inverse_transform, v)) for k, v in self.table.items()})

    def __eq__(self, other: 'Object') -> bool:
        return self.table == other.table

    def __len__(self) -> int:
        return sum(map(len, self.table.values()))

    def __str__(self) -> str:
        str_obj = ""
        for feature in self.table.keys():
            str_obj += str(feature) + ": {"
            for pr in self.table[feature]:
                str_obj += str(pr)
            str_obj += "} "
        return str_obj

    def __contains__(self, pr: Predicate) -> bool:
        # проверяет, содержит ли объект предикат item
        return pr in self.table.get(pr.ident, [])

    def __copy__(self) -> 'Object':
        new_obj = Object(copy(self.table))
        return new_obj

    def __deepcopy__(self) -> 'Object':
        new_obj = Object(deepcopy(self.table))
        return new_obj


class FixPoint(Object):

    def __init__(self, data, pt, ident) -> None:
        super(FixPoint, self).__init__(data, pt, ident)
        self.process = []

    def step_add(self, p: Predicate, rules: List[Regularity]) -> 'FixPoint':
        self_copy = self.add(p)
        self_copy.process.append((p, rules))
        return self_copy

    def step_del(self, p: Predicate, rules: List[Regularity]) -> 'FixPoint':
        self_copy = self.delete(p)
        self_copy.process.append((p, rules))
        return self_copy

    def __copy__(self) -> 'FixPoint':
        fp_copy = FixPoint(copy(self.table))
        fp_copy.process = self.process[:]
        return fp_copy

