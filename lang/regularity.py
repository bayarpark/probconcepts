from lang.predicate import *
from alg.model import *


class Regularity:
    prob: float = None
    pvalue: float = None

    def __init__(self, conclusion: Predicate, features: List[Predicate] = None) -> None:
        if features is None:
            features = []
        self.conclusion = conclusion
        self.features = features

    def __eq__(self, other: 'Regularity') -> bool:
        # Вообще говоря, здесь могут быть проблемы, т.к. [a,b] != [b,a],
        # поэтому нужно следить, чтобы все предикаты шли в лексикографическом порядке
        return self.conclusion == other.conclusion and self.features == other.features

    def __hash__(self) -> int:
        # Аналогичная с __eq__ ситуация
        h = [p for p in self.features]
        h.append(self.conclusion)
        return hash(h)

    def __len__(self) -> int:
        return len(self.features)

    def __str__(self) -> str:
        rule_str = ""
        for lit in self.features:
            rule_str += str(lit) + " & "
        rule_str = rule_str[:-2] + "=> " + str(self.conclusion)
        rule_str += f" {self.prob}, {self.pvalue}"
        return rule_str

    def is_nonnegative(self) -> bool:
        """
        Проверяет, что в посылке правила есть хотя бы один позитивный предикат
        """
        return any(map(Predicate.is_positive, self.features))

    def enhance(self, p: Predicate) -> 'Regularity':
        return Regularity(self.conclusion, self.features[:].append(p))

    def eval_prob(self, model: Model) -> float:
        return self.evaluate(model)[0]

    def eval_pvalue(self, model: Model) -> float:
        return self.evaluate(model)[1]

    def evaluate(self, model: Model) -> Tuple[float, float]:
        if self.prob is None or self.pvalue is None:
            self.prob, self.pvalue = model.measure(self, model)
            return self.prob, self.pvalue
        else:
            return self.prob, self.pvalue

    def to_dict(self) \
            -> Dict[str,
                    Union[
                        List[Dict[str, Union[Oper, Var, int, bool, float, Iterable[float], Iterable[int]]]],
                        Dict[str, Union[Oper, Var, int, bool, float, Iterable[float], Iterable[int]]],
                        float]]:
        return {
            'features': [p.to_dict() for p in self.features],
            'conclusion': self.conclusion.to_dict(),
            'prob': self.prob,
            'pvalue': self.pvalue
        }

    @staticmethod
    def from_dict(d: Dict[str,
                          Union[
                            List[Dict[str, Union[Oper, Var, int, bool, float, Iterable[float], Iterable[int]]]],
                            Dict[str, Union[Oper, Var, int, bool, float, Iterable[float], Iterable[int]]],
                            float]]) -> 'Regularity':
        r = Regularity(
            Predicate.from_dict(d['conclusion']),
            [Predicate.from_dict(p) for p in d['features']])
        r.prob, r.pvalue = d['prob'], d['pvalue']
        return r
