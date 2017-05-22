'''
    XlPy/matched/PepXML/mascot
    __________________________

    Definitions for processing pepXML files to the matched PyTables
    format from Mascot.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
import os

from collections import defaultdict

from xldlib.chemical import building_blocks
from xldlib.objects import matched
from xldlib.qt.objects import base
from xldlib.utils import logger, masstools

from .. import scan_titles


# CONSTANTS
# ---------

TERMINI = (
    'mod_nterm_mass',
    'mod_cterm_mass'
)

HYDROGEN_MASS = building_blocks.ELEMENTS['H'].isotopes[1].mass


# HELPERS
# -------


def gettype(masskey):
    '''gettype("mass") -> mass'''

    if masskey == 'mass':
        return masskey
    else:
        # terminal mods use massdiff
        return 'massdiff'


def getposition(attrs, masskey):
    '''Returns the modification position relative to the peptide'''

    if masskey == 'mass':
        return int(attrs['position'])
    elif masskey == 'mod_nterm_mass':
        return 'nterm'
    elif masskey == 'mod_cterm_mass':
        return 'cterm'


@logger.init('matched', 'DEBUG')
class Modifications(base.BaseObject):
    '''Modifications custom handler for pepXML formats'''

    # ROUNDING
    # --------
    precision = 4

    def __init__(self):
        super(Modifications, self).__init__()

        self.masses = defaultdict(dict)

    #     HANDLERS

    def store(self, attrs):
        '''Stores the modification masses for later modification parsing'''

        # stored for I believe solely internal modifications
        name = attrs['description']
        mass = self._masskey(attrs["mass"])
        self.masses['mass'][mass] = name

        # stored for I believe solely terminal modifications
        massdiff = self._masskey(attrs["massdiff"], adjust=HYDROGEN_MASS)
        self.masses['massdiff'][massdiff] = name


    #     GETTERS

    def getmodification(self, attrs, masskey):
        '''Returns the modification name from the XML attrs'''

        mass = self._masskey(attrs[masskey])
        modificationtype = gettype(masskey)
        return self.masses[modificationtype][mass]

    #     HELPERS

    def _masskey(self, mass, adjust=0):
        '''
        Returns a unique mass key for the modifications, since the pepXML
        specs do not all use the same mass accuracy for mods.
        '''

        return str(round(float(mass) + adjust, self.precision))


# NODES
# -----


@logger.init('matched', 'DEBUG')
class Start(base.BaseObject):
    '''Utilities for parsing XML start elements'''

    def __init__(self):
        super(Start, self).__init__()

        self.modifications = Modifications()
        self.titleformatter = scan_titles.TitleFormatter()

    #     HANDLERS

    def fraction(self, attrs):
        '''Handler for the <search_summary> node of the pepXML file'''

        self._fraction = os.path.basename(attrs['base_name'])

    def scan(self, attrs):
        '''Initializes the scan data and sets base attributes'''

        title = attrs['spectrum']
        match = self.titleformatter(title)

        num = int(match.group('num'))
        self._scan = matched.Scan(num=num, fraction=self._fraction)
        self._scan['z'] = charge = int(attrs.get('assumed_charge', 1))
        # calculate m/z
        neutral_mass = float(attrs['precursor_neutral_mass'])
        self._scan['mz'] = masstools.mz(neutral_mass, charge, 0)

    def hit(self, attrs):
        '''Processes an individual hit from various candidates'''

        rank = int(attrs['hit_rank'])
        hit = self._scan.set_hit(rank)

        hit['peptide'] = attrs['peptide']
        hit['id'] = attrs['protein'].split('|')[0]
        hit['name'] = attrs['protein_descr']
        # calculate ppm
        massdiff = float(attrs['massdiff'])
        hit['ppm'] = (massdiff / self._scan['mz']) * 1e6

    def score(self, attrs):
        '''Processes the score values from a search hit'''

        hit = self._scan['hits'][-1]
        if attrs['name'] == "expect":
            # pep_expect is not the p-value, or Expectation Value, it is
            # the number of hits that would occur above it by chance at pep
            # hit['ev'] = float(attrs["value"])
            pass

        if attrs['name'] == "ionscore":
            hit['score'] = score = float(attrs["value"])
            hit['ev'] = 10 ** (-score/10)

    def terminal(self, attrs):
        '''Processes each terminal modification from the element'''

        hit = self._scan['hits'][-1]

        masskeys = (i for i in TERMINI if i in attrs)
        for masskey in masskeys:
            name = self.modifications.getmodification(attrs, masskey)
            position = getposition(attrs, masskey)

            hit['modifications']['certain'][name].append(position)

    def internal(self, attrs):
        '''Processes each internal modification from the element'''

        name = self.modifications.getmodification(attrs, 'mass')
        position = getposition(attrs, 'mass')

        hit = self._scan['hits'][-1]
        hit['modifications']['certain'][name].append(position)


@logger.init('matched', 'DEBUG')
class End(base.BaseObject):
    '''Utilities for parsing XML end elements'''

    def __init__(self):
        super(End, self).__init__()
