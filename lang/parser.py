from lang.regularity import Regularity


def compress_str(rule: Regularity) -> str:
    rule_str = ""
    for pr in rule.premise:
        rule_str += str(pr.ident) + ' '
        rule_str += str(pr.operation)[1:]
        rule_str += '&'

    rule_str = rule_str[:-1] + "@"
    rule_str += str(rule.conclusion.ident) + ' '
    rule_str += str(rule.conclusion.operation)[1:]
    rule_str += " {} {}".format(str(rule.pvalue), str(rule.prob))
    return rule_str
