'''
    XlPy/matched/Proteome_Discoverer/base
    _____________________________________

    Inheritable objects with methods to calculate Proteome Discoverer
    peptide ID formulas PPMs, and standardize the peptide sequences
    (use of mixed case).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# losd modules
import copy

from xldlib import chemical
from xldlib.utils import logger, masstools

# load objects/functions
from libs.definitions import ZIP
from ..base import MatchedPeptideBase
from ..core import get_engine, unpack_mods


class ProteomeDiscovererUtils(object):
    '''Provides useful methods for formula and PPM calculation'''

    def calculate_formula(self, peptide, mods):
        '''
        Calculates the exact formula for the peptide without XLer
        modification
        '''

        atom_counts = chemical.Molecule(peptide=peptide)
        mods = unpack_mods(mods)
        for name, pos in mods.items():
            if name not in self.fragments and name in self.engine['mods']:
                formula = self.engine['mods'][name][0]
                count = len(pos)
                atom_counts.update_formula(formula, count=count)

        return atom_counts

    def calculate_ppm(self, atom_counts, mods, exper, charge):
        '''Calculates the theroetical PPM from the exper mass'''

        atom_counts = copy.deepcopy(atom_counts)
        mods = unpack_mods(mods)

        for name, pos in mods.items():
            if name in self.fragments:
                formula = self.fragments[name]
                count = len(pos)
                atom_counts.update_formula(formula, count=count)

        theor = masstools.mz(atom_counts.mass, charge, 0)
        return (theor - exper) / exper * 1e6

    def upper_sequences(self):
        '''Converts all the annotated, lowercase residues to uppercase'''

        self.data['peptide'] = [i.upper() for i in self.data['peptide']]

    def calculate_ppms(self):
        '''Calculates the theoretical PPMs for each entry'''

        self.data.setdefault('formula', [])

        keys = ['peptide', 'mods', 'm/z', 'z']
        for peptide, mod, exper, charge in ZIP(*map(self.data.get, keys)):
            formula = self.calculate_formula(peptide, mod)
            self.data['formula'].append(formula)

            ppm = self.calculate_ppm(formula, mod, exper, charge)
            self.data['ppm'].append(ppm)


class ProteomeDiscovererBase(MatchedPeptideBase, ProteomeDiscovererUtils):
    '''Base class of the Proteome Discoverer parser'''

    def __init__(self, source):
        super(ProteomeDiscovererBase, self).__init__(source)

        logger.Logging.info("Initializing base class for "
            "Proteome Discoverer....")

        self.fragments = self.worker.modifications['fragments']
        self.engine = get_engine(self.data)

        # self.matched = self.get_matched("proteome_discoverer", "1.3SQLite")
        # self.scoring = self.matched['scoring']

    def store_search(self):
        '''Only has the raw file name, which will be assumed to be project'''

        fraction = None
        if self.data['fraction']:
            fraction = self.data['fraction'][0]

        self.data['project'] = fraction
        self.data['search'] = None
