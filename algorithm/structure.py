import algorithm.measures as measures
from dataclasses import dataclass
from enum import Enum, auto
from copy import copy
from typing import *
from algorithm.model import *

# При добавлении новых типов переменных их семантику необходимо прописать в Predicate
# и добавить необходимые операции в Oper


class Var(Enum):
    Bin = auto()        # {T, F}
    Nom = auto()        # {named}
    Int = auto()        # Int
    Real = auto()       # float

    @staticmethod
    def isbin(vart: 'Var') -> bool:
        return vart == Var.Bin
    
    @staticmethod
    def isnom(vart: 'Var') -> bool:
        return vart == Var.Nom
    
    @staticmethod
    def isint(vart: 'Var') -> bool:
        return vart == Var.Int
    
    @staticmethod
    def isreal(vart: 'Var') -> bool:
        return vart == Var.Real

# При добавлении новых операций в Oper их семантику необходимо прописать в Predicate


class Oper(Enum):
    eq = '='            # x == c
    neq = '!='          # x != c
    le = '<'            # x < c
    leq = '<='          # x <= c
    ge = '>'            # x > c
    geq = '>='          # x >= c
    interval = auto()   # x in [a, b]
    tails = auto()      # x not in [a, b]
    
    @staticmethod
    def iseq(opt: 'Oper') -> bool:
        return opt == Oper.eq
   
    @staticmethod
    def isneq(opt: 'Oper') -> bool:
        return opt == Oper.neq
   
    @staticmethod
    def isle(opt: 'Oper') -> bool:
        return opt == Oper.le
   
    @staticmethod
    def isleq(opt: 'Oper') -> bool:
        return opt == Oper.leq
   
    @staticmethod
    def isge(opt: 'Oper') -> bool:
        return opt == Oper.ge   
    
    @staticmethod
    def isgeq(opt: 'Oper') -> bool:
        return opt == Oper.geq    
    
    @staticmethod
    def isinterval(opt: 'Oper') -> bool:
        return opt == Oper.interval

    @staticmethod
    def istails(opt: 'Oper') -> bool:
        return opt == Oper.tails

    @staticmethod
    def is_binary(opt: 'Oper') -> bool:
        return opt in [Oper.eq, Oper.neq, Oper.ge, Oper.geq, Oper.le, Oper.geq]


class Predicate:
    def __init__(self,
                 opt: Oper,
                 vart: Var,
                 ident: int,
                 args: Union[int, bool, float, Tuple[float, float], Tuple[int, int]]) -> None:
        self.opt = opt
        self.vart = vart
        self.ident = ident
        self.arg = args
        self.__typecheck()
        self.__normalize()

    def __call__(self, x: Union[int, bool, float]) -> bool:
        if Oper.iseq(self.opt):
            return self.arg == x

        elif Oper.isneq(self.opt):
            return self.arg != x

        elif Oper.isle(self.opt):
            return x < self.arg

        elif Oper.isleq(self.opt):
            return x <= self.arg

        elif Oper.isge(self.opt):
            return x > self.arg

        elif Oper.isgeq(self.opt):
            return x >= self.arg

        elif Oper.isinterval(self.opt):
            return self.arg[0] <= x <= self.arg[1]

        elif Oper.istails(self.opt):
            return not (self.arg[0] <= x <= self.arg[1])

        else:
            raise NotImplementedError("Semantic for `opt` is not implemented")

    def __invert__(self) -> 'Predicate':
        inverted = Predicate(self.opt, self.vart, self.ident, self.arg)
        if Oper.iseq(inverted.opt):
            inverted.opt = Oper.neq
            inverted.__normalize()

        elif Oper.isneq(inverted.opt):
            inverted.opt = Oper.eq

        elif Oper.isle(inverted.opt):
            inverted.opt = Oper.geq

        elif Oper.isleq(inverted.opt):
            inverted.opt = Oper.ge

        elif Oper.isge(inverted.opt):
            inverted.opt = Oper.leq

        elif Oper.isgeq(inverted.opt):
            inverted.opt = Oper.le

        elif Oper.isinterval(inverted.opt):
            inverted.opt = Oper.tails

        elif Oper.istails(inverted.opt):
            inverted.opt = Oper.interval

        else:
            raise NotImplementedError("Semantic for `opt` is not implemented")

        return inverted

    def __str__(self) -> str:
        if Oper.is_binary(self.opt):
            return f"[x{self.ident} {self.opt.value} {self.arg}]"
        elif Oper.isinterval(self.opt):
            return f"[x{self.ident} in {self.arg[0]}, {self.arg[1]}]"
        elif Oper.istails(self.opt):
            return f"[x{self.ident} nin {self.arg[0]}, {self.arg[1]}]"
        else:
            raise NotImplementedError("Semantic for `opt` is not implemented")

    def __eq__(self, other: 'Predicate') -> bool:
        return self.vart == other.vart and self.opt == other.opt and \
            self.ident == other.ident and self.arg == other.arg

    def __hash__(self) -> int:
        return hash((self.opt, self.vart, self.ident, self.arg))

    def __len__(self) -> int:
        return 1

    def is_positive(self) -> bool:
        if Oper.isneq(self.opt) or (Var.isbin(self.vart) and not self.arg) or \
                Oper.istails(self.opt):
            return False

        else:
            return True

    def __normalize(self) -> None:
        if Oper.isneq(self.opt) and Var.isbin(self.vart):
            self.opt = Oper.eq
            self.arg = not self.arg

    def __typecheck(self) -> None:
        if Oper.is_binary(self.opt):
            if ((Var.isnom(self.vart)) or Var.isbin(self.vart)) and (self.opt != Oper.eq or self.opt != Oper.neq):
                raise TypeError("For 'Var.Nom' and 'Var.Bin' only 'Oper.eq' and 'Oper.neq' is allowed")

            elif (Var.isint(self.vart) or Var.isnom(self.vart)) and isinstance(self.arg, int) or \
                    (Var.isreal(self.vart)) and isinstance(self.arg, float) or \
                    Var.isbin(self.vart) and isinstance(self.arg, bool):
                pass
            else:
                raise ValueError("var and args must be some type")

        elif self.opt == Oper.interval:
            if Var.isint(self.vart) and isinstance(self.arg, (int, int)) or \
                    Var.isreal(self.vart) and isinstance(self.arg, (float, float)):
                pass
            else:
                raise ValueError("var and args must be some type")
        else:
            raise TypeError("Unknown semantic for operation")


class Regularity:
    pass




"""

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
        '''
        Проверяет, что в посылке правила есть хотя бы один позитивный предикат
        '''
        return any(map(Predicate.is_positive, self.features))

    def enhance(self, lit: Predicate) -> 'Rule':
        return Rule(self.concl, self.features[:].append(lit))

    def prob(self, par: FindParams) -> float:
        return self.evaluate(par)[0]

    def p_value(self, par: FindParams) -> float:
        return self.evaluate(par)[1]

    def evaluate(self, par: FindParams) -> Tuple[float, float]:
        '''
        Расчет вероятности и p-значения, если это еще не было сделано

        :param par: Параметры поиска / идеализации
        :return: Условная вероятность и p-значение
        '''
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

"""
