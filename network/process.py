from typing import List

from lang.predicate import Predicate
from lang.parser import decstr
from network.extregularity import Conjunction, ExtRegularity
import pandas as pd
import glob


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


def find_extrules(dir, model, ctype_dict):
    # getting all rules from directory
    all_rules = []
    for file in glob.glob(dir+"*.txt"):
        all_rules.extend(decstr(file, ctype_dict))

    # searching for rules with the same premise
    dict_rules = dict()
    for rule in all_rules:
        rule_hash = rule.hash_premise()
        if dict_rules.get(rule_hash) is None:
            dict_rules[rule_hash] = [rule]
        else:
            dict_rules[rule_hash].append(rule)

    extrules = []
    for key in dict_rules.keys():
        base_rule = dict_rules[key][0]
        concls = []
        for rule in dict_rules[key]:
            if rule.premise != base_rule.premise:
                print("Collision found, base rule is {}, collision rule is {}".format(str(rule), str(base_rule)))
            else:
                concls.append(rule.conclusion)

        extrule = ExtRegularity(conclusion=concls, premise=base_rule.premise)
        extrule.evaluate(model)
        # TODO checking for threshold
        extrules.append(extrule)

    return extrules


def dense_layer(dir, ):
    # reading


    extrules = find_extrules

    conjunctions = []
    for extrule in extrules:
        conjunctions.appen(extrule.to_conjunction())


"""
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


"""
def find_assoc_rules(pt):

    pass


def ass_rules_to_conj(ass_rules):
    return List[Conjunctions]

def conj_to_sample(conjunctions):
    # строит по конъюнкициям выборку
    pass
"""