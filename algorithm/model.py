from dataclasses import dataclass
from math import inf
from typing import *


@dataclass()
class Feature:
    name: str
    domain: type


@dataclass()
class Dataset:
    dataset: List[List[Union[float, int, bool]]]
    dataset_size: int
    features: Dict[int, Feature]


@dataclass
class GenParams:
    base_depth: float
    fully_depth: float
    confidence_level: float = 0.05
    dirname: str = "spl"


DEFAULT_GEN_PARAMS = GenParams(2, inf)


class Model:
    def __init__(self, dataset: Dataset = None, genpar: GenParams = DEFAULT_GEN_PARAMS) -> None:
        self.dataset = dataset
        self.genpar = genpar

    def __iadd__(self, other: Union[Dataset, GenParams]) -> None:
        if isinstance(other, Dataset):
            self.dataset = other
        elif isinstance(other, GenParams):
            self.genpar = other
        else:
            raise TypeError("Unknown type, only 'Dataset' and 'GenParams' are allowed")




