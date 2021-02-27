import pandas as pd
from typing import *
from lang.predicate import Predicate
from lang.regularity import Regularity
from copy import deepcopy


class Object:
    table: Dict[int, List[Tuple[Predicate, Predicate]]] = None

    def __init__(self, data) -> None:
        self.data = data

    def check_contradiction(self) -> bool:
        pass

    def completion(self) -> None:
        pass

    def decompletion(self) -> None:
        pass

    def rule_applicability(self, reg: Regularity) -> bool:
        pass

    def add(self, p: Predicate) -> 'Object':
        pass

    def delete(self, p: Predicate) -> 'Object':
        pass

    def __eq__(self, other: 'Object') -> bool:
        return self.table == other.table

    def __hash__(self) -> int:
        return hash(self.table)

    def __len__(self) -> int:
        pass

    def __contains__(self, item: Predicate) -> bool:
        pass

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
