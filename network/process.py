from typing import List

from ..lang.predicate import Predicate
from ..lang.parser import decstr
from .extregularity import Conjunction, ExtRegularity
import pandas as pd
import glob


def conj_on_obj(obj: List, conj: Conjunction):
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
    print("Total rules:", len(all_rules))

    # searching for rules with the same premise
    dict_rules = dict()
    for rule in all_rules:
        rule_hash = rule.hash_premise()
        if dict_rules.get(rule_hash) is None:
            dict_rules[rule_hash] = [rule]
        else:
            dict_rules[rule_hash].append(rule)
    print("Total unique premises:", len(dict_rules))

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
        # extrule.evaluate(model)
        # TODO checking for threshold
        extrules.append(extrule)
    print("Total extrules:", len(extrules))
    return extrules
