from alg.model import *
from time import time

a = pd.read_csv('/home/bayar/git/probconcepts/projecttest/numbers/numbers.csv')
qwertty = ['lox' + str(i % 2) for i in range(360)]
qwertty[359] = None
a['25'] = qwertty

cd = create_cd(a, cat_features=[str(i) for i in range(1, 25)], bool_features=[24])
a = missing_cat_bool_typecast(a, cd)
p = PredicateEncoder(a, cd)
p.encode()
p.generate_pt()
s = Sample(a, p, cd)

ts = time()
for _ in range(100000):
    iter(p)
print(f'{time() - ts} sec')



"""
import pandas as pd
from lang.predicate import Predicate
from numpy import *
from lang.opers import Var
from time import time
d = [[i*j for i in range(50)] for j in range(100000)]
df = pd.DataFrame(d)

p = Predicate(ident=100, vartype=Var.Int, opt='=', params=99)

t_n = time()
for i in range(100000):
    for j in range(50):
        if p(d[i][j]):
            2*100

print(time() - t_n)


dt = tuple(tuple(a) for a in d)

t_n = time()
for i in range(100000):
    for j in range(50):
        if p(dt[i][j]):
            2*100
print(time() - t_n)

da = array(d)

t_n = time()
for i in range(100000):
    for j in range(50):
        if p(da[i][j]):
            2*100
print(time() - t_n)

t_n = time()
for i in range(100000):
    for j in range(50):
        if p(df.iloc[i, j]):
            2*100

print(time() - t_n)
"""





