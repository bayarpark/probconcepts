from typing import List, Dict
from tqdm import tqdm
import glob

from .opers import Var
from .predicate import Predicate
from .regularity import Regularity


def cstr(rule: Regularity) -> str:
    rule_str = ""
    for pr in rule.premise:
        rule_str += str(pr.name) + ' '
        rule_str += str(pr.operation)[1:] + '&'

    rule_str = rule_str[:-1] + '@'
    rule_str += str(rule.conclusion.name) + ' '
    rule_str += str(rule.conclusion.operation)[1:]
    rule_str += " {} {}".format(str(rule.prob), str(rule.pvalue))
    return rule_str


def decstr_folder(path_to_folder: str,
                  cd: 'ColumnsDescription' = None,
                  ctype_dict: Dict[int, str] = None,
                  min_prob: float = None,
                  max_pvalue: float = None) -> List[Regularity]:

    if ctype_dict is None:
        ctype_dict = {cd.features[feature_num]: feature_type for feature_num, feature_type in cd.type_dict.items()}

    if not path_to_folder.endswith('/') or not path_to_folder.endswith('\\'):
        path_to_folder = path_to_folder + '/'

    rules = []
    for file in tqdm(glob.glob(path_to_folder + '*.txt')):
        rules.extend(decstr(file, ctype_dict, min_prob, max_pvalue))
    return rules


def decstr(filename: str,
           ctype_dict: Dict[int, str],
           min_prob: float = None,
           max_pvalue: float = None) -> List[Regularity]:

    with open(filename, 'r') as f:
        rules = []
        for line in f:
            i, premise = read_premise(line, ctype_dict)
            i, concl = read_concl(i, line, ctype_dict)
            prob, pvalue = read_probs(i, line, len(line))

            rule = Regularity(conclusion=concl, premise=premise)

            if (min_prob is not None and prob < min_prob) or (max_pvalue is not None and pvalue > max_pvalue):
                continue
            else:
                rule.prob = prob
                rule.pvalue = pvalue
                rules.append(rule)

        return rules


def read_premise(line, ctype_dict):
    i = 0
    premise = []
    while True:
        name = ""
        opt = ""
        par = ""

        # reading name of predicate (int)
        while line[i] != ' ':
            name += line[i]
            i += 1
        i += 1  # move pointer to operator
        int_id = int(name)

        # reading operator of predicate (Opt)
        # =, !=, <, >, =>, <=, in
        while line[i] != ' ':
            opt += line[i]
            i += 1
        i += 1  # move pointer to parameter

        # reading parameter for operator (float, [a,b], bool)
        while line[i] != '&' and line[i] != '@':
            par += line[i]
            i += 1
        i += 1  # move pointer to next predicate

        premise.append(cstr_to_predicate(int_id, ctype_dict[int_id], opt, par))
        if line[i-1] == '@':
            return i, premise
        elif line[i-1] != '&':
            raise ValueError('Error in parsing. Expected &, got {} in line: {}'.format(line[i-1], line))


def cstr_to_predicate(int_id, str_var, opt, par):
    # case interval
    if par[0] == '[':
        j = 0
        while par[j] != ',':
            j += 1
        a = par[1:j]
        b = par[j + 1:len(par) - 1]

        return Predicate(int_id, Var(str_var), opt=str(opt), params=(float(a), float(b)))
    else:
        if str_var == 'B':
            if par == "False":
                bool_par = False
            else:
                bool_par = True
            return Predicate(int_id, Var(str_var), opt=str(opt), params=bool_par)
        if str_var == 'C' or str_var == 'I':
            return Predicate(int_id, Var(str_var), opt=str(opt), params=int(par))
        elif str_var == 'F':
            return Predicate(int_id, Var(str_var), opt=str(opt), params=float(par))  # TODO float parameter


def read_concl(i, line, ctype_dict):
    name = ""
    opt = ""
    par = ""

    # reading name of predicate (int)
    while line[i] != ' ':
        name += line[i]
        i += 1
    i += 1  # move pointer to operator
    int_id = int(name)

    # reading operator of predicate (Oper)
    # =, !=, <, >, =>, <=, in
    while line[i] != ' ':
        opt += line[i]
        i += 1
    i += 1  # move pointer to parameter

    # reading parameter for operator (float, [a,b], bool)
    while line[i] != ' ':
        par += line[i]
        i += 1
    i += 1  # move pointer to pvalue

    conclusion = cstr_to_predicate(int_id, ctype_dict[int_id], opt, par)

    return i, conclusion


def read_probs(i, line, len_line):
    j = i
    while line[j] != ' ':
        j += 1

    prob = line[i:j]
    pvalue = line[j+1:len_line]

    return float(prob), float(pvalue)
