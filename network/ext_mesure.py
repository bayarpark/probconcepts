from utils.fisher import fisher_exact
from typing import NewType, Tuple

PValue = NewType('PValue', float)
Proba = NewType('Proba', float)


def ext_std_measure(rule, model) -> Tuple[Proba, PValue]:
    top = 0
    bottom = 0
    cons_count = 0
    all_sum = 0
    for obj in model.sample.data:
        d, n = 1, 1
        prem_val_is_unknown = False
        for lit in rule.premise:
            p = obj[lit.ident]
            if p is None:
                prem_val_is_unknown = True
                d = 0
                break
            if not lit(p):
                d = 0
                break

        concl_true = True
        concl_val_is_unknown = False
        for lit in rule.conclusion:
            p = obj[lit.ident]
            if p is None:
                concl_val_is_unknown = True
                break
            if not lit(p):
                n = 0
                concl_true = False
                break

        if not concl_val_is_unknown and not prem_val_is_unknown:
            all_sum += 1
            if concl_true:
                cons_count += 1

            if d == 0 or not concl_true:
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
