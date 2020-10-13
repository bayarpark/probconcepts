from algorithm.measures import *
from algorithm.structure import *
from dataclasses import dataclass
from os import mkdir


@dataclass
class GenParams:
    base_depth: float
    fully_depth: float
    confidence_level: float = 0.05
    dirname: str = "spl"


# Правила строятся следующим образом (используется обход графа "в глубину):
# Последовательно фиксируются заключения, далее, для каждого заключения
# запускается функция build_premise, которая


def build_spl(find_interval: Tuple[int, int], find: FindParams, gen: GenParams) -> None:
    """
    Строит правила.
    :param find_interval:
    Отрезок [a, b] ⊆ [0, `find.features_num`].
    Правила будут строиться для заключений, номера которых принимают значения из данного отрезка.
    :param find: Основные параметры обучающей выборки
    :param gen: Основные параметры генерации
    :return: None. Печатает закономерности в соответствующий файл в директории /`gen.dirname`
    """
    if not (
            0 <= find_interval[0] < find.features_number
            and
            0 < find_interval[1] <= find.features_number
    ):
        raise IndexError("`find_interval` = [a, b] should be a subseteq of [0, `features_number`]")

    try:
        mkdir(gen.dirname)
    except FileExistsError:
        pass

    def check_subrules_prob(rule: Rule) -> bool:
        # Проверяет вероятности подправил на единицу меньше
        # Вообще говоря, нужно проверять ВСЕ подправила
        for lit_del in rule.features:
            subrule = Rule(rule.concl, [lit for lit in rule.features if lit != lit_del])
            if subrule.prob(find) >= rule.prob(find) and \
                    subrule.p_value(find) <= rule.p_value(find):
                return False
        return True

    def check_fisher(rule: Rule) -> bool:
        # TODO
        pass

    # Генерация заключения
    def build_conclusion() -> None:
        for lid in range(find_interval[0], find_interval[1] + 1):
            possible = [[True, True] for _ in range(find.features_number)]
            possible[lid][0] = False
            possible[lid][1] = False
            with open(f"{gen.dirname}/spl_{lid}.txt", "w") as f:
                build_premise(Rule(Literal(lid, True)), [a[:] for a in possible], 0, f)

            with open(f"{gen.dirname}/spl_~{lid}.txt", "w") as f:
                build_premise(Rule(Literal(lid, False)), [a[:] for a in possible], 0, f)

    # Наращиваение посылки
    def build_premise(rule: Rule, possible_lits: List[List[bool]], depth: int, file) -> bool:
        if depth < gen.fully_depth:
            enhance = False
            for lid in range(find.features_number):
                for tf in range(2):

                    if not possible_lits:
                        continue

                    possible_lits[lid][tf] = False
                    # TODO оптимизировать

                    new_rule = rule.enhance(Literal(lid, bool(tf)))

                    if new_rule.is_nonnegative() and rule.prob(find) < new_rule.prob(find) and \
                            new_rule.p_value(find) < gen.confidence_level and check_subrules_prob(new_rule) and \
                            rule.p_value(find) > new_rule.p_value(find) and check_fisher(new_rule):

                        if depth == gen.fully_depth - 1:
                            new_rule.writefile(file)
                            enhance = True
                        else:
                            enhance = build_premise(new_rule, [a[:] for a in possible_lits], depth + 1, file) or enhance

                    elif depth < gen.base_depth:
                        enhance = build_premise(new_rule, [a[:] for a in possible_lits], depth + 1, file) or enhance

            if not enhance:
                if depth == 0:
                    return True
                elif depth <= gen.base_depth:
                    if rule.p_value(find) < gen.confidence_level and \
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
