from .data import *
from ..utils.measure import std_measure


class BaseModel:
    def __init__(self,
                 sample: Sample = None,
                 base_depth: int = 2,
                 fully_depth: int = 100,
                 confidence_level: float = 0.05,
                 confidence_predicate: float = 0.05,
                 negative_threshold: float = 0.,
                 measure: Union[Callable[[Regularity, 'BaseModel'], Tuple[float, float]], str] = 'std',
                 rules_write_path: str = 'pcr/') -> None:

        self.path = rules_write_path
        self.sample = sample

        if fully_depth < 1:
            raise ValueError('fully_depth must be int and >= 1')
        else:
            self.fully_depth = fully_depth

        if not (1 <= base_depth <= fully_depth):
            raise ValueError('base_depth must be int and 1 <= base_depth <= fully_depth')
        else:
            self.base_depth = base_depth

        if not (0 <= confidence_level <= 1) or not (0 <= confidence_predicate <= 1):
            raise ValueError('confidence_level must be float and in interval [0, 1]')
        else:
            self.confidence_predicate = confidence_predicate
            self.confidence_level = confidence_level

        if not (0 <= confidence_level <= 1):
            raise ValueError('negative_threshold must be float and in interval [0; 1] ')
        else:
            self.negative_threshold = negative_threshold

        if measure == 'std':
            self.measure = std_measure
        elif type(measure).__name__ == 'function':
            self.measure = measure
