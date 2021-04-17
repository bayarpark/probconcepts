from copy import copy
from math import log as mlog
from typing import *
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .model import BaseModel
from .structure import Object, FixPoint
from ..lang.predicate import Predicate, UndefinedPredicate
from ..lang.regularity import Regularity


def consistency(lits: Object, rules: List[Regularity], md: BaseModel) -> float:
    """
    Мера объекта
    :param lits: Объект
    :param rules: Правила, относительно которых считается мера
    :param md: Параметры поиска / идеализации
    :return: Мера объекта, положительное число
    """
    measure = 0
    for rule in rules:
        if lits.rule_applicability(rule):
            if rule.conclusion in lits:
                measure += log_prob(rule, md)
            if ~ rule.conclusion in lits:
                measure -= log_prob(rule, md)
    return measure


def consistency_add(lits: Object, lit: Predicate, rules: List[Regularity], md: BaseModel) -> float:
    measure = 0
    for rule in rules:
        if (lit == rule.conclusion or ~ lit == rule.conclusion) and lits.rule_applicability(rule):
            if rule.conclusion in lits:
                measure += log_prob(rule, md)
            if ~ rule.conclusion in lits:
                measure -= log_prob(rule, md)
    return measure


def step_operator(lits: Object,
                  rules: List[Regularity],
                  model: BaseModel,
                  alternative_choose: bool,
                  logging: bool) -> Object:

    spec_delta_add, spec_lit_add = __delta_argmax_add_spec(lits, rules, model)
    delta_del, lit_del = __delta_argmax_del(lits, rules, model)

    consistency_lits = consistency(lits, rules, model)
    if spec_delta_add > 0 and spec_delta_add > delta_del and \
            consistency_lits < consistency(lits.add(spec_lit_add), rules, model):

        if logging:
            print(' # ---- STEP COMPLETED ---- # ')
            print(f'ADDED SPEC: {spec_lit_add} with DELTA: {spec_delta_add}')
            print(f'ALTERNATIVE: {lit_del} with DELTA: {delta_del}')

        return lits.add(spec_lit_add)
    else:
        if alternative_choose:
            delta_add, lit_add = __delta_argmax_add(lits, rules, model)
        if alternative_choose and \
                delta_add > 0 and delta_add > delta_del and \
                consistency_lits < consistency(lits.add(lit_add), rules, model):

            if logging:
                print(' # ---- STEP COMPLETED ---- # ')
                print(f'ADDED ALT: {lit_add} with DELTA: {delta_add}')
                print(f'ALTERNATIVE: {lit_del} wit DELTA: {delta_del}')

            return lits.add(lit_add)
        elif delta_del > 0 and lit_del in lits and consistency_lits < consistency(lits.delete(lit_del), rules, model):

            if logging:
                print(' # ---- STEP COMPLETED ---- # ')
                print(f'DELETED: {lit_del} with DELTA: {delta_del}')
                print(f'ALTERNATIVE SPEC: {spec_lit_add} with DELTA: {spec_delta_add}')

                if alternative_choose:
                    print(f'ALTERNATIVE ALT: {lit_add} with DELTA: {delta_add}')

            return lits.delete(lit_del)

        else:
            if logging:
                print(' # ---- STEP COMPLETED ---- # ')
                print('NO LITERALS ADDED OR DELETED')
            return copy(lits)


def fix_points(lits: List[Object],
               rules: List[Regularity],
               model: BaseModel,
               write_path: str = None,
               alternative_choose: bool = False,
               logging: bool = False) -> Union[None, List[Object]]:
    if write_path is None:
        return __find_fix_points_and_return(lits, rules, model, alternative_choose, logging)
    else:
        __find_fix_points_on_air(lits, rules, model, write_path, alternative_choose)


