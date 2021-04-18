import unittest

from lang.predicate import Predicate, Var


class TestPredicate(unittest.TestCase):
    def test_EqPredicate(self):
        predicate = Predicate('test', Var.Cat, opt='=', params='TestCatValue')

        self.assertTrue(predicate('TestCatValue'))
        self.assertFalse(predicate(1423))

    def test_NeqPredicate(self):
        predicate = Predicate('test', Var.Cat, opt='!=', params='TestCatValue')

        self.assertFalse(predicate('TestCatValue'))
        self.assertTrue(predicate(1423))

    def test_InPredicate(self):
        predicate = Predicate('test', Var.Float, opt='in', params=[0.1, .245])

        self.assertTrue(predicate(0.145))
        self.assertFalse(predicate(12))

    def test_GePredicate(self):
        predicate = Predicate('test', Var.Float, opt='>', params=42)

        self.assertTrue(predicate(43))
        self.assertFalse(predicate(12))

    def test_PredicateInvert(self):
        predicate = Predicate('test', Var.Cat, opt='=', params='TestCatValue')
        predicate_inverted = Predicate('test', Var.Cat, opt='!=', params='TestCatValue')

        self.assertEqual(~predicate, predicate_inverted)
        self.assertNotEqual(predicate, predicate_inverted)

    def test_TruthOnObject(self):
        obj1 = [42, 43, 44]
        obj2 = [33, 34, 35, 213, 432]
        predicate = Predicate(2, Var.Cat, opt='=', params=44)

        self.assertTrue(predicate[obj1])
        self.assertFalse(predicate[obj2])

    def test_FromToDict(self):
        predicate = Predicate('test', Var.Bool, opt='=', params=True)
        predicate_dict = predicate.to_dict()

        predicate_from_dict = Predicate.from_dict(predicate_dict)

        self.assertEqual(predicate, predicate_from_dict)
