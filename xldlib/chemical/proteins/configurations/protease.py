'''
    Chemical/Proteins/Configurations/protease
    _________________________________________

    Proteolytic enzyme configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from namedlist import namedlist

import tables as tb

from xldlib.chemical import building_blocks
from xldlib.general import mapping, sequence
from xldlib.resources import paths

__all__ = [
    'ENZYMES',
    'Protease',
    'TERMINI',
]

# PATHS
# -----
ENZYME_PATH = os.path.join(paths.DIRS['data'], 'enzymes.json')

# ENUMS
# -----

TERMINI = tb.Enum([
    'N',
    'C'
])


# OBJECTS
# -------


@sequence.serializable("Protease")
class Protease(namedlist("Protease", "name cut nocut side")):
    '''Definitions for a protease configuration object'''

    # RESIDUES
    # --------
    _residues = set(building_blocks.ONE_LETTER)

    #    PROPERTIES

    @property
    def nterm(self):
        return self.side == TERMINI['N']

    @property
    def cterm(self):
        return not self.nterm

    @property
    def cut_residues(self):
        '''
        Identify residues cut from by `self` at a residue,
        by filtering out all the `self.nocut` sites.
        '''

        return ''.join(self._residues - set(self.nocut))

    @property
    def cut_site(self):
        '''Unformatted regex for a specific cut site.'''

        if self.nterm:
            return r'[{}]{{residue}}'.format(self.cut_residues)
        else:
            return r'{{residue}}[{}]'.format(self.cut_residues)

    @property
    def cut_regex(self):
        '''Uncompiled regular expression mimicing a protease'''

        return '|'.join([self.cut_site.format(residue=i) for i in self.cut])


# DATA
# ----

ENZYMES = mapping.Configurations(ENZYME_PATH, [
    ('Trypsin', Protease(name='Trypsin',
            cut=['K', 'R'],
            nocut=['P'],
            side=TERMINI['C'])),
    ('Lys-C', Protease(name='Lys-C',
            cut=['K'],
            nocut=[],
            side=TERMINI['C'])),
    ('Lys-N', Protease(name='Lys-N',
            cut=['K'],
            nocut=[],
            side=TERMINI['N'])),
    ('Trypsin + Lys-C', Protease(name='Trypsin + Lys-C',
            cut=['K', 'R'],
            nocut=[],
            side=TERMINI['C'])),
    ('Chymotrypsin FYW', Protease(name='Chymotrypsin FYW',
            cut=['F', 'Y', 'W'],
            nocut=['P'],
            side=TERMINI['C'])),
    ('Chymotrypsin FYWLM', Protease(name='Chymotrypsin FYWLM',
            cut=['F', 'Y', 'W', 'L', 'M'],
            nocut=['P'],
            side=TERMINI['C'])),
    ('Chymotrypsin FYWLMKR', Protease(name='Chymotrypsin FYWLMKR',
            cut=['F', 'Y', 'W', 'L', 'M', 'K', 'R'],
            nocut=['P'],
            side=TERMINI['C'])),
    ('Chymotrypsin FWYMEDLN', Protease(name='Chymotrypsin FWYMEDLN',
            cut=['F', 'W', 'Y', 'M', 'E', 'D', 'L', 'N'],
            nocut=['P'],
            side=TERMINI['C']))
])
