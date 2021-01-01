from typing import *

from lang.opers import *


class Predicate:
    def __init__(self,
                 ident: int,
                 vartype: Var,
                 operation: Oper = None,
                 opt: Union[Opers, str] = None,
                 params: Union[int, bool, float, Tuple[float, float], Tuple[int, int]] = None) -> None:
        self.ident = ident
        self.vartype = vartype

        if operation is not None:
            self.operation = operation
        elif opt is not None and params is not None:
            self.operation = Oper.make(opt, params)
        else:
            raise ValueError("`operation` or (`opt` and `params`) must be defined")

    def __call__(self, x: Union[int, bool, float]) -> bool:
        return self.operation(x)

    def __invert__(self) -> 'Predicate':
        return Predicate(self.ident, self.vartype, ~self.operation)  # TODO 

    def __str__(self) -> str:
        return f"<x{self.ident}{str(self.operation)}>"

    def __eq__(self, other: 'Predicate') -> bool:
        return self.ident == other.ident and self.operation == other.operation and self.vartype == other.vartype

    def __hash__(self) -> int:
        return hash(self.to_dict())

    def __len__(self) -> int:
        return 1

    def is_positive(self) -> bool:
        return self.operation.is_positive()

    def to_dict(self) -> Dict[str, Union[Oper, Var, int, bool, float, Tuple[float, float], Tuple[int, int]]]:
        return {
            "id": self.ident,
            "var": self.vartype.name,
            "op": self.operation.to_dict(),
        }

    @staticmethod
    def from_dict(d: Dict[str, Union[int, str, Dict]]) -> 'Predicate':
        return Predicate(
            ident=d['id'],
            vartype=Var[d['var']],
            operation=Oper.from_dict(d['op'])
        )


class UndefinedPredicate(Predicate):
    def __init__(self) -> None:
        super().__init__(0, vartype=Var.undefined, operation=UndefinedOperation())
