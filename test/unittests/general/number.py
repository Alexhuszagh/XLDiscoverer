'''
    Unittests/General/number
    ________________________

    Test suite for a mutable number recipe.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import copy
import operator as op
import numbers
import random
import six
import unittest

from xldlib.general import number

# CASES
# -----


class MutableNumberTest(unittest.TestCase):
    '''Test mathematical operations and copy/deepcopy constructors'''

    def setUp(self):
        '''Set up unittests'''

        self.zero = number.MutableNumber(0)

        self.int = random.randint(1, 100)
        self.mutable_int = number.MutableNumber(self.int)

        self.float = random.random() + 0.0001 # nonzero
        self.mutable_float = number.MutableNumber(self.float)

    #   PROPERTIES

    @property
    def numbers(self):
        return (self.int, self.float)

    @property
    def mutables(self):
        return (self.mutable_int, self.mutable_float)

    @property
    def items(self):
        return zip(self.numbers, self.mutables)

    #     TESTS

    def test_add(self):
        '''Test lefthand, righthand, and in-place addition'''

        self._test_operation(op.add, op.iadd)

    def test_sub(self):
        '''Test lefthand, righthand, and in-place subtraction'''

        self._test_operation(op.sub, op.isub)

    def test_mul(self):
        '''Test lefthand, righthand, and in-place multiplication'''

        self._test_operation(op.mul, op.imul)

    def test_div(self):
        '''Test lefthand, righthand, and in-place division'''

        self._test_operation(op.truediv, op.itruediv)
        self._test_operation(op.floordiv, op.ifloordiv)
        if six.PY2:
            # op.div only defined in Py2
            self._test_operation(op.div, op.idiv)

    def test_pow(self):
        '''Test lefthand, righthand, and in-place powers'''

        self._test_operation(op.pow, op.ipow)

    def test_lshift(self):
        '''Test lefthand, righthand, and left-shift powers'''

        self._test_operation(op.lshift, op.ilshift, int_only=True)

    def test_rshift(self):
        '''Test lefthand, righthand, and right-shift powers'''

        self._test_operation(op.rshift, op.irshift, int_only=True)

    def test_abs(self):
        '''Test absolute values'''

        absolute = abs(self.mutable_int)
        self.assertIsInstance(absolute, number.MutableNumber)
        self.assertEquals(absolute.number, abs(self.int))

    def test_neg(self):
        '''Test negation'''

        neg = -self.mutable_int
        self.assertIsInstance(neg, number.MutableNumber)
        self.assertEquals(neg.number, -self.int)

    def test_pos(self):
        '''Test positive form'''

        pos = +self.mutable_int
        self.assertIsInstance(pos, number.MutableNumber)
        self.assertEquals(pos.number, +self.int)

    def test_bool(self):
        '''Test boolean expectations'''

        self.assertFalse(self.zero)
        self.assertTrue(self.mutable_int)
        self.assertTrue(self.mutable_float)

    def test_and(self):
        '''Test lefthand, righthand, and bitwise and powers'''

        self._test_operation(op.and_, op.iand, int_only=True)

    def test_or(self):
        '''Test lefthand, righthand, and bitwise or powers'''

        self._test_operation(op.or_, op.ior, int_only=True)

    def test_xor(self):
        '''Test lefthand, righthand, and bitwise xor powers'''

        self._test_operation(op.xor, op.ixor, int_only=True)

    def test_cmp(self):
        '''Test comparisons'''

        for numeral, mutable in self.items:
            lt = numeral - 0.01
            gt = numeral + 0.01

            self.assertLess(lt, mutable)
            self.assertLessEqual(lt, mutable)
            self.assertLessEqual(numeral, mutable)

            self.assertGreater(gt, mutable)
            self.assertGreaterEqual(gt, mutable)
            self.assertGreaterEqual(numeral, mutable)

    def test_types(self):
        '''Test type conversions'''

        for mutable in self.mutables:
            self.assertIsInstance(int(mutable), int)
            self.assertIsInstance(float(mutable), float)
            self.assertIsInstance(mutable.conjugate(), type(mutable.number))
            self.assertIsInstance(complex(mutable), complex)

            if six.PY2:
                self.assertIsInstance(long(mutable), long)

    def test_copy(self):
        '''Test shallow and deepcopy operations'''

        shallow = copy.copy(self.mutable_int)
        self.assertIsInstance(shallow, number.MutableNumber)
        self.assertEquals(shallow.number, self.mutable_int.number)

        deep = copy.deepcopy(self.mutable_int)
        self.assertIsInstance(deep, number.MutableNumber)
        self.assertEquals(deep.number, self.mutable_int.number)

    #   NON-PUBLIC

    def _test_operation(self, operator, inplace, int_only=False):
        '''Non-public test for lefthand, righthand, and inplace operations'''

        for numeral, mutable in self.items:
            if int_only:
                if isinstance(numeral, float):
                    continue
                rand = random.randint(0, 100)
            else:
                rand = random.random()

            self._test_lefthand(operator, numeral, mutable, rand)
            self._test_rightthand(operator, numeral, mutable, rand)
            self._test_inplace(operator, inplace, numeral, mutable, rand)

    def _test_lefthand(self, operator, numeral, mutable, rand):
        '''Test lefthand operations'''

        left = operator(mutable, rand)
        self.assertIsInstance(left, number.MutableNumber)
        self.assertIsInstance(left.number, numbers.Real)
        self.assertAlmostEquals(left, operator(numeral, rand))

    def _test_rightthand(self, operator, numeral, mutable, rand):
        '''Test lefthand operations'''

        right = operator(rand, mutable)
        self.assertIsInstance(right, numbers.Real)
        self.assertAlmostEquals(right, operator(rand, numeral))

    def _test_inplace(self, operator, inplace, numeral, mutable, rand):
        '''Test inplace operations'''

        new = copy.copy(mutable)
        inplace(new, rand)
        self.assertIsInstance(new, number.MutableNumber)
        self.assertIsInstance(new.number, numbers.Real)
        self.assertAlmostEquals(new, operator(numeral, rand))

    def tearDown(self):
        '''Tear down unittests'''

        del self.int, self.mutable_int, self.float, self.mutable_float


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(MutableNumberTest('test_add'))
    suite.addTest(MutableNumberTest('test_sub'))
    suite.addTest(MutableNumberTest('test_mul'))
    suite.addTest(MutableNumberTest('test_div'))
    suite.addTest(MutableNumberTest('test_pow'))
    suite.addTest(MutableNumberTest('test_lshift'))
    suite.addTest(MutableNumberTest('test_rshift'))
    suite.addTest(MutableNumberTest('test_neg'))
    suite.addTest(MutableNumberTest('test_pos'))
    suite.addTest(MutableNumberTest('test_bool'))
    suite.addTest(MutableNumberTest('test_and'))
    suite.addTest(MutableNumberTest('test_or'))
    suite.addTest(MutableNumberTest('test_xor'))
    suite.addTest(MutableNumberTest('test_cmp'))
    suite.addTest(MutableNumberTest('test_types'))
    suite.addTest(MutableNumberTest('test_copy'))
