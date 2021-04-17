from .opers import *


class Predicate:

    def __init__(self,
                 name: Union[int, str],
                 vtype: Var,
                 operation: Oper = None,
                 opt: Union[Opers, str] = None,
                 params: Union[int, bool, float, Any] = None) -> None:
        self.__name = name
        self.__vtype = vtype

        if operation is not None:
            self.__operation = operation
        elif opt is not None and params is not None:
            self.__operation = Oper.make(opt, params)
        else:
            raise ValueError("`operation` or (`opt` and `params`) must be defined")

    def __getitem__(self, x: Union[List, Iterable]) -> bool:
        """
        checks the satisfiability of a predicate on an object
        (list, tuple or other object representation)
        """
        return self.__operation(x[self.__name])

    def __call__(self, x: Union[int, bool, float]) -> bool:
        """
        checks the satisfiability of a predicate on value (int, bool or float)
        """
        return self.__operation(x)

    def __invert__(self) -> 'Predicate':
        return Predicate(self.__name, self.__vtype, ~self.__operation)  # TODO 

    def __str__(self) -> str:
        return f"<#{self.__name}{str(self.__operation)}>"

    def __eq__(self, other: 'Predicate') -> bool:
        return self.__name == other.name and self.__operation == other.operation and self.__vtype == other.vtype
        # Есть проблемы с сравнением бинарных равенств, т.е. если признак принимает только {A, B}
        # то в нашем случае Eq(A) := x == A НЕ РАВНО Neq(B) := x != B
        # (а по-хорошему должно было бы, т.к. это одно и то же)

    def __hash__(self) -> int:
        return hash((self.__name, self.__vtype, self.__operation))

    def __len__(self) -> int:
        return 1

    def is_positive(self) -> bool:
        if self.__vtype == Var.Bool and isinstance(self.__operation, Eq):
            return True
        else:
            return self.__operation.is_positive()

    def to_dict(self) -> Dict:
        return {
            "nm": self.__name,
            "var": self.__vtype.name,
            "op": self.__operation.to_dict(),
        }

    @staticmethod
    def from_dict(d: Dict) -> 'Predicate':
        return Predicate(
            name=d['nm'],
            vtype=Var[d['var']],
            operation=Oper.from_dict(d['op'])
        )

    @property
    def name(self) -> Union[int, str]:
        return self.__name

    @property
    def operation(self) -> Oper:
        return self.__operation

    @property
    def vtype(self) -> Var:
        return self.__vtype


class UndefinedPredicate(Predicate):
    def __init__(self) -> None:
        super().__init__('undefined', vtype=Var.undefined, operation=UndefinedOperation())
