from lang.opers import *
from typing import *


class Predicate:
    def __init__(self,
                 opt: Oper,
                 vart: Var,
                 ident: int,
                 args: Union[int, bool, float, Tuple[float, float], Tuple[int, int]]) -> None:
        self.opt = opt
        self.vart = vart
        self.ident = ident
        self.arg = args
        self.__typecheck()
        self.__normalize()

    def __call__(self, x: Union[int, bool, float]) -> bool:
        if Oper.iseq(self.opt):
            return self.arg == x

        elif Oper.isneq(self.opt):
            return self.arg != x

        elif Oper.isle(self.opt):
            return x < self.arg

        elif Oper.isleq(self.opt):
            return x <= self.arg

        elif Oper.isge(self.opt):
            return x > self.arg

        elif Oper.isgeq(self.opt):
            return x >= self.arg

        elif Oper.isinterval(self.opt):
            return self.arg[0] <= x <= self.arg[1]

        elif Oper.istails(self.opt):
            return not (self.arg[0] <= x <= self.arg[1])

        else:
            raise NotImplementedError("Semantic for `opt` is not implemented")

    def __invert__(self) -> 'Predicate':
        inverted = Predicate(self.opt, self.vart, self.ident, self.arg)
        if Oper.iseq(inverted.opt):
            inverted.opt = Oper.neq
            inverted.__normalize()

        elif Oper.isneq(inverted.opt):
            inverted.opt = Oper.eq

        elif Oper.isle(inverted.opt):
            inverted.opt = Oper.geq

        elif Oper.isleq(inverted.opt):
            inverted.opt = Oper.ge

        elif Oper.isge(inverted.opt):
            inverted.opt = Oper.leq

        elif Oper.isgeq(inverted.opt):
            inverted.opt = Oper.le

        elif Oper.isinterval(inverted.opt):
            inverted.opt = Oper.tails

        elif Oper.istails(inverted.opt):
            inverted.opt = Oper.interval

        else:
            raise NotImplementedError("Semantic for `opt` is not implemented")

        return inverted

    def __str__(self) -> str:
        if Oper.is_binary(self.opt):
            return f"[x{self.ident} {self.opt.value} {self.arg}]"
        elif Oper.isinterval(self.opt):
            return f"[x{self.ident} in {self.arg[0]}, {self.arg[1]}]"
        elif Oper.istails(self.opt):
            return f"[x{self.ident} nin {self.arg[0]}, {self.arg[1]}]"
        else:
            raise NotImplementedError("Semantic for `opt` is not implemented")

    def __eq__(self, other: 'Predicate') -> bool:
        return self.vart == other.vart and self.opt == other.opt and \
            self.ident == other.ident and self.arg == other.arg

    def __hash__(self) -> int:
        return hash((self.opt, self.vart, self.ident, self.arg))

    def __len__(self) -> int:
        return 1

    def is_positive(self) -> bool:
        if Oper.isneq(self.opt) or (Var.isbin(self.vart) and not self.arg) or \
                Oper.istails(self.opt):
            return False
        else:
            return True

    def __normalize(self) -> None:
        if Oper.isneq(self.opt) and Var.isbin(self.vart):
            self.opt = Oper.eq
            self.arg = not self.arg

    def __typecheck(self) -> None:
        if Oper.is_binary(self.opt):
            if ((Var.isnom(self.vart)) or Var.isbin(self.vart)) and (self.opt != Oper.eq or self.opt != Oper.neq):
                raise TypeError("For 'Var.Nom' and 'Var.Bin' only 'Oper.eq' and 'Oper.neq' is allowed")

            elif (Var.isint(self.vart) or Var.isnom(self.vart)) and isinstance(self.arg, int) or \
                    (Var.isreal(self.vart)) and isinstance(self.arg, float) or \
                    Var.isbin(self.vart) and isinstance(self.arg, bool):
                pass
            elif self.vart == Var.undefined:
                pass
            else:
                raise ValueError("var and args must be some type")

        elif Oper.isinterval(self.opt) or Oper.istails(self.opt):
            if Var.isint(self.vart) and isinstance(self.arg, (int, int)) or \
                    Var.isreal(self.vart) and isinstance(self.arg, (float, float)):
                pass
            else:
                raise ValueError("var and args must be some type")
        else:
            raise TypeError("Unknown semantic for operation")


class UndefinedPredicate(Predicate):
    def __init__(self):
        super().__init__(Oper.eq, Var.undefined, -1, -1)
