from math import log, exp, lgamma
from typing import List


def fisher_exact(crosstab: List[List[int]], enable_assert=True) -> float:
    """
    Right tail fisher's exact projecttest
    for 2x2 contingency table
    :param crosstab: 2x2 contingency table
    :param enable_assert: enable assert
    :return: p-value
    """

    if enable_assert:
        if any(map(lambda x: x < 0, crosstab)):
            raise ValueError("All values in `crosstab` must be nonnegative.")

    a = crosstab[0][0]
    ab = a + crosstab[0][1]
    ac = a + crosstab[1][0]
    all_sum = sum(map(sum, crosstab))

    a_min = max(0, ab+ac-all_sum)
    a_max = min(ab, ac)
    if a_min == a_max:
        return 1.
    p0 = lgamma(ab+1) + lgamma(ac+1) + lgamma(all_sum-ac+1) + lgamma(all_sum-ab+1) - lgamma(all_sum+1)
    pa = lgamma(a+1) + lgamma(ab-a+1) + lgamma(ac-a+1) + lgamma(all_sum-ab-ac+a+1)

    if ab * ac > a * all_sum:
        sl = 0.
        for i in range(a-1, a_min-1, -1):
            sl_new = sl + exp(pa - lgamma(i+1) - lgamma(ab-i+1) - lgamma(ac-i+1) - lgamma(all_sum-ab-ac+i+1))
            if sl_new == sl:
                break
            sl = sl_new
        return 1. - max(0, exp(p0 - pa) * sl)
    else:
        sr = 1.
        for i in range(a+1, a_max+1):
            sr_new = sr + exp(pa - lgamma(i+1) - lgamma(ab-i+1) - lgamma(ac-i+1) - lgamma(all_sum-ab-ac+i+1))
            if sr_new == sr:
                break
            sr = sr_new
        return exp(-max(0., pa - p0 - log(sr)))
