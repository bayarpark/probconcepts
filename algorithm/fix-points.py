from algorithm.structure import *
from math import log as mlog
from copy import copy


def krit(lits: Object, rules: List[Rule], par: FindParams) -> float:
    """
    Мера объекта
    :param lits: Объект
    :param rules: Правила, относительно которых считается мера
    :param par: Параметры поиска / идеализации
    :return: Мера объекта, положительное число
    """
    sat = []
    fal = []
    for rule in rules:
        if lits.rule_applicability(rule):
            if rule.concl in lits:
                sat.append(rule)
            if ~ rule.concl in lits:
                fal.append(rule)
    return sum(map(lambda x: log_prob(x, par), sat)) - sum(map(lambda x: log_prob(x, par), fal))


def krit_add(lits: Object, lit: Literal, rules: List[Rule], par: FindParams) -> float:
    sat = []
    fal = []
    for rule in rules:
        if (lit == rule.concl or ~ lit == rule.concl) and lits.rule_applicability(rule):
            if rule.concl in lits:
                sat.append(rule)
            if ~ rule.concl in lits:
                fal.append(rule)
    return sum(map(lambda x: log_prob(x, par), sat)) - sum(map(lambda x: log_prob(x, par), fal))


def step_operator(lits: Object, rules: List[Rule], par: FindParams) -> Object:
    applicable_concls = copy(lits)
    for rule in rules:
        if lits.rule_applicability(rule):
            applicable_concls = applicable_concls.add(rule.concl)

    delta_add, lit_add = __delta_argmax_add(lits, applicable_concls, rules, par)
    delta_del, lit_del = __delta_argmax_del(lits, applicable_concls, rules, par)
    if krit(lits, rules, par) < krit(lits.add(lit_add), rules, par) and delta_add > delta_del and delta_add > 0:
        return lits.add(lit_add)
    elif krit(lits, rules, par) < krit(lits.delete(lit_del), rules, par) and delta_del >= delta_add and delta_del > 0:
        return lits.delete(lit_del)
    else:
        return copy(lits)


def step_operator_explicable(lits: FixPoint, rules: [Rule], par: FindParams, k: int) -> FixPoint:
    def get_k_maxprob_rules(lit):  # Очень тупо, переделать
        return sorted(
            [r for r in rules if r.concl == lit and lits.rule_applicability(r)],
            key=lambda l: l.evaluate_prob(), reverse=True
        )[:k]

    applicable_concls = get_applicable_conclusions(lits, rules)

    delta_add, lit_add = __delta_argmax_add(lits, applicable_concls, rules, par)
    delta_del, lit_del = __delta_argmax_del(lits, applicable_concls, rules, par)

    if krit(lits, rules, par) < krit(lits.add(lit_add), rules, par) and delta_add > delta_del and delta_add > 0:
        return lits.step_add(lit_add, get_k_maxprob_rules(lit_add))
    elif krit(lits, rules, par) < krit(lits.delete(lit_del), rules, par) and delta_del >= delta_add and delta_del > 0:
        return lits.step_del(lit_del, get_k_maxprob_rules(lit_del))
    else:
        return copy(lits)


def fp_explicit_with_k_rules(lits: [FixPoint], rules: [Rule], par: FindParams, k: int) -> Set[FixPoint]:
    if k <= 0:
        raise ValueError("`k` must be positive")
    else:
        fix_points = set()

        for lit_now in lits:
            lit_now = FixPoint(lit_now)
            lit_now.completion()

            while True:
                lit_next = step_operator_explicable(lit_now, rules, par, k)
                if lit_now == lit_next:
                    break
                lit_now = lit_next

            lit_now.decompletion()
            fix_points.update({lit_now})

        return fix_points


def fp(lits: List[Object], rules: List[Rule], par: FindParams) -> Set[Object]:
    fix_points = set()

    for lit_now in lits:
        lit_now.completion()

        while True:
            lit_next = step_operator(lit_now, rules, par)
            if lit_now == lit_next:
                break
            lit_now = lit_next

        lit_now.decompletion()
        fix_points.update({lit_now})

    return fix_points


# Далее идут чисто технические функции

def __delta_argmax_add(lits: Object, applicable_concls: List[Literal], rules: List[Rule], par: FindParams) \
        -> Tuple[float, Literal]:
    # Функция ищет максимальное изменение критерия при добавлении предиката
    argmax = UndefinedLiteral()
    krit_lits, kritmax_delta, kritmax_arg, kr = .0, .0, .0, .0
    for lit in applicable_concls:
        if lit not in lits:
            krit_lits = krit_add(lits, lit, rules, par)
            kr = krit_add(lits.add(lit), lit, rules, par) - krit_lits
        if kr > kritmax_delta:
            kritmax_delta = kr
        if kr + krit_lits > kritmax_arg:
            kritmax_arg = kr + krit_lits
            argmax = lit
    return kritmax_delta, argmax


def __delta_argmax_del(lits: Object, applicable_concls: List[Literal], rules: List[Rule], par: FindParams) \
        -> Tuple[float, Literal]:
    krit_lits = krit(lits, rules, par)
    argmax = UndefinedLiteral()
    kritmax_delta, kritmax_arg, kr = .0, .0, .0
    for lit in applicable_concls:
        if lit not in lits:
            kr = krit(lits.add(lit), rules, par) - krit_lits
        if kr > kritmax_delta:
            kritmax_delta = kr
        if kr + krit_lits > kritmax_arg:
            kritmax_arg = kr + krit_lits
            argmax = lit
    return kritmax_delta, argmax


def log_prob(r: Rule, par: FindParams) -> float:
    return -mlog(1 - r.evaluate(par)[0])


def get_applicable_conclusions(lits: Union[FixPoint, Object], rules: List[Rule]) -> List[Literal]:
    applicable_concls = copy(lits)
    for rule in rules:
        if lits.rule_applicability(rule):
            applicable_concls = applicable_concls.add(rule.concl)
    return applicable_concls
