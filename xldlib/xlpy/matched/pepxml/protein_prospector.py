'''
    XlPy/matched/PepXML/protein_prospector
    ______________________________________

    Definitions for processing pepXML files to the matched PyTables
    format from Protein Prospector.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
from collections import defaultdict

from xldlib.objects import matched
from xldlib.qt.objects import base
from xldlib.utils import masstools


# CONSTANTS
# ---------

TERMINI = (
    'mod_nterm_mass',
    'mod_cterm_mass'
)


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
        massdiff = self._masskey(attrs["massdiff"])
        self.masses['massdiff'][massdiff] = name

    #     GETTERS

    def getmodification(self, attrs, masskey):
        '''Returns the modification name from the XML attrs'''

        mass = self._masskey(attrs[masskey])
        modificationtype = gettype(masskey)
        return self.masses[modificationtype][mass]

    #     HELPERS

    def _masskey(self, mass):
        '''
        Returns a unique mass key for the modifications, since the pepXML
        specs do not all use the same mass accuracy for mods.
        '''

        return str(round(float(mass), self.precision))


# NODES
# -----


class Start(base.BaseObject):
    '''Utilities for parsing XML start elements'''

    def __init__(self):
        super(Start, self).__init__()

        self.modifications = Modifications()

    #     HANDLERS

    def fraction(self, attrs):
        '''Handler for the <search_summary> node of the pepXML file'''

        self._fraction = attrs['base_name']

    def scan(self, attrs):
        '''Initializes the scan data and sets base attributes'''

        num = int(attrs['start_scan'])
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
        hit['id'] = id_ = attrs['protein'].split('|')[1]
        hit['name'] = attrs['protein_descr']
        # calculate ppm
        massdiff = float(attrs['massdiff'])
        hit['ppm'] = (massdiff / self._scan['mz']) * 1e6

    def score(self, attrs):
        '''Processes the score values from a search hit'''

        hit = self._scan['hits'][-1]
        if attrs['name'] == "expect":
            hit['ev'] = float(attrs["value"])
        elif attrs['name'] == "ion_score":
            hit['score'] = float(attrs["value"])

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


class End(base.BaseObject):
    '''Utilities for parsing XML end elements'''

    def __init__(self):
        super(End, self).__init__()
