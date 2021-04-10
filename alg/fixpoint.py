from copy import copy
from math import log as mlog
from typing import *

from .model import BaseModel
from .structure import Object, FixPoint
from ..lang.predicate import Predicate, UndefinedPredicate
from ..lang.regularity import Regularity
import json


def consistency(lits: Object, rules: List[Regularity], md: BaseModel) -> float:
    """
    Мера объекта
    :param lits: Объект
    :param rules: Правила, относительно которых считается мера
    :param md: Параметры поиска / идеализации
    :return: Мера объекта, положительное число
    """
    measure = 0
    for rule in rules:
        if lits.rule_applicability(rule):
            if rule.conclusion in lits:
                measure += log_prob(rule, md)
            if ~ rule.conclusion in lits:
                measure -= log_prob(rule, md)
    return measure


def consistency_add(lits: Object, lit: Predicate, rules: List[Regularity], md: BaseModel) -> float:
    measure = 0
    for rule in rules:
        if (lit == rule.conclusion or ~ lit == rule.conclusion) and lits.rule_applicability(rule):
            if rule.conclusion in lits:
                measure += log_prob(rule, md)
            if ~ rule.conclusion in lits:
                measure -= log_prob(rule, md)
    return measure


def step_operator(lits: Object, rules: List[Regularity], model: BaseModel) -> Object:

    delta_add, lit_add = __delta_argmax_add_spec(lits, rules, model)
    delta_del, lit_del = __delta_argmax_del(lits, rules, model)
    print(delta_add, lit_add)
    print(delta_del, lit_del)
    print('---------^^^^^^^^^---------')

    if (consistency_lits := consistency(lits, rules, model)) < consistency(lits.add(lit_add), rules, model) and\
            delta_add > delta_del and delta_add > 0:

        return lits.add(lit_add)
    else:
        delta_add, lit_add = __delta_argmax_add(lits, rules, model)
        print('---------#########---------')
        print(delta_add, lit_add)
        print(delta_del, lit_del)
        print('---------#########---------')
        if consistency_lits < consistency(lits.add(lit_add), rules, model) and \
                delta_add > delta_del and delta_add > 0:
            return lits.add(lit_add)
        elif consistency_lits < consistency(lits.delete(lit_del), rules, model) and\
                delta_del > 0:

            return lits.delete(lit_del)

        else:
            return copy(lits)


def fp(lits: List[Object], rules: List[Regularity], model: BaseModel) -> List[Object]:
    fix_points = []

    for lit_now in lits:
        lit_now.completion(model.sample.pt)

        while True:
            lit_next = step_operator(lit_now, rules, model)
            if lit_now == lit_next:
                break
            lit_now = lit_next

        lit_now.decompletion()
        fix_points.append(lit_now)

    return fix_points


# Далее идут чисто технические функции

def __delta_argmax_add(lits: Object, rules: List[Regularity], model: BaseModel) \
        -> Tuple[float, Predicate]:
    # Функция ищет максимальное изменение критерия при добавлении предиката
    argmax = UndefinedPredicate()
    applicable_concls = set(r.conclusion for r in rules if lits.rule_applicability(r) and r.conclusion not in lits)
    consistency_lits, consistencymax_delta, consistencymax_arg, kr = .0, .0, .0, .0
    for lit in applicable_concls:
        consistency_lits = consistency(lits, rules, model)
        kr = consistency(lits.add(lit), rules, model) - consistency_lits
        if kr > consistencymax_delta:
            consistencymax_delta = kr
        if kr + consistency_lits > consistencymax_arg:
            consistencymax_arg = kr + consistency_lits
            argmax = lit
    return consistencymax_delta, argmax


def __delta_argmax_add_spec(lits: Object, rules: List[Regularity], model: BaseModel) \
        -> Tuple[float, Predicate]:
    # Функция ищет максимальное изменение критерия при добавлении предиката
    argmax = UndefinedPredicate()
    applicable_concls = set(r.conclusion for r in rules if lits.rule_applicability(r) and r.conclusion not in lits)
    consistency_lits, consistencymax_delta, consistencymax_arg, kr = .0, .0, .0, .0
    for lit in applicable_concls:
        consistency_lits = consistency_add(lits, lit, rules, model)
        kr = consistency_add(lits.add(lit), lit, rules, model) - consistency_lits
        if kr > consistencymax_delta:
            consistencymax_delta = kr
        if kr + consistency_lits > consistencymax_arg:
            consistencymax_arg = kr + consistency_lits
            argmax = lit
    return consistencymax_delta, argmax


def __delta_argmax_del(lits: Object, rules: List[Regularity], model: BaseModel) \
        -> Tuple[float, Predicate]:
    consistency_lits = consistency(lits, rules, model)
    argmax = UndefinedPredicate()
    consistencymax_delta, consistencymax_arg, kr = .0, .0, .0
    for lit in lits:
        kr = consistency(lits.delete(lit), rules, model) - consistency_lits
        if kr > consistencymax_delta:
            consistencymax_delta = kr
        if kr + consistency_lits > consistencymax_arg:
            consistencymax_arg = kr + consistency_lits
            argmax = lit
    return consistencymax_delta, argmax


def log_prob(r: Regularity, model: BaseModel) -> float:
    return -mlog(1 - r.eval_prob(model))

