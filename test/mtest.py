from alg.model import *

a = pd.read_csv('test/numbers/numbers.csv')
cd = create_cd(a, cat_features=[str(i) for i in range(1, 25)])
p = PredicateEncoder(a, cd)
p.encode()
p.generate_pt()
s = Sample(a, p, cd)


