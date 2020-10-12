from core.fisher import *
from typing import *


def std_prob_measure(rule: 'Rule', par: 'FindParams') -> Tuple[float, float]:
    top = 0
    bottom = 0
    cons_count = 0
    all_sum = 0
    for obj in par.dataset:
        d, n = 1, 1
        val_is_unknown = False
        for lit in rule.features:
            p = obj[lit.id()]
            if p == 0:
                val_is_unknown = True
                break
            if (not lit.val() and p == -1) or (lit.val() and p == 1):
                d = 0
                break
        p = obj[rule.concl.id()]
        if val_is_unknown or p == 0:
            d, n = 0, 0
        else:
            all_sum += 1
            if rule.concl.val() and p == 1 \
                    or not rule.concl.val() and p == -1:
                cons_count += 1

            if d == 0 or (not rule.concl.val() and p == -1) or \
                    (rule.concl.val() and p == 1):
                n = 0
        top += n
        bottom += d

    absolute_prob = (cons_count + 1) / (par.dataset_size + 2)  # absolute_prob д.б. < cond_prob
    cond_prob = (top + 1) / (bottom + 2) if top != 0 and bottom != 0 else 0.

    if absolute_prob >= cond_prob:  # Костыль -- если абсоютная в-ть >= условной, то возвращаем p_val = 1
        return cond_prob, 1.

    contingency_table = [[top, bottom - top], [cons_count - top, all_sum - cons_count - bottom + top]]
    p_val = fisher_exact(contingency_table)

    return cond_prob if top != 0. and bottom != 0. else 0., p_val
