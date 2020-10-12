from core.measures import *
from core.structure import *
from os import mkdir


class GenParams:
    def __init__(self, confidence_level: float, dirname: str, fully_depth: int, base_depth: int = 0):
        self.dirname = dirname
        self.base_depth = int(1/10 * fully_depth) if base_depth == 0 else base_depth  # TODO проверить гипотезу
        self.fully_depth = fully_depth
        self.confidence_level = confidence_level


def build_spl(find_interval: (int, int), find: FindParams, gen: GenParams) -> None:
    """
    :param find_interval:
    Отрезок [a, b] ⊆ [0, `find.features_num`].
    Правила будут строиться для заключений, номера которых принимают значения из данного отрезка.
    :param find:
    Основные параметры обучающей выборки
    :param gen:
    Основные параметры генерации
    :return:
    None. Печатает закономерности в соответствующий файл в директории /`gen.dirname`
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




