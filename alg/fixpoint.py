from copy import copy
from math import log as mlog
from typing import *

from .model import BaseModel
from .structure import Object, FixPoint
from ..lang.predicate import Predicate, UndefinedPredicate
from ..lang.regularity import Regularity


def krit(lits: Object, rules: List[Regularity], model: BaseModel) -> float:
    """
    Мера объекта
    :param lits: Объект
    :param rules: Правила, относительно которых считается мера
    :param model: Параметры поиска / идеализации
    :return: Мера объекта, положительное число
    """
    sat = []
    fal = []
    for rule in rules:
        if lits.rule_applicability(rule):
            if rule.conclusion in lits:
                sat.append(rule)
            if ~ rule.conclusion in lits:
                fal.append(rule)
    return sum(map(lambda x: log_prob(x, model), sat)) - sum(map(lambda x: log_prob(x, model), fal))


def krit_add(lits: Object, lit: Predicate, rules: List[Regularity], model: BaseModel) -> float:
    sat = []
    fal = []
    for rule in rules:
        if (lit == rule.conclusion or ~ lit == rule.conclusion) and lits.rule_applicability(rule):
            if rule.conclusion in lits:
                sat.append(rule)
            if ~ rule.conclusion in lits:
                fal.append(rule)
    return sum(map(lambda x: log_prob(x, model), sat)) - sum(map(lambda x: log_prob(x, model), fal))


def step_operator(lits: Object, rules: List[Regularity], model: BaseModel) -> Object:
    applicable_concls = copy(lits)
    for rule in rules:
        if lits.rule_applicability(rule):
            applicable_concls = applicable_concls.add(rule.conclusion)

    delta_add, lit_add = __delta_argmax_add(lits, applicable_concls, rules, model)
    delta_del, lit_del = __delta_argmax_del(lits, applicable_concls, rules, model)
    print(lit_add)
    print(lit_del)
    if krit(lits, rules, model) < krit(lits.add(lit_add), rules, model) and delta_add > delta_del and delta_add > 0:
        return lits.add(lit_add)
    elif krit(lits, rules, model) < krit(lits.delete(lit_del), rules, model) and delta_del >= delta_add and delta_del > 0:
        return lits.delete(lit_del)
    else:
        return copy(lits)


def step_operator_explicable(lits: FixPoint, rules: List[Regularity], model: BaseModel, k: int) -> FixPoint:
    def get_k_maxprob_rules(lit):  # Очень тупо, переделать
        return sorted(
            [r for r in rules if r.conclusion == lit and lits.rule_applicability(r)],
            key=lambda l: l.evaluate_prob(), reverse=True
        )[:k]

    applicable_concls = get_applicable_conclusions(lits, rules)

    delta_add, lit_add = __delta_argmax_add(lits, applicable_concls, rules, model)
    delta_del, lit_del = __delta_argmax_del(lits, applicable_concls, rules, model)

    if krit(lits, rules, model) < krit(lits.add(lit_add), rules, model) and delta_add > delta_del and \
            delta_add > 0:
        return lits.step_add(lit_add, get_k_maxprob_rules(lit_add))
    elif krit(lits, rules, model) < krit(lits.delete(lit_del), rules, model) and delta_del >= delta_add and \
            delta_del > 0:
        return lits.step_del(lit_del, get_k_maxprob_rules(lit_del))
    else:
        return copy(lits)


def fp_explicit_with_k_rules(lits: [FixPoint], rules: List[Regularity], model: BaseModel, k: int) -> Set[FixPoint]:
    if k <= 0:
        raise ValueError("`k` must be positive")
    else:
        fix_points = set()

        for lit_now in lits:
            lit_now = FixPoint(lit_now)
            lit_now.completion(model.sample.pt)

            while True:
                lit_next = step_operator_explicable(lit_now, rules, model, k)
                if lit_now == lit_next:
                    break
                lit_now = lit_next

            lit_now.decompletion()
            fix_points.update({lit_now})

        return fix_points


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
        print(str(lit_now))
        fix_points.append(lit_now)

    return fix_points


# Далее идут чисто технические функции

def __delta_argmax_add(lits: Object, applicable_concls: List[Predicate], rules: List[Regularity], model: BaseModel) \
        -> Tuple[float, Predicate]:
    # Функция ищет максимальное изменение критерия при добавлении предиката
    argmax = UndefinedPredicate()
    krit_lits, kritmax_delta, kritmax_arg, kr = .0, .0, .0, .0
    for lit in applicable_concls:
        if lit not in lits:
            krit_lits = krit_add(lits, lit, rules, model)
            kr = krit_add(lits.add(lit), lit, rules, model) - krit_lits
        if kr > kritmax_delta:
            kritmax_delta = kr
        if kr + krit_lits > kritmax_arg:
            kritmax_arg = kr + krit_lits
            argmax = lit
    return kritmax_delta, argmax


def __delta_argmax_del(lits: Object, applicable_concls: List[Predicate], rules: List[Regularity], model: BaseModel) \
        -> Tuple[float, Predicate]:
    krit_lits = krit(lits, rules, model)
    argmax = UndefinedPredicate()
    kritmax_delta, kritmax_arg, kr = .0, .0, .0
    for lit in applicable_concls:
        if lit not in lits:
            kr = krit(lits.add(lit), rules, model) - krit_lits
        if kr > kritmax_delta:
            kritmax_delta = kr
        if kr + krit_lits > kritmax_arg:
            kritmax_arg = kr + krit_lits
            argmax = lit
    return kritmax_delta, argmax


def log_prob(r: Regularity, model: BaseModel) -> float:
    return -mlog(1 - r.evaluate(model)[0])


def get_applicable_conclusions(lits: Union[FixPoint, Object], rules: List[Regularity]) -> List[Predicate]:
    applicable_concls = copy(lits)
    for rule in rules:
        if lits.rule_applicability(rule):
            applicable_concls = applicable_concls.add(rule.conclusion)
    return applicable_concls
