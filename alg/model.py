from alg.data import *
from typing import *
from utils.fisher import fisher_exact

PValue = NewType('PValue', float)
Proba = NewType('Proba', float)


class BaseModel:
    def __init__(self,
                 sample: Sample = None,
                 base_depth: int = None,
                 fully_depth: int = None,
                 confidence_level: float = None,
                 measure: Union[Callable[[Regularity, 'BaseModel'], Tuple[Proba, PValue]], str] = 'std',
                 dirname: str = 'pcr') -> None:
        
        self.dirname = dirname
        self.sample = sample
        
        if fully_depth is None:
            self.fully_depth = 2**64
        else:
            if not (isinstance(fully_depth, int) and fully_depth >= 1):
                raise ValueError('fully_depth must be int and >= 1')
            else:
                self.fully_depth = fully_depth

        if base_depth is None:
            self.base_depth = 2
        else:
            if not (isinstance(base_depth, int) and 1 <= base_depth <= fully_depth):
                raise ValueError('base_depth must be int and 1 <= base_depth <= fully_depth')
            else:
                self.base_depth = base_depth

        if confidence_level is None:
            self.confidence_level = 0.05
        else:
            if not (isinstance(confidence_level, float) and 0 <= confidence_level <= 1):
                raise ValueError('confidence_level must be int and 0 <= confidence_level <= 1')
            else:
                self.confidence_level = confidence_level

        if measure == 'std':
            self.measure = std_measure
        elif type(measure).__name__ == 'functiom':
            self.measure = measure
        
    
def std_measure(rule: 'Regularity', model: BaseModel) -> Tuple[Proba, PValue]:
    top = 0
    bottom = 0
    cons_count = 0
    all_sum = 0
    for obj in model.sample.data:
        d, n = 1, 1
        val_is_unknown = False
        for lit in rule.premise:
            p = obj[lit.ident]
            if p is None:
                val_is_unknown = True
                break
            if not lit(p):
                d = 0
                break
        p = obj[rule.conclusion.ident]
        if val_is_unknown or p is None:
            d, n = 0, 0
        else:
            all_sum += 1
            if rule.conclusion(p):
                cons_count += 1

            if d == 0 or not rule.conclusion(p):
                n = 0
        top += n
        bottom += d

    absolute_prob = (cons_count + 1) / (model.sample.shape[0] + 2)  # absolute_prob д.б. < cond_prob
    cond_prob = (top + 1) / (bottom + 2) if top != 0 and bottom != 0 else 0.

    if absolute_prob >= cond_prob:  # Костыль -- если абсоютная в-ть >= условной, то возвращаем p_val = 1
        return cond_prob, 1.

    crosstab = [[top, bottom - top], [cons_count - top, all_sum - cons_count - bottom + top]]
    p_val = fisher_exact(crosstab)

    return cond_prob if top != 0. and bottom != 0. else 0., p_val