def __find_fix_points_and_return(lits: List[Object],
                                 rules: List[Regularity],
                                 model: BaseModel,
                                 alternative_choose: bool = False,
                                 logging: bool = False) -> List[Object]:
    fix_points = []

    for lit_now in lits:
        lit_now.completion(model.sample.pt)

        if logging:
            print('# ==== STARTING IDEALIZING A NEW OBJECT ==== #')

        while True:
            lit_next = step_operator(lit_now, rules, model, alternative_choose, logging)
            if lit_now == lit_next:
                break
            lit_now = lit_next

        fix_points.append(lit_now)

    return fix_points


def __find_fix_points_on_air(lits: List[Object],
                             rules: List[Regularity],
                             model: BaseModel,
                             write_path: str = None,
                             alternative_choose: bool = False) -> None:
    with open(write_path, 'w') as f:
        for lit_now in lits:
            lit_now.completion(model.sample.pt)

            while True:
                lit_next = step_operator(lit_now, rules, model, alternative_choose, False)
                if lit_now == lit_next:
                    break
                lit_now = lit_next

            print(yaml.dump([lit_now.to_dict()], Dumper=Dumper), file=f)


def __delta_argmax_add(lits: Object,
                       rules: List[Regularity],
                       model: BaseModel) -> Tuple[float, Predicate]:

    literals_to_add = set(
        rule.conclusion for rule in rules if lits.rule_applicability(rule) and rule.conclusion not in lits
    )
    argmax = UndefinedPredicate()
    max_delta_consistency = .0
    max_consistency_added = .0

    consistency_lits = consistency(lits, rules, model)

    for literal in literals_to_add:
        consistency_added = consistency(lits.add(literal), rules, model)
        delta_consistency = consistency_added - consistency_lits

        max_delta_consistency = max(delta_consistency, max_delta_consistency)

        if consistency_added > max_consistency_added:
            argmax = literal
            max_consistency_added = consistency_added
    #print(consistency(lits.add(argmax), rules, model), consistency(lits, rules, model))
    #print(max_delta_consistency, argmax)

    return max_delta_consistency, argmax


def __delta_argmax_add_spec(lits: Object,
                            rules: List[Regularity],
                            model: BaseModel) -> Tuple[float, Predicate]:

    literals_to_add = set(
        rule.conclusion for rule in rules if lits.rule_applicability(rule) and rule.conclusion not in lits
    )
    argmax = UndefinedPredicate()
    max_delta_consistency = .0
    max_consistency_added = .0

    for literal in literals_to_add:
        consistency_added = consistency_add(lits.add(literal), literal, rules, model)
        consistency_lits = consistency_add(lits, literal, rules, model)
        delta_consistency = consistency_added - consistency_lits
        if delta_consistency > max_delta_consistency:
            max_delta_consistency = delta_consistency
            argmax = literal

    return max_delta_consistency, argmax


def __delta_argmax_del(lits: Object,
                       rules: List[Regularity],
                       model: BaseModel) -> Tuple[float, Predicate]:

    argmax = UndefinedPredicate()
    max_delta_consistency = .0
    max_consistency_deleted = .0

    consistency_lits = consistency(lits, rules, model)

    for literal in lits:
        consistency_deleted = consistency(lits.delete(literal), rules, model)
        delta_consistency = consistency_deleted - consistency_lits

        max_delta_consistency = max(delta_consistency, max_delta_consistency)

        if consistency_deleted > max_consistency_deleted:
            argmax = literal
            max_consistency_deleted = consistency_deleted

    return max_delta_consistency, argmax


def log_prob(r: Regularity, model: BaseModel) -> float:
    return -mlog(1 - r.eval_prob(model))


def load_yml_fix_points(path: str = None, stream=None) -> List[Object]:
    if path is not None:
        with open(path, 'r') as f:
            return [Object.from_dict(obj) for obj in yaml.load(f, Loader=yaml.FullLoader)]
    elif stream is not None:
        return [Object.from_dict(obj) for obj in yaml.load(stream, Loader=yaml.FullLoader)]
    else:
        raise ValueError('you must pass `path` or `stream`')
