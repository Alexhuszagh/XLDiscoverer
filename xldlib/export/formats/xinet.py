'''
    Export/Formats/XiNet
    ____________________

    Writer for the crosslink CSV format used by xiNET, a crosslinker
    viewer software for generating crosslink maps:
        http://crosslinkviewer.org/

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

# HELPERS
# -------


def removeheader(string):
    '''
    Removes residue header from the joined residues and positions,
    enabling the exact positions to be determined.
    :
        string --  '{0}{1}'.format(res, pos) string
    '''

    if ':' in string:
        return string[string.find(':')+1:]
    else:
        return string[1:]


def formathierarchical(remainder):
    '''
    Processes and removes the residue headers from mods written
    in the hierarchical format.
    '''

    raise NotImplementedError

def formatflattened(remainder):
    '''
    Processes and removes the residue headers from mods written
    in the flattened format.
            residues joined in a Protein Prospector format
    '''

    split = remainder.split('|')
    for item in split:
        joined = '&'.join(removeheader(i) for i in item.split('&'))
        yield joined


def formatuncertain(remainder):
    '''
    Processes the uncertain crosslinker positions, depending on
    whether they were joined with a flattened or hierarchical format.
    :
        remainder -- res:pos values for crosslinker modified
            residues joined in a Protein Prospector format
    '''

    if defaults.DEFAULTS['write_hierarchical_modifications']:
        return formathierarchical(remainder)
    else:
        return '|'.join(formatflattened(remainder))


def formatcertain(certain):
    '''
    Processes the certain crosslinker positions within the
    crosslink position list of '{0}{1}'.format(res, pos) strings,
    '''

    return (removeheader(i) for i in certain)


def formatpositions(fragmentpositions):
    '''Removes the residue prefix for each xl_pos.'''

    for position in fragmentpositions:
        certain = position.split(';')
        remainder = certain.pop(-1)

        for position in formatcertain(certain):
            yield position
        yield formatuncertain(remainder)


# WRITER
# ------


@logger.init('spreadsheet', 'DEBUG')
class ToXiNet(base.BaseObject):
    '''Core writer for XiNet-like formats'''

    def __init__(self, row):
        super(ToXiNet, self).__init__()

        self.row = row

    def __call__(self, index, fragmentpositions):
        '''On start'''

        xinet = []
        xinet.append(self.formatscores(index))

        for row in self.row.data.getcolumn(index, ('id', 'preferred')):
            xinet.append(u'sp|{0}|{1}'.format(*row))

        xinet += list(formatpositions(fragmentpositions))
        return ''.join(xinet)

    #   FORMATTERS

    def formatscores(self, index):
        '''Returns the XiNet formatted scores for link filtering'''

        scores = self.row.data.getcolumn(index, 'score')
        return '{0:.2f}'.format(sum(scores) / len(index))
