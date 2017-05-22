
# load modules
import os
import sys
import unittest

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path)

from objects import mod


class TestModObject(unittest.TestCase):
    '''
    Tests the mod objects to be correct.
    '''

    def setUp(self):
        '''Create mob object and bind'''

        self.mod_obj = mod.Mod("Label:2H(4)", "H-4 2H4", "K")

    def test_mob_obj(self):

        self.assertEqual(repr(self.mod_obj),
            'Mod(name=Label:2H(4), position=K, uncleaved=False, '
            'constant=False, variable=True)')
        self.assertEqual(self.mod_obj._formula, 'H-4 2H4')
        self.assertEqual(self.mod_obj.position, frozenset(['K', 'prot_nterm']))

if __name__ == '__main__':
    unittest.main()
