from enum import Enum, auto
from typing import *


class Var(Enum):
    # При добавлении новых типов переменных их семантику необходимо прописать в Predicate
    # и добавить необходимые операции в Oper
    Bin = auto()  # {T, F}
    Nom = auto()  # {named}
    Int = auto()  # Int
    Real = auto()  # float
    undefined = auto()  # special undefined type

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


class Oper(Enum):
    # При добавлении новых операций в Oper их семантику необходимо прописать в Predicate
    eq = '='  # x == c
    neq = '!='  # x != c
    le = '<'  # x < c
    leq = '<='  # x <= c
    ge = '>'  # x > c
    geq = '>='  # x >= c
    interval = auto()  # x in [a, b]
    tails = auto()  # x not in [a, b]

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
