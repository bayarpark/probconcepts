import algorithm.measures as measures
from dataclasses import dataclass
from copy import copy
from typing import *


@dataclass()
class FindParams:
    dataset: List[List[int]]
    dataset_size: int
    features_number: int


class Predicate:

    def __init__(self, ident: int, val: bool) -> None:
        if ident < 0:
            raise ValueError("`ident` must be in 0..`features_number`")
        else:
            self.__ident = ident
            self.__val = val

    def __eq__(self, other) -> bool:
        return self.__ident == other.__ident and self.__val == other.__val

    def __hash__(self) -> int:
        return hash((self.__ident, self.__val))

    def __len__(self) -> int:
        return 1

    def is_positive(self) -> bool:
        return self.__val

    def is_negative(self) -> bool:
        return not self.__val

    def id(self) -> int:
        return self.__ident

    def val(self) -> bool:
        return self.__val

    def __str__(self) -> str:
        if self.__val:
            return f"P{self.__ident}"
        else:
            return f"~P{self.__ident}"

    def __call__(self, obj: 'Object') -> bool:
        pass

    def __invert__(self) -> 'Predicate':
        return Predicate(self.__ident, not self.__val)


class UndefinedPredicate(Predicate):
    """
    Неопределенный литерал
    """

    def __init__(self) -> None:
        super().__init__(0, False)
        self._Predicate__ident = -1

    def __str__(self) -> str:
        return "undefLit"


class Rule:
    __prob: float = None
    __p_value: float = None

    def __init__(self, conclusion: Predicate, features: List[Predicate] = None) -> None:
        if features is None:
            features = []
        self.concl = conclusion
        self.features = features

    def __eq__(self, other: 'Rule') -> bool:
        return self.concl == other.concl and self.features == other.features

    def __hash__(self) -> int:
        h = [self.concl]
        h.extend(self.features)
        return hash(tuple(h))

    def __str__(self) -> str:
        rule_str = ""
        for lit in self.features:
            rule_str += str(lit) + " & "
        rule_str = rule_str[:-2] + "=> " + str(self.concl)
        return rule_str

    def writefile(self, file: Any) -> None:
        pass

    def __len__(self) -> int:
        return len(self.features)

    def is_nonnegative(self) -> bool:
        """
        Проверяет, что в посылке правила есть хотя бы один позитивный предикат
        """
        return any(map(Predicate.is_positive, self.features))

    def enhance(self, lit: Predicate) -> 'Rule':
        return Rule(self.concl, self.features[:].append(lit))

    def prob(self, par: FindParams) -> float:
        return self.evaluate(par)[0]

    def p_value(self, par: FindParams) -> float:
        return self.evaluate(par)[1]

    def evaluate(self, par: FindParams) -> Tuple[float, float]:
        """
        Расчет вероятности и p-значения, если это еще не было сделано

        :param par: Параметры поиска / идеализации
        :return: Условная вероятность и p-значение
        """
        if self.__prob is None or self.__p_value is None:
            self.__prob, self.__p_value = measures.std_prob_measure(self, par)
            return self.__prob, self.__p_value
        else:
            return self.__prob, self.__p_value


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


class FixPoint(Object):
    def __init__(self, data: List[Tuple[bool, bool]]) -> None:
        super().__init__(data)
        self.process = []

    def step_add(self, p: Predicate, rules: List[Rule]) -> 'FixPoint':
        self_copy = self.add(p)
        self_copy.process.append((p, rules))
        return self_copy

    def step_del(self, p: Predicate, rules: List[Rule]) -> 'FixPoint':
        self_copy = self.delete(p)
        self_copy.process.append((p, rules))
        return self_copy

    def __copy__(self) -> 'FixPoint':
        fp_copy = FixPoint(self.data[:])
        fp_copy.process = self.process[:]
        return fp_copy
