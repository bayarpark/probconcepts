from typing import List, Tuple

from alg.structure import Object
from lang.predicate import Predicate


class Conjunction:
    def __init__(self, predicates: List[Predicate]):
        self.predicates = predicates

    def __str__(self):
        str_predicate = ""
        for pr in self.predicates:
            str_predicate += str(pr) + ' & '
        return str_predicate[:-3]

    def __hash__(self):
        return hash(tuple(self.predicates))

    def in_obj(self, obj: Object):
        for pr in self.predicates:
            if pr not in obj:
                return False
        return True


class ExtRegularity:
    prob: float = None
    pvalue: float = None

    def __init__(self, conclusion, premise=None):
        self.conclusion = conclusion
        if premise is None:
            self.premise = []
        else:
            self.premise = premise

    def __str__(self):
        rule_str = ""
        for lit in self.premise:
            rule_str += str(lit) + " & "
        rule_str = rule_str[:-2] + "=> "

        for lit in self.conclusion:
            rule_str += str(lit) + " & "

        rule_str = rule_str[:-2] + f" {self.prob}, {self.pvalue}"
        return rule_str

    def __hash__(self):
        h = [p for p in self.premise]
        for pr in self.conclusion:
            h.append(pr)
        return hash(tuple(h))

    def ext_premise(self, predicate):
        self.premise.append(predicate)

    def ext_conclusion(self, predicate):
        self.conclusion.append(predicate)

    def calc_prob(self, sample):
        pass

    def calc_pvalue(self, sample):
        pass

    def calc_probs(self, model):
        pass

    def evaluate(self, ext_model) -> Tuple[float, float]:
        if self.prob is None or self.pvalue is None:
            self.prob, self.pvalue = ext_model.measure(self, ext_model)
            return self.prob, self.pvalue
        else:
            return self.prob, self.pvalue

    def to_conjunction(self) -> Conjunction:
        h = [p for p in self.premise]
        for pr in self.conclusion:
            h.append(pr)
        return Conjunction(h)
