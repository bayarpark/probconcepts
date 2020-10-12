import core.measures as measures
from typing import *


class FindParams:
    def __init__(self, dataset: [bool], obj_num: int, features_number: int):
        self.dataset = dataset
        self.obj_num = obj_num
        self.features_number = features_number


class Literal:

    def __init__(self, ident: int, val: bool):
        if type(ident) is not int:
            raise TypeError("Literal must have an identifier of type int")
        elif ident < 0:
            raise ValueError("`ident` must be in 0..features_num")
        else:
            self.__ident = ident
            self.__val = val

    def __eq__(self, other):
        return self.__ident == other.__ident and self.__val == other.__val

    def __hash__(self):
        return hash((self.__ident, self.__val))

    def __len__(self):
        return 1

    def is_positive(self) -> bool:
        return self.__val

    def is_negative(self) -> bool:
        return not self.__val

    def id(self) -> int:
        return self.__ident

    def val(self) -> bool:
        return self.__val

    def __str__(self):
        if self.__val:
            return f"P{self.__ident}"
        else:
            return f"~P{self.__ident}"

    def __invert__(self):
        return Literal(self.__ident, not self.__val)


class UndefinedLiteral(Literal):
    """
    Неопределенный литерал
    """
    def __init__(self):
        super().__init__(0, False)
        self._Literal__ident = -1

    def __str__(self):
        return "undefLit"


class Rule:
    __prob = None
    __p_value = None

    def __init__(self, conclusion: Literal, features=None):
        if features is None:
            features = []
        self.concl = conclusion
        self.features = features

    def __eq__(self, other):
        return self.concl == other.concl and self.features == other.features

    def __hash__(self):
        h = [self.concl]
        h.extend(self.features)
        return hash(tuple(h))

    def __str__(self):
        rule_str = ""
        for lit in self.features:
            rule_str += str(lit) + " & "
        rule_str = rule_str[:-2] + "=> " + str(self.concl)
        return rule_str

    def __len__(self):
        return len(self.features)

    def is_nonnegative(self) -> bool:
        return any(map(Literal.is_positive, self.features))
    
    def prob(self, par: FindParams) -> float:
        return self.evaluate(par)[0]
    
    def pvalue(self, par: FindParams) -> float:
        return self.evaluate(par)[1]

    def evaluate(self, par: FindParams) -> (float, float):
        if self.__prob is None or self.__p_value is None:
            self.__prob, self.__p_value = measures.std_prob_measure(self, par)
            return self.__prob, self.__p_value
        else:
            return self.__prob, self.__p_value


class Object:
    def __init__(self, data: [tuple]):  # Object = [(P_i: Bool, ~P_i: Bool)]
        self.data = data

    def check_contradiction(self) -> bool:
        return any(map(lambda x: x[0] and x[1], self.data))

    def completion(self):
        self.data = list(map(lambda x: (x[0], not x[0]), self.data))

    def decompletion(self):
        self.data = list(map(lambda x: (x[1], False), self.data))

    def rule_applicability(self, rule: Rule) -> bool:
        if type(rule) is not Rule:
            raise TypeError
        else:
            return all(map(lambda x: x in self, rule.features))

    def add(self, other: Literal):
        if type(other) is not Literal:
            raise TypeError
        else:
            self.data[other.id()] = (True, self.data[other.id()][1]) if other.val() \
                else \
                (self.data[other.id()][0], True)

    def delete(self, other: Literal):
        if type(other) is not Literal:
            raise TypeError
        else:
            self.data[other.id()] = \
                (False, self.data[other.id()][1]) if other.val() \
                else \
                (self.data[other.id()][0], False)

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self):
        return hash(tuple(self.data))

    def __len__(self):
        return sum(map(sum, self.data))

    def __contains__(self, item: Literal):
        return self.data[item.id()] == \
               self.data[item.id][0] and item.val() or self.data[item.id()][1] and not item.val()

    def __copy__(self):
        return Object(self.data[:])


class FixPoint(Object):
    def __init__(self, data: [tuple]):
        super().__init__(data)
        self.process = []

    def step_add(self, p: Literal, rules: [Rule]):
        self.add(p)
        self.process.append((p, rules))

    def step_del(self, p: Literal, rules: [Rule]):
        self.delete(p)
        self.process.append((p, rules))

    def __copy__(self):
        fp_copy = FixPoint(self.data[:])
        fp_copy.process = self.process[:]
        return fp_copy
