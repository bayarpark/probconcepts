from ..utils.fisher import fisher_exact
from typing import NewType, Tuple

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
                if c!=0 and  not lit(p):
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
