from os import mkdir
from lang.regularity import Regularity
from alg.model import *

# Правила строятся следующим образом (используется обход графа "в глубину"):
# Последовательно фиксируются заключения, далее, для каждого заключения
# запускается функция build_premise, которая


def build_spcr(conclusions: List[Predicate], model: BaseModel) -> None:
    """

    :param conclusions: Предикаты в заключении
    :param model: Модель, на которой оцениваются правила
    :return: None
    """

    try:
        mkdir(model.dirname)
    except FileExistsError:
        mkdir(f'{model.dirname}_1')  # BUG TODO

    def check_subrules_prob(rule: Regularity) -> bool:
        """
        Checks the probabilities of the subrules
        """
        # for lit_del in rule.premise:
        #     subrule = Regularity(rule.conclusion, [lit for lit in rule.premise if lit != lit_del])
        #     if subrule.eval_prob(model) >= rule.eval_prob(model) and \
        #             subrule.eval_pvalue(model) <= rule.eval_pvalue(model):
        #         return False
        return True

    def check_fisher(rule: Regularity) -> bool:
        """
        Checks p-values of the subrules
        """



        # TODO
        return True

    # Генерация заключения
    def build_conclusion() -> None:
        for lit in conclusions:
            poss_lits = model.sample.pt.init(lit)
            with open(f"{model.dirname}/spcr_{str(lit)}.txt", "w") as f:
                build_premise(Regularity(lit), poss_lits, 0, f)

            with open(f"{model.dirname}/spcr_{str(~lit)}.txt", "w") as f:
                build_premise(Regularity(~lit), poss_lits, 0, f)

    # Наращивание посылки
    def build_premise(rule: Regularity, possible_lits: PredicateTable, depth: int, file) -> bool:
        if depth < model.fully_depth:
            enhance = False
            for lit in possible_lits:
                new_rule = rule.enhance(lit)
                print(new_rule, new_rule.eval_prob(model))
                if new_rule.is_nonnegative() and rule.eval_prob(model) < new_rule.eval_prob(model) and \
                        new_rule.eval_pvalue(model) < model.confidence_level and check_subrules_prob(new_rule) and \
                        rule.eval_pvalue(model) > new_rule.eval_pvalue(model) and check_fisher(new_rule):
                    print(new_rule)
                    if depth == model.fully_depth - 1:
                        new_rule.writefile(file)
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
                            check_subrules_prob(rule) and check_fisher(rule):
                        rule.writefile(file)
                        return True
                    else:
                        return False
                else:
                    rule.writefile(file)
                    return True
            else:
                return True
        else:
            return False

    build_conclusion()
