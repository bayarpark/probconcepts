from .data import *
from typing import *
from ..utils.measure import std_measure

PValue = NewType('PValue', float)
Proba = NewType('Proba', float)


class BaseModel:
    def __init__(self,
                 sample: Sample = None,
                 base_depth: int = None,
                 fully_depth: int = None,
                 confidence_level: float = None,
                 measure: Union[Callable[[Regularity, 'BaseModel'], Tuple[Proba, PValue]], str] = 'std',
                 rules_write_path: str = 'pcr/') -> None:
        
        self.path = rules_write_path
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
        elif type(measure).__name__ == 'function':
            self.measure = measure
