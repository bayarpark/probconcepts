from lang.predicate import *


class Regularity:
    prob: float = None
    pvalue: float = None

    def __init__(self, conclusion: Predicate, premise: List[Predicate] = None) -> None:
        if premise is None:
            premise = []
        self.conclusion = conclusion
        self.premise = premise

    def __eq__(self, other: 'Regularity') -> bool:
        # Вообще говоря, здесь могут быть проблемы, т.к. [a,b] != [b,a],
        # поэтому нужно следить, чтобы все предикаты шли в лексикографическом порядке
        return self.conclusion == other.conclusion and self.premise == other.premise

    def __hash__(self) -> int:
        # Аналогичная с __eq__ ситуация
        h = [p for p in self.premise]
        h.append(self.conclusion)
        return hash(tuple(h))

    def __len__(self) -> int:
        return len(self.premise)

    def __str__(self) -> str:
        rule_str = ""
        for lit in self.premise:
            rule_str += str(lit) + " & "
        rule_str = rule_str[:-2] + "=> " + str(self.conclusion)
        rule_str += f" {self.prob}, {self.pvalue}"
        return rule_str

    def writefile(self, file) -> None:
        print(f'{str(self)} {self.prob} {self.pvalue}', file=file)

    def is_nonnegative(self) -> bool:
        """
        Проверяет, что в посылке правила есть хотя бы один позитивный предикат
        """
        return any(map(Predicate.is_positive, self.premise))

    def enhance(self, p: Predicate) -> 'Regularity':
        new_premise = self.premise[:]
        new_premise.append(p)
        return Regularity(self.conclusion, new_premise)

    def eval_prob(self, model) -> float:
        return self.evaluate(model)[0]

    def eval_pvalue(self, model) -> float:
        return self.evaluate(model)[1]

    def evaluate(self, model) -> Tuple[float, float]:
        if self.prob is None or self.pvalue is None:
            self.prob, self.pvalue = model.measure(self, model)
            return self.prob, self.pvalue
        else:
            return self.prob, self.pvalue

    def to_dict(self) -> Dict:
        return {
            'premise': [p.to_dict() for p in self.premise],
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
            [Predicate.from_dict(p) for p in d['premise']])
        r.prob, r.pvalue = d['prob'], d['pvalue']
        return r
