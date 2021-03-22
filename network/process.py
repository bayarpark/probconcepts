from typing import List

from lang.predicate import Predicate
from network.extregularity import Conjunction
import pandas as pd


def conj_on_obj(obj: List, conj: Conjunction ):
    for pr in conj.predicates:
        if obj[pr.ident] is None:
            return None
        elif pr.operation.name == "Eq" and obj[pr.ident] != pr.operation.params:
            return False
        elif pr.operation.name == "Neq" and obj[pr.ident] == pr.operation.params:
            return False
    # TODO: add other operations
    return True


def convert_sample(sample, conjs):
    data = sample.data
    new_data = []
    for obj in data:
        new_obj = []
        for conj in conjs:
            new_obj.append(conj_on_obj(obj, conj))
        new_data.append(new_obj)

    new_df = pd.DataFrame.from_records(new_data)
    # TODO: rename columns
    return new_df


def find_all_extrules(dir, pt):
    all_rules = []
    for i in range(len(pt)):
        for j in range(len(pt[i])):
            for k in range(2):
                with open(str(pt.table[i][j][k])+".txt", 'r') as f:
                    for line in f:
                        all_rules.append(find_extrules(read_rule(line), i, j, k) )


def find_extrules(rule, i, j, k):



"""
def find_assoc_rules(pt):

    pass


def ass_rules_to_conj(ass_rules):
    return List[Conjunctions]

def conj_to_sample(conjunctions):
    # строит по конъюнкициям выборку
    pass
"""