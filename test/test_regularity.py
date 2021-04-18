import unittest

from lang.predicate import Predicate, Var
from lang.regularity import Regularity


class TestRegularity(unittest.TestCase):
    def setUp(self):
        p1 = Predicate(name=1, vtype=Var.Cat, opt='!=', params=10)
        p2 = Predicate(name=2, vtype=Var.Bool, opt='=', params=True)
        p3 = Predicate(name=3, vtype=Var.Int, opt='<=', params=42)
        p4 = Predicate(name=4, vtype=Var.Float, opt='in', params=[0.42, 42.22])

        p0 = Predicate(name=5, vtype=Var.Bool, opt='=', params=False)

        self.reg = Regularity(p0, [p1, p2, p3, p4])

    def test_CorrectIsNonnegative(self):
        self.assertTrue(self.reg.is_nonnegative())

    def test_CorrectIsPositive(self):
        self.assertFalse(self.reg.is_positive())

    def test_FromToDict(self):
        self.reg.prob = .0
        self.reg.pvalue = .0
        reg_dict = self.reg.to_dict()
        reg_from_dict = Regularity.from_dict(reg_dict)
        self.assertEqual(self.reg, reg_from_dict)

