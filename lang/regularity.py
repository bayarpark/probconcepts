from .predicate import *


class Regularity:
    __prob: float = None
    __pvalue: float = None

    def __init__(self, conclusion: Predicate, premise: List[Predicate] = None) -> None:
        if premise is None:
            premise = []
        self.__conclusion = conclusion
        self.__premise = premise

    def __eq__(self, other: 'Regularity') -> bool:
        # Вообще говоря, здесь могут быть проблемы, т.к. [a,b] != [b,a],
        # поэтому нужно следить, чтобы все предикаты шли в лексикографическом порядке
        return self.__conclusion == other.conclusion and self.__premise == other.premise

    def __hash__(self) -> int:
        # Аналогичная с __eq__ ситуация
        h = [p for p in self.__premise]
        h.append(self.__conclusion)
        return hash(tuple(h))

    def __len__(self) -> int:
        return len(self.__premise)

    def __str__(self) -> str:
        rule_str = ""
        for lit in self.__premise:
            rule_str += str(lit) + " & "
        rule_str = rule_str[:-2] + "=> " + str(self.__conclusion)
        rule_str += f" {self.__prob}, {self.__pvalue}"
        return rule_str

    def writefile(self, file) -> None:
        print(self, file=file)

    def is_nonnegative(self) -> bool:
        """
        Проверяет, что в посылке правила есть хотя бы один позитивный предикат
        """
        return any(map(Predicate.is_positive, self.__premise))

    def is_positive(self) -> bool:
        return all(map(Predicate.is_positive, self.__premise))

    def enhance(self, p: Predicate) -> 'Regularity':
        new_premise = self.__premise[:]
        new_premise.append(p)
        return Regularity(self.__conclusion, new_premise)

    def eval_prob(self, model) -> float:
        return self.evaluate(model)[0]

    def eval_pvalue(self, model) -> float:
        return self.evaluate(model)[1]

    def evaluate(self, model, force=False) -> Tuple[float, float]:
        if self.__prob is None or self.__pvalue is None or force:
            self.__prob, self.__pvalue = model.measure(self, model)
            return self.__prob, self.__pvalue
        else:
            return self.__prob, self.__pvalue

    def to_dict(self) -> Dict:
        return {
            'premise': [p.to_dict() for p in self.__premise],
            'conclusion': self.__conclusion.to_dict(),
            'prob': self.__prob,
            'pvalue': self.__pvalue
        }

    @staticmethod
    def from_dict(d: Dict) -> 'Regularity':
        r = Regularity(
            Predicate.from_dict(d['conclusion']),
            [Predicate.from_dict(p) for p in d['premise']])
        r.prob, r.pvalue = d['prob'], d['pvalue']
        return r

    @property
    def conclusion(self) -> Predicate:
        return self.__conclusion

    @property
    def premise(self) -> List[Predicate]:
        # тут тоже осторожно, возвращенный лист можно поменять
        return self.__premise

    @property
    def prob(self) -> float:
        return self.__prob

    @prob.setter
    def prob(self, value: float):
        if not (0 <= value <= 1):
            raise ValueError('Incorrect probability value')
        self.__prob = value

    @property
    def pvalue(self) -> float:
        return self.__pvalue

    @pvalue.setter
    def pvalue(self, value: float):
        if not (0 <= value <= 1):
            raise ValueError('Incorrect  p-value')
        self.__prob = value
