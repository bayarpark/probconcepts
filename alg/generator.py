from .model import *
from ..lang.parser import cstr
from ..utils.fisher import fisher_exact
from ..utils.sys import makedir


# Правила строятся следующим образом (используется обход графа "в глубину"):
# Последовательно фиксируются заключения, далее, для каждого заключения
# запускается функция build_premise, которая


def build_spcr(conclusions: List[Predicate], model: BaseModel) -> None:
    """

    :param conclusions: List of conclusions
    :param model: model
    :return: None
    """

    path = makedir(model.path)

    # Генерация заключения
    def build_conclusion() -> None:
        for lit in conclusions:
            poss_lits = model.sample.pt.init(lit)
            with open(f"{path}spcr_{str(lit)}.txt", "w") as f:
                build_premise(Regularity(lit), poss_lits, 0, f)

    # Наращивание посылки
    def build_premise(rule: Regularity, possible_lits: PredicateTable, depth: int, file) -> bool:
        if depth < model.fully_depth:
            enhance = False
            for lit in possible_lits:
                new_rule = rule.enhance(lit)
                if new_rule.is_nonnegative() and rule.eval_prob(model) < new_rule.eval_prob(model) and \
                        check_threshold(new_rule, rule, lit, model) and \
                        new_rule.eval_pvalue(model) < model.confidence_level and check_proba(new_rule, model) and \
                        rule.eval_pvalue(model) > new_rule.eval_pvalue(model) and check_fisher(new_rule, model):
                    if depth == model.fully_depth - 1:
                        print(cstr(new_rule), file=file)
                        enhance = True
                    else:
                        enhance = build_premise(new_rule, possible_lits.drop(lit), depth + 1, file) or enhance

                elif depth < model.base_depth:
                    enhance = build_premise(new_rule, possible_lits.drop(lit), depth + 1, file) or enhance

            if not enhance:
                if depth == 0:
                    return True
                elif depth <= model.base_depth:
                    if rule.eval_pvalue(model) < model.confidence_level and \
                            check_proba(rule, model) and check_fisher(rule, model):
                        print(cstr(rule), file=file)
                        return True
                    else:
                        return False
                else:
                    print(cstr(rule), file=file)
                    return True
            else:
                return True
        else:
            return False

    build_conclusion()


def check_threshold(new_rule: Regularity, rule: Regularity, lit: Predicate, model: BaseModel) -> bool:
    if lit.is_positive():
        return True
    else:
        return new_rule.eval_prob(model) - rule.eval_prob(model) >= model.negative_threshold


def check_proba(rule: Regularity, model: BaseModel) -> bool:
    """
    Checks the probabilities of the subrules

    :param rule:
    :param model:
    :return:
    """
    for lit_del in rule.premise:
        subrule = Regularity(rule.conclusion, [lit for lit in rule.premise if lit != lit_del])
        if subrule.eval_prob(model) >= rule.eval_prob(model) and \
                subrule.eval_pvalue(model) <= rule.eval_pvalue(model):
            return False
    return True


def check_fisher(rule: Regularity, model: BaseModel) -> bool:
    """
    Checks p-values of the subrules

    :params rule: Regularity for check
    :params model: BaseModel object
    :return:
    """
    is_true = lambda obj, subpremise: all(pr[obj] for pr in subpremise)

    for lit in rule.premise:
        subpremise = [p for p in rule.premise if p != lit]

        top = 0
        bottom = 0
        cons_count = 0
        all_sum = 0
        for obj in model.sample.data:
            if is_true(obj, subpremise):
                all_sum += 1
                if rule.conclusion[obj]:
                    cons_count += 1
                    if lit[obj]:
                        top += 1
                if lit[obj]:
                    bottom += 1

        crosstab = [[top, bottom - top], [cons_count - top, all_sum - cons_count - bottom + top]]
        if p_value := fisher_exact(crosstab) >= model.confidence_level:
            return False
    return True
