from typing import List

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


"""
class ExtendRegularity:

    def __init__(self, Rules1, Rules2):
        self.premise = List[Rules1]
        self.conclusion = List[Rules2]
        self.prob = None
        self.pvalue = None

    def __str__(self):
        pass

    def __hash__(self):
        pass


    def ext_premise(self, predicate):
        pass

    def ext_conclusion(self, predicate):
        pass

    def calc_prob(self, sample):
        pass

    def calc_pvalue(self, sample):
        pass

    def to_conjunction(self) -> Conjunction:
        pass
"""
