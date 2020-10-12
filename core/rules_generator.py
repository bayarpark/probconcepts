from core.measures import *
from core.structure import *
from dataclasses import dataclass
from os import mkdir


@dataclass
class GenParams:
    base_depth: float
    fully_depth: float
    confidence_level: float = 0.05
    dirname: str = "spl"


def build_spl(find_interval: Tuple[int, int], find: FindParams, gen: GenParams) -> None:
    """
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

    # Генерация заключения
    for lit_ind in range(find_interval[0], find_interval[1] + 1):
        pass
        # TODO доделать

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
        pass
