import pandas as pd
from typing import *
from lang.opers import *
from lang.predicate import Predicate
from lang.regularity import Regularity
from copy import deepcopy



class Object:
    table: Dict[int, Set[Predicate]] = None

    def __init__(self, data: Union[pd.Series, Dict], pe: 'PredicateEncoder') -> None:
        self.table = {pe.cd.features[col]: {pe.transform(Predicate(col, vtype=Var(pe.cd.type_dict[col]), opt='=', \
                                                                   params=data[col]))} for col in data.keys()}

    def check_contradiction(self) -> bool:
        # проверка на противоречивость

        for col in self.table:
            for pr in self.table[col]:
                if ~pr in self.table[col]:
                    return True

        return False

    def completion(self) -> None:
        # добавляет все соответствующие отрицания предикатов

        for col in self.table:
            neg_pr = {}
            for pr in self.table[col]:
                neg_pr.add(~pr)
            self.table[col].update(neg_pr)


    def decompletion(self) -> None:
        # удаляет все отрицания предикатов

        for col in self.table:
            neg_pr = {}
            for pr in self.table[col]:
                if not pr.is_positive():
                    self.table[col].remove(pr)


    def rule_applicability(self, reg: Regularity) -> bool:
        # проверяет, применимо ли правило к объекту, т.е.
        # reg.premise подмножество self

        for pr in reg.premise:
            if pr not in self.table[pr.ident]:
                return False

        return True

    def add(self, p: Predicate) -> 'Object':
        # добавляет предикат в объект

        self.table[p.ident].add(p)

    def delete(self, p: Predicate) -> 'Object':
        # удаляет предикат из объекта

        # first check is table contains predicate #TODO add error
        self.table[p.ident].remove(p)

    def __eq__(self, other: 'Object') -> bool:
        return self.table == other.table

    def __hash__(self) -> int:
        pass
        # return hash(self.table) can't hash dict[int : set]

    def __len__(self) -> int:
        # возвращает число предикатов в объекте
        return sum(map(len, self.table))

    def __str__(self) -> str:
        return str(self.table)
    
    def __contains__(self, pr: Predicate) -> bool:
        # проверяет, содержит ли объект предикат item
        return pr in self.table[pr.ident]


    def __copy__(self) -> 'Object':
        pass


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
