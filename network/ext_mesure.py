from ..alg.data import Sample
from ..lang.regularity import Regularity
from .extregularity import Conjunction
from ..utils.fisher import fisher_exact
from typing import NewType, Tuple, List, Dict
from sklearn.metrics import roc_auc_score, precision_score, accuracy_score, recall_score, f1_score
import numpy as np
from tqdm import tqdm

PValue = NewType('PValue', float)
Proba = NewType('Proba', float)


def ext_std_measure(rule, model) -> Tuple[Proba, PValue]:
                        # P(A|B) = P(A&B) / P(B) A-premise, B-conclusion
    top = 0             # num obj where A&B is true
    bottom = 0          # num obj where A is true
    cons_count = 0      # num obj where B is true
    all_sum = 0         # num obj where all features is not None
    for obj in model.sample.data:
        d, n = 1, 1     # n = A&B is true on obj, d = A is true on obj
        prem_is_unknown = False
        concl_is_unknown = False

        # checking premise
        for lit in rule.premise:
            p = obj[lit.ident]
            if p is None:
                prem_is_unknown = True
                break
            if d != 0 and not lit(p):
                d = 0

        # checking conclusion
        if prem_is_unknown:
            d, n = 0, 0
        else:
            c = 1  # conclusion is True
            for lit in rule.conclusion:
                p = obj[lit.ident]
                if p is None:
                    concl_is_unknown = True
                    break
                if c != 0 and not lit(p):
                    c = 0

            if concl_is_unknown:
                d, n = 0, 0
            else:
                all_sum += 1
                cons_count += c
                if c == 0 or d == 0:
                    n = 0

        top += n
        bottom += d

    absolute_prob = (cons_count + 1) / (model.sample.shape[0] + 2)  # absolute_prob д.б. < cond_prob
    cond_prob = (top + 1) / (bottom + 2) if top != 0 and bottom != 0 else 0.

    if absolute_prob >= cond_prob:  # Костыль -- если абсолютная в-ть >= условной, то возвращаем p_val = 1
        return Proba(cond_prob), PValue(1.)

    crosstab = [[top, bottom - top], [cons_count - top, all_sum - cons_count - bottom + top]]
    p_val = fisher_exact(crosstab)

    return Proba(cond_prob) if top != 0. and bottom != 0. else 0., PValue(p_val)


def check_rules(rules: List[Regularity], obj: Sample.data, types: List[str], conjs: List[Conjunction]) \
                                            -> Tuple[List[Regularity], float]:

    perf_rules = []
    total_prob = 0
    num_pr = len(types) - len(conjs)

    for rule in rules:
        performed = True
        for pr in rule.premise:
            if types[pr.ident] == "pr":  # checking predicate in obj
                p = obj[pr.ident]
                if p is None or not pr(p):
                    performed = False
                    break

            elif types[pr.ident] == "conj":      # checking conjunction in obj
                perf_conj = True
                conj = conjs[pr.ident - num_pr]  # сопоставление конъюнкции в массиве по id признака
                # если параметр конъюнкции True,
                # то конъюнкция верна, когда все конъюнкты истинны
                # ложна, когда хоть один конъюнкт ложный
                if pr.operation.params == "True":
                    for lit in conj.predicates:
                        p = obj[lit.ident]
                        if p is None or not lit(p):
                            perf_conj = False
                            break

                # если параметр конъюнкции False,
                # то конъюнкция верна, когда хотя бы один конъюнкт ложный
                # ложна, когда все конъюнкты истинны
                else:
                    all_true = True
                    for lit in conj.predicates:
                        p = obj[lit.ident]
                        if p is None or not lit(p):
                            all_true = False
                            perf_conj = True
                            break
                    if all_true:
                        perf_conj = False

                if not perf_conj:
                    performed = False
                    break
            else:
                raise ValueError("Unknown type of lit in rule")

        if performed:
            total_prob += rule.prob
            perf_rules.append(rule)

    return perf_rules, total_prob/len(rules)


