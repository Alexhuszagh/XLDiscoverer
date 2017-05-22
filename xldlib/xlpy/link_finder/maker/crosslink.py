'''
    XlPy/Link_Finder/maker/crosslink
    ________________________________

    Tools to compile the link data into a minimal tuple for
    later data processing.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from collections import namedtuple

from xldlib.definitions import partial
from xldlib.general import sequence
from xldlib.qt.objects import base
from xldlib.resources import chemical_defs
from xldlib.resources.parameters import defaults, reports
from xldlib.utils import logger, modtools


# DATA
# ----

BOOLSTRINGS = {
    True: 'T',
    False: ''
}


# HELPERS
# -------


def localtoglobal(link, localindexes):
    '''
    Converts the local indexes within the link to indexes for the matched
    data.
    '''

    return [link.scan.indexer.filtered[i] for i in localindexes]


def getcrosslinktype(link, linkname, indexes):
    '''Finds the associated cross-link type based on the bridging modes'''

    if linkname == 'Incomplete' and len(indexes) > 1:
        return 'multilink'

    elif len(indexes) > 1:
        return 'interlink'

    else:
        if link.ends.isdeadend:
            return 'deadend'
        else:
            return 'intralink'


# DATA
# ----

TYPES = (
    'Intersubunit',
    'Intrasubunit',
    'Single',
    'Double',
    'Deadend',
    'Intralink',
    'Ambiguous'
)


# OBJECTS
# -------


class LinkTypes(namedtuple("LinkTypes", "intersubunit "
    "intrasubunit single double deadend intralink ambiguous")):

    def __new__(cls, *args):
        args = (BOOLSTRINGS[i] for i in args)
        return super(LinkTypes, cls).__new__(cls, *args)

    def tospreadsheet(self):
        '''Returns the current data to a dict with conventional keys'''

        return {i: getattr(self, i.lower()) for i in TYPES}


@sequence.serializable("SequencedCrosslink")
class Link(namedtuple("Link", "index name "
    "type ppm ppm_set ends mass ambiguous "
    "crosslinker label frozen")):

    # ROUNDING
    # --------
    precision = 3
    _round = partial(round, ndigits=precision)

    @logger.call('xlpy', 'debug')
    def totypes(self, intrasubunit):
        '''totypes() -> LinkTypes(intersubunit="T", ...)'''

        double = self.type == reports.LINKTYPES['interlink']

        intersubunit = (not intrasubunit) & double
        intrasubunit = intrasubunit & double

        return LinkTypes(
            intersubunit,
            intrasubunit,
            True,
            double,
            self.type == reports.LINKTYPES['deadend'],
            self.type == reports.LINKTYPES['intralink'],
            self.ambiguous)

    def tospreadsheet(self):
        '''Returns the current data to a dict with conventional keys'''

        return {
            'Cross-Linker': self.getcrosslinkername(),
            'Cross-Link Number': self.ends.number,
            'Missing Mass': self.getmasserror(),
            'MS2 PPM': self.getppm(),
            'MS2 PPM Corrected': self.getcorrectedppm()
        }

    #    GETTERS

    @logger.call('xlpy', 'debug')
    def getcrosslinkername(self):
        '''Returns the crosslinker name with any isotope labels added'''

        crosslinker = chemical_defs.CROSSLINKERS[self.crosslinker]
        if self.label:
            return u'{0} {1}'.format(self.label, crosslinker.name)
        else:
            return crosslinker.name

    def getmasserror(self):
        return self._round(self.mass.error)

    def getppm(self):
        return self._round(self.ppm)

    @logger.call('xlpy', 'debug')
    def getcorrectedppm(self):
        '''0 -> ppm_corrected -> 2.261'''

        if self.ppm_set:
            return self._round(min(self.ppm_set, key=abs))
        else:
            return self._round(self.ppm)


@logger.init('xlpy', 'DEBUG')
class MakeLink(base.BaseObject):
    '''Object which makes link tuple instances for data storage'''

    def __init__(self, row, crosslinker):
        super(MakeLink, self).__init__()

        self.row = row
        self.crosslinker = crosslinker

        self._labeler = modtools.ModificationLabeler(row)

    def __call__(self, link, linkname, localindexes):
        '''Constructs the link tuple from the link data and type'''

        indexes = localtoglobal(link, localindexes)
        linktype = getcrosslinktype(link, linkname, indexes)

        return Link(
            indexes,
            reports.LINKNAMES[linkname],
            reports.LINKTYPES[linktype],
            link.ppm.base,
            link.ppm.set,
            link.ends,
            link.mass,
            self.getambiguous(link),
            self.crosslinker.id,
            self.getlabels(indexes, link.scan.modifications),
            None)

    #    GETTERS

    def getambiguous(self, link):
        '''
        Determines whether a link is ambiguous or not. Raises an
        AssertionError if the list is ambiguous, otherwise, returns fFlse.
        '''

        ambiguous = False
        for indexes in link.scan.indexer.group.values():
            for column in ('id', 'peptide'):
                values = self.row.data.getcolumn(indexes, column)
                value = next(values)
                ambiguous |= not all(i == value for i in values)

        return ambiguous

    def getlabels(self, indexes, modifications):
        '''
        Processes the crosslinker name with a series of isotopic
        labels if configured to do so. Just calls label_crosslinker
        to actually add the name and then returns it to be stored.
        :
            index -- list of indexes for values in data sublists
        '''

        if defaults.DEFAULTS['add_isotopic_labels']:
            return self._labeler(modifications)
        else:
            return ''
