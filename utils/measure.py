from typing import NewType, Tuple

from .fisher import fisher_exact

PValue = NewType('PValue', float)
Proba = NewType('Proba', float)


def std_measure(rule, model) -> Tuple[Proba, PValue]:
    top = 0
    bottom = 0
    cons_count = 0
    all_sum = 0
    for obj in model.sample.data:
        d, n = 1, 1
        val_is_unknown = False
        for lit in rule.premise:
            p = obj[lit.ident]
            if p is None:
                val_is_unknown = True
                break
            if not lit(p):
                d = 0
        p = obj[rule.conclusion.ident]
        if val_is_unknown or p is None:
            d, n = 0, 0
        else:
            all_sum += 1
            if rule.conclusion(p):
                cons_count += 1

            if d == 0 or not rule.conclusion(p):
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