def str_conj_rule(rule, types, conjs):
    str_rule = ''
    for pr in rule.premise:
        if types[pr.ident] == 'pr':
            str_rule += str(pr) + ' & '
        if types[pr.ident] == 'conj':
            str_rule += str() + ""
    return str_rule


def make_predictions(data: Sample.data, labels: List[int], neg_rules: List[Regularity], pos_rules: List[Regularity],
                     types: List[str], conjs: List[Conjunction], pred_log, rules_log) \
        -> Tuple[List[int], List[int], Dict[str, float], Dict[str, float]]:

    with open(pred_log, 'w') as f_pred, open(rules_log, 'w') as f_rules:
        sel_preds = []
        preds = []
        metrics = dict()
        sel_metrics = dict()
        for obj_i, obj in enumerate(tqdm(data)):
            perf_neg, logits_neg = check_rules(neg_rules, obj, types, conjs)
            perf_pos, logits_pos = check_rules(pos_rules, obj, types, conjs)

            # pred = np.argmax([logits_neg, logits_pos]) # максимальное по кол-ву применимых правил
            pred = np.argmax([logits_neg, logits_pos])
            preds.append(pred)
            sel_pred = pred

            if (abs(logits_neg-logits_pos)/max(logits_neg, logits_pos)) <= 0.25 or logits_neg == 0 or logits_pos == 0:
                sel_pred = -1
                sel_preds.append(sel_pred)
            else:
                sel_preds.append(sel_pred)

            # printing logs for object without rules
            print("Object:", obj_i, file=f_pred)
            for i, x_i in enumerate(obj):
                print(f"|{i}:{x_i}| ", end='', file=f_pred)
            print(file=f_pred)
            print(f"num rules: {[len(perf_neg), len(perf_pos)]}, logits: {[logits_neg, logits_pos]}", file=f_pred)
            print(f"pred label: {pred}, true label: {labels[obj_i]}. skipped: {sel_pred==-1}", file=f_pred)
            print(f"Prediction: {pred == labels[obj_i]}", file=f_pred)
            print("--------------------------", file=f_pred)

            # printing performed rules for object
            print("Object:", obj_i, file=f_rules)
            for i, x_i in enumerate(obj):
                print(f"|{i}:{x_i}| ", end='', file=f_rules)
            print(file=f_rules)
            print(f"NEGATIVE RULES : {len(perf_neg)}", file=f_rules)
            for rule in perf_neg:
                print(rule, file=f_rules)
            print(f"POSITIVE RULES : {len(perf_pos)}", file=f_rules)
            for rule in perf_pos:
                print(rule, file=f_rules)
            print("--------------------------", file=f_rules)

        # calculating metrics
        metrics["accuracy"] = accuracy_score(labels, preds)
        metrics["precision"] = precision_score(labels, preds)
        metrics["recall"] = recall_score(labels, preds)
        metrics["f1"] = f1_score(labels, preds)
        metrics["roc_auc"] = roc_auc_score(labels, preds)

        print("Metrics on full data", file=f_pred)

        print("All objects", file=f_pred)
        for key, value in metrics.items():
            print(key, ' : ', value, file=f_pred)
        print("--------------------------", file=f_pred)

        # calculating metrics on selected data
        sel_pred_sq = []  # removing -1
        sel_lbls = []
        for i, p in enumerate(sel_preds):
            if p != -1:
                sel_pred_sq.append(p)
                sel_lbls.append(labels[i])

        sel_metrics["accuracy"] = accuracy_score(sel_lbls, sel_pred_sq)
        sel_metrics["precision"] = precision_score(sel_lbls, sel_pred_sq)
        sel_metrics["recall"] = recall_score(sel_lbls, sel_pred_sq)
        sel_metrics["f1"] = f1_score(sel_lbls, sel_pred_sq)
        sel_metrics["roc_auc"] = roc_auc_score(sel_lbls, sel_pred_sq)

        print("Metrics on selected data", file = f_pred)
        for key, value in sel_metrics.items():
            print(key, ' : ', value, file=f_pred)

    return preds, sel_preds, metrics, sel_metrics
