'''
    XlPy/matched/formula
    ____________________

    Calculates the base formula (without crosslinker fragments) from
    the peptide sequence and mod composition for each peptide ID.

    Crosslinker fragments are ignored since they do not correspond
    to the linked peptide with the intact, cross-linker bridge.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
import operator as op

from xldlib.onstart.main import APP
from xldlib.utils import logger, masstools
from xldlib.xlpy import wrappers


# DATA PROCESSING
# ---------------


@logger.call('matched', 'debug')
@wrappers.threadprogress(15, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Calculating peptide formulas...")
def calculateformulas(columns=('peptide', 'modifications')):
    '''
    Calculates the formula for each of the modification/peptide pairs,
    ignoring all crosslinker modifications.
    '''

    source = APP.discovererthread

    for row in source.files:
        engine = row.engines['matched']
        for peptide, mod in row.data.iterrows(columns):
            formula = masstools.getpeptideformula(peptide, mod, engine)
            row.data['matched']['formula'].append(formula)
