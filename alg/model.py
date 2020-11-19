from dataclasses import dataclass
from math import inf
from typing import *
from alg.measures import *


@dataclass()
class Feature:
    name: str
    domain: type


@dataclass()
class Dataset:
    dataset: List[List[Union[float, int, bool]]]
    size: int
    features: Dict[int, Feature]


@dataclass
class GenParams:
    base_depth: float
    fully_depth: float
    confidence_level: float = 0.05
    dirname: str = "spl"


DEFAULT_GEN_PARAMS = GenParams(2, inf)


class Model:
    def __init__(self,
                 dataset: Dataset = None,
                 genpar: GenParams = DEFAULT_GEN_PARAMS,
                 measure: Callable[['Regularity', 'Model'], Tuple[float, float]] = None) -> None:
        self.dataset = dataset
        self.genpar = genpar
        if measure is None:
            self.measure = std_measure
        else:
            self.measure = measure

    def __iadd__(self, other: Union[Dataset, GenParams]) -> None:
        if isinstance(other, Dataset):
            self.dataset = other
        elif isinstance(other, GenParams):
            self.genpar = other
        else:
            raise TypeError("Unknown type, only 'Dataset' and 'GenParams' are allowed")


def std_measure(rule: 'Regularity', model: Model) -> Tuple[float, float]:
    top = 0
    bottom = 0
    cons_count = 0
    all_sum = 0
    for obj in model.dataset.dataset:
        d, n = 1, 1
        val_is_unknown = False
        for lit in rule.features:
            p = obj[lit.id()]
            if p == 0:
                val_is_unknown = True
                break
            if (not lit.val() and p == -1) or (lit.val() and p == 1):
                d = 0
                break
        p = obj[rule.concl.id()]
        if val_is_unknown or p == 0:
            d, n = 0, 0
        else:
            all_sum += 1
            if rule.concl.val() and p == 1 \
                    or not rule.concl.val() and p == -1:
                cons_count += 1

            if d == 0 or (not rule.concl.val() and p == -1) or \
                    (rule.concl.val() and p == 1):
                n = 0
        top += n
        bottom += d

    absolute_prob = (cons_count + 1) / (model.dataset.size + 2)  # absolute_prob д.б. < cond_prob
    cond_prob = (top + 1) / (bottom + 2) if top != 0 and bottom != 0 else 0.

    if absolute_prob >= cond_prob:  # Костыль -- если абсоютная в-ть >= условной, то возвращаем p_val = 1
        return cond_prob, 1.

    crosstab = [[top, bottom - top], [cons_count - top, all_sum - cons_count - bottom + top]]
    p_val = fisher_exact(crosstab)

    return cond_prob if top != 0. and bottom != 0. else 0., p_val
