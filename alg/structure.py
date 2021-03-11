import pandas as pd
from typing import *
from lang.opers import *
from lang.predicate import Predicate
from lang.regularity import Regularity
from copy import copy, deepcopy
from alg.data import PredicateTable


class Object:
    table: Dict[int, Set[Predicate]] = None

    def __init__(self, data: Union[pd.Series, Dict], pt: PredicateTable = None) -> None:
        if pt is None and type(data) is dict:
            self.table = data
        else:
            self.table = {pt.pe.cd.features[col]: {pt.pe.transform(Predicate(col,
                                                                             vtype=Var(pt.pe.cd.type_dict[col]),
                                                                             opt='=',
                                                                             params=data[col]))} for col in data.keys()}

    def check_contradiction(self) -> bool:
        # contradiction if object contains p and ~p
        for feature in self.table.keys():
            for pr in self.table[feature]:
                if ~pr in self.table[feature]:
                    return True
        return False

    def completion(self, pt) -> None:
        # add all neg predicates for each pos predicate
        for feature in self.table.keys():
            new_features = set()
            for pr in self.table[feature]:
                new_features.add(pr)
                if pr.is_positive():
                    for pr_tuple in pt.table[feature]:
                        if pr_tuple[0] != pr:
                            new_features.add(pr_tuple[1])

            self.table[feature] = new_features

    def decompletion(self) -> None:
        # delete all neg predicates
        for feature in self.table.keys():
            pos_pr = set()
            for pr in self.table[feature]:
                if pr.is_positive():
                    pos_pr.add(pr)
                self.table[feature] = pos_pr

    def rule_applicability(self, reg: Regularity) -> bool:
        # проверяет, применимо ли правило к объекту, т.е.   #TODO  add transform mode
        # reg.premise подмножество self
        for pr in reg.premise:
            if pr not in self.table[pr.ident]:
                return False
        return True

    def add(self, p: Predicate) -> 'Object':
        # добавляет предикат в объект и возвращает копию    #TODO need deepcopy?
        new_obj = Object(deepcopy(self.table))
        new_obj.table[p.ident].add(p)
        return new_obj

    def delete(self, p: Predicate) -> 'Object':
        # удаляет предикат из объекта
        # first check is table contains predicate       #TODO add error
        self.table[p.ident].remove(p)
        new_obj = Object(deepcopy(self.table))
        new_obj.table[p.ident].remove(p)
        return new_obj

    def update(self, p: Predicate) -> None:
        self.table[p.ident].add(p)

    def remove(self, p: Predicate) -> None:
        self.table[p.ident].remove(p)

    @staticmethod
    def from_dict(new_dict: Dict[str, Set[Predicate]]) -> 'Object':
        return Object(data=new_dict)

    def to_dict(self) -> Dict:
        if type(self.table) is dict:
            return self.table
        else:                               # if pd.Series
            return self.table.to_dict()

    def __eq__(self, other: 'Object') -> bool:
        return self.table == other.table

    def __hash__(self) -> int:
        pass
        # return hash(self.table) can't hash dict[int : set]

    def __len__(self) -> int:
        # возвращает число предикатов в объекте
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
        return pr in self.table[pr.ident]

    def __copy__(self) -> 'Object':
        new_obj = Object(copy(self.table))
        return new_obj

    def __deepcopy__(self) -> 'Object':
        new_obj = Object(deepcopy(self.table))
        return new_obj


class FixPoint(Object):

    def __init__(self, data) -> None:
        super(FixPoint, self).__init__(data)
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
        fp_copy = FixPoint(self.data[:])
        fp_copy.process = self.process[:]
        return fp_copy


"""
class Object:
    def __init__(self, data: List[Tuple[bool, bool]]):  # Object = [(P_i: Bool, ~P_i: Bool)]
        self.data = data

    def check_contradiction(self) -> bool:
        return any(map(lambda x: x[0] and x[1], self.data))

    def completion(self) -> None:
        self.data = list(map(lambda x: (x[0], not x[0]), self.data))

    def decompletion(self) -> None:
        self.data = list(map(lambda x: (x[1], False), self.data))

    def rule_applicability(self, rule: Rule) -> bool:
        return all(map(lambda x: x in self, rule.features))

    def add(self, lit: Predicate) -> 'Object':
        self_copy = copy(self)
        if lit.val():
            self_copy.data[lit.id()] = (True, self.data[lit.id()][1])
        else:
            self_copy.data[lit.id()] = (self.data[lit.id()][0], True)
        return self_copy

    def delete(self, lit: Predicate) -> 'Object':
        self_copy = copy(self)
        if lit.val():
            self_copy.data[lit.id()] = (False, self.data[lit.id()][1])
        else:
            self_copy.data[lit.id()] = (self.data[lit.id()][0], False)
        return self_copy

    def __eq__(self, other) -> bool:
        return self.data == other.data

    def __hash__(self) -> int:
        return hash(tuple(self.data))

    def __len__(self) -> int:
        return sum(map(sum, self.data))

    def __contains__(self, item: Predicate) -> bool:
        return self.data[item.id()] == \
               self.data[item.id()][0] and item.val() or self.data[item.id()][1] and not item.val()

    def __copy__(self) -> 'Object':
        return Object(self.data[:])

"""
