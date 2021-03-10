from lang.opers import *


class Predicate:

    def __init__(self,
                 ident: Union[int, str],
                 vtype: Var,
                 operation: Oper = None,
                 opt: Union[Opers, str] = None,
                 params: Union[int, bool, float, Tuple[float, float], Tuple[int, int]] = None) -> None:
        self.ident = ident
        self.vtype = vtype

        if operation is not None:
            self.operation = operation
        elif opt is not None and params is not None:
            self.operation = Oper.make(opt, params)
        else:
            raise ValueError("`operation` or (`opt` and `params`) must be defined")

    def __call__(self, x: Union[int, bool, float]) -> bool:
        return self.operation(x)

    def __invert__(self) -> 'Predicate':
        return Predicate(self.ident, self.vtype, ~self.operation)  # TODO 

    def __str__(self) -> str:
        return f"<x{self.ident}{str(self.operation)}>"

    def __eq__(self, other: 'Predicate') -> bool:
        return self.ident == other.ident and self.operation == other.operation and self.vtype == other.vtype
        # Есть проблемы с сравнением бинарных равенств, т.е. если признак принимает только {A, B}
        # то в нашем случае Eq(A) := x == A НЕ РАВНО Neq(B) := x != B
        # (а по-хорошему должно было бы, т.к. это одно и то же)

    def __hash__(self) -> int:
        return hash((self.ident, self.vtype, self.operation))

    def __len__(self) -> int:
        return 1

    @property
    def name(self) -> Union[int, str]:
        return self.ident

    def is_positive(self) -> bool:
        if self.vtype == Var.Bool and isinstance(self.operation, Eq):
            return self.operation.params
        else:
            return self.operation.is_positive()

    def to_dict(self) -> Dict:
        return {
            "id": self.ident,
            "var": self.vtype.name,
            "op": self.operation.to_dict(),
        }

    @staticmethod
    def from_dict(d: Dict[str, Union[int, str, Dict]]) -> 'Predicate':
        return Predicate(
            ident=d['id'],
            vtype=Var[d['var']],
            operation=Oper.from_dict(d['op'])
        )


class UndefinedPredicate(Predicate):
    def __init__(self) -> None:
        super().__init__(0, vtype=Var.undefined, operation=UndefinedOperation())
