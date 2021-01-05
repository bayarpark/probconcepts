from abc import ABC, abstractmethod
from enum import Enum, auto
from math import isclose
from typing import *


class Var(Enum):
    # При добавлении новых типов переменных их семантику необходимо прописать в Predicate
    # и добавить необходимые операции в Oper
    Bool = 'B'  # {T, F}
    Nom = 'N'  # {named}
    Int = 'I'  # Int
    Float = 'F'  # float
    undefined = auto()  # special undefined type

    @staticmethod
    def isbin(vart: 'Var') -> bool:
        return vart == Var.Bool

    @staticmethod
    def isnom(vart: 'Var') -> bool:
        return vart == Var.Nom

    @staticmethod
    def isint(vart: 'Var') -> bool:
        return vart == Var.Int

    @staticmethod
    def isreal(vart: 'Var') -> bool:
        return vart == Var.Float


ORDERED_VAR = [Var.Int, Var.Float]
ALLOWED_PYTHON_TYPES = Union[bool, int, float]


class Opers(Enum):
    """
    При добавлении новых операций нужно (как минимум):
    а) добавить их сюда
    б) создать подкласс от класса Oper с тем же именем, что и тут
    в) Прописать создание в make_operation
    """

    Eq = '='  # x == c
    Neq = '!='  # x != c
    Le = '<'  # x < c
    Leq = '<='  # x <= c
    Ge = '>'  # x > c
    Geq = '>='  # x >= c
    In = 'in'  # x in [a, b]
    Nin = 'nin'  # x not in [a, b]


class Oper(ABC):
    params: Union[int, bool, float, Tuple[Union[int, bool, float]], List[Union[int, bool, float]]]

    @abstractmethod
    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> ALLOWED_PYTHON_TYPES:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    def __eq__(self, other: 'Oper') -> bool:
        return type(self) == type(other) and self.params == other.params

    @abstractmethod
    def __invert__(self) -> 'Oper':
        pass

    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def is_binary(self) -> bool:
        pass

    @abstractmethod
    def is_positive(self) -> bool:
        pass

    def to_dict(self):
        return {
            "n": type(self).__name__,
            "params": self.params
        }

    @staticmethod
    def from_dict(d: Dict[str, Union[str, List[ALLOWED_PYTHON_TYPES]]]) -> 'Oper':
        return (globals()[d['n']])(d['params'])

    @staticmethod
    def make(opt: Union[Opers, str],
             params: Union[int, bool, float, Tuple[float, float], Tuple[int, int]]
             ) -> 'Oper':

        try:
            if type(opt) is str:

                # Special block for `
                if type(params) is bool and opt == '!=':
                    return Eq(not params)

                return (globals()[Opers(opt).name])(params)
            elif type(opt) is Opers:
                return (globals()[opt.name])(params)
            else:
                raise TypeError('`opt` must have type Opers or str')
        except ValueError:
            raise NotImplementedError(f'Semantic for operation "{opt}" is not implemented')


class OperBinary(Oper, ABC):
    params: ALLOWED_PYTHON_TYPES

    def arity(self) -> int:
        return 2

    def is_binary(self) -> bool:
        return True


class Eq(OperBinary):

    def __init__(self, params: ALLOWED_PYTHON_TYPES) -> None:
        self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        if type(self.params) is float:
            return isclose(x, self.params)
        else:
            return x == self.params

    def __invert__(self) -> OperBinary:
        if type(self.params) is bool:
            return Eq(not self.params)
        else:
            return Neq(self.params)

    def __str__(self) -> str:
        return f' = {self.params}'

    def is_positive(self) -> bool:
        return True


class Neq(OperBinary):

    def __init__(self, params: ALLOWED_PYTHON_TYPES) -> None:
        self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        if type(self.params) is float:
            return not isclose(x, self.params)
        else:
            return x != self.params

    def __invert__(self) -> OperBinary:
        return Eq(self.params)

    def __str__(self) -> str:
        return f' != {self.params}'

    def is_positive(self) -> bool:
        return False


class Le(OperBinary):
    def __init__(self, params: ALLOWED_PYTHON_TYPES) -> None:
        self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        return x < self.params

    def __invert__(self) -> OperBinary:
        return Geq(self.params)

    def __str__(self) -> str:
        return f' < {self.params}'

    def is_positive(self) -> bool:
        return True


class Leq(OperBinary):
    def __init__(self, params: ALLOWED_PYTHON_TYPES) -> None:
        self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        return x <= self.params

    def __invert__(self) -> OperBinary:
        return Ge(self.params)

    def __str__(self) -> str:
        return f' <= {self.params}'

    def is_positive(self) -> bool:
        return True


class Ge(OperBinary):
    def __init__(self, params: ALLOWED_PYTHON_TYPES) -> None:
        self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        return x > self.params

    def __invert__(self) -> OperBinary:
        return Leq(self.params)

    def __str__(self) -> str:
        return f' > {self.params}'

    def is_positive(self) -> bool:
        return True


class Geq(OperBinary):
    def __init__(self, params: ALLOWED_PYTHON_TYPES) -> None:
        self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        return x > self.params

    def __invert__(self) -> OperBinary:
        return Le(self.params)

    def __str__(self) -> str:
        return f' >= {self.params}'

    def is_positive(self) -> bool:
        return True


class In(Oper):

    def __init__(self, params: List[ALLOWED_PYTHON_TYPES]) -> None:
        if len(params) != 2:
            raise ValueError  # TODO дописать
        else:
            self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        return self.params[0] <= x <= self.params[1]

    def __str__(self) -> str:
        return f' in [{self.params[0]}, {self.params[1]}]'

    def __invert__(self) -> 'Oper':
        return Nin(self.params)

    def arity(self) -> int:
        return 3

    def is_binary(self) -> bool:
        return False

    def is_positive(self) -> bool:
        return True


class Nin(Oper):

    def __init__(self, params: List[ALLOWED_PYTHON_TYPES]) -> None:
        if len(params) != 2:
            raise ValueError  # TODO написать
        else:
            self.params = params

    def __call__(self, x: ALLOWED_PYTHON_TYPES) -> bool:
        return self.params[0] <= x <= self.params[1]

    def __str__(self) -> str:
        return f' nin [{self.params[0]}, {self.params[1]}]'

    def __invert__(self) -> 'Oper':
        return In(self.params)

    def arity(self) -> int:
        return 3

    def is_binary(self) -> bool:
        return False

    def is_positive(self) -> bool:
        return False


class UndefinedOperation(Oper):
    def __call__(self, x: Any) -> bool:
        return False

    def __str__(self) -> str:
        return 'undefined'

    def __invert__(self) -> 'Oper':
        return self

    def arity(self) -> int:
        return 0

    def is_binary(self) -> bool:
        return False

    def is_positive(self) -> bool:
        return False
