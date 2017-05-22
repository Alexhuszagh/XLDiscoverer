'''
    Unittests/Utils/Masstools/charged_mass
    ______________________________________

    Unittests for mass-to-charge ratio (m/z) and mass error (ppm)
    calculations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from namedlist import namedlist

from xldlib.utils.masstools import charged_mass


# OBJECTS
# -------

Test = namedlist("Test", "input expected")


# ITEMS
# -----


MZ = [
    Test(input=(500., 3, 0),
        expected=167.67394313666668),
    Test(input=(167.673943137, 0, 3),
        expected=500.),
    Test(input=(500., 3, 1),
        expected=167.33818431333333),
    Test(input=(500., 3, 2),
        expected=333.66909215666664),
]


PPM = [
    Test(input=(500., 2, 333.669, 3),
        expected=0.276470076),
    Test(input=(333.669, 3, 500., 2),
        expected=-0.276191798)
]


# CASES
# -----


class ChargedMassTest(unittest.TestCase):
    '''Test theoretical to expected mass calculations'''

    def test_mz(self):
        '''Test mass to charge calculations'''

        for item in MZ:
            result = charged_mass.mz(*item.input)
            self.assertAlmostEquals(result, item.expected, 5)

    def test_ppm(self):
        '''Test mass error calculations'''

        for item in PPM:
            result = charged_mass.ppm(*item.input)
            self.assertAlmostEquals(result, item.expected, 5)


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ChargedMassTest('test_mz'))
    suite.addTest(ChargedMassTest('test_ppm'))
