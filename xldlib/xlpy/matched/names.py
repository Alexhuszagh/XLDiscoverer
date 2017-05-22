'''
    XlPy/matched/names
    __________________

    Sets the preferred name for the protein with the following precedence
    :
        User Defined > Gene Name > Mnemonic / UniProt ID

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op

from xldlib.onstart.main import APP
from xldlib.utils import logger
from xldlib.xlpy import wrappers


# PUBLIC
# ------


def preferred_name(source, uniprotid, mappings):
    '''Returns the preferred name, if found, for the UniProt ID'''

    for obj in mappings:
        if uniprotid in obj:
            return _namechecker(obj[uniprotid])
    return uniprotid


@logger.call('matched', 'debug')
@wrappers.threadprogress(20, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Adding preferred protein names...")
def addnames():
    '''
    Calculates the formula for each of the modification/peptide pairs,
    ignoring all crosslinker modifications.
    '''

    source = APP.discovererthread
    named = source.proteins.get_lookup('Named', 'Name')
    proteins = source.proteins.get_lookup('Proteins', 'Name')

    for row in source.files:
        for uniprotid, in row.data.iterrows(['id']):
            name = preferred_name(source, uniprotid, (named, proteins))
            row.data['matched']['preferred'].append(name)


# PRIVATE
# -------


def _namechecker(name, delimiter=';'):
    return name.split(delimiter)[0]
