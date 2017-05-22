'''
    Export/Formats/modifications
    ____________________________

    Processing for post-translational modifications and peptides
    for easily-to-visualize exports.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import six

from xldlib.definitions import re, ZIP
from xldlib.general import sequence
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import decorators, logger


__all__ = [
    'ModificationFormatter',
    'ProteinModifications',
    'LabeledProteinModifications',
    'ModificationsInPeptide',
    'LabeledModificationsInPeptide'
]


# FORMATTING
# ----------


@logger.init('spreadsheet', 'DEBUG')
class ModificationFormatter(base.BaseObject):
    '''Processes modification positions to a Protein Prospector-like output'''

    # FORMATTING
    # ----------
    _flattened = '{0}@{1}'

    def __init__(self, engine):
        super(ModificationFormatter, self).__init__()

        self.engine = engine

    #    FORMATTERS

    def __call__(self, name, positions, start):
        '''Returns a flattened protein mod format from a name/positions set'''

        for position in positions:
            position = self.getproteinposition(position, start)
            yield self._flattened.format(name, position)

    def one(self, uncertain, start):
        '''Adds a singular uncertain mod in the flattened format.'''

        nested = (i for item in uncertain for i in item.values())
        unnested = (i for item in nested for i in item)
        sorted_ = sorted(set(unnested), key=self.engine.key)

        # process n-/c-terms and adjust relative to protein sequence
        adjusted = (self.getproteinposition(i, start) for i in sorted_)
        position = '|'.join(adjusted)
        name = next(iter(uncertain[0].keys()))

        return self._flattened.format(name, position)

    def hierarchical(self, uncertain, start):
        '''Adds the uncertain modifications in a hierarchical format'''

        raise NotImplementedError

    def flattened(self, uncertain, start):
        '''Adds the uncertain modifications in a flattened format'''

        flattened = ('&'.join(i) for i in self.getflattened(uncertain, start))
        return '|'.join(sequence.uniquer(flattened))

    #    GETTERS

    @staticmethod
    def getproteinposition(position, start):
        '''
        Processes a mod position to the "writer" value and orients
        relative to protein start sequence.
        '''

        if isinstance(position, six.integer_types):
            position = str(position + start - 1)

        return position

    def getflattened(self, uncertain, start):
        '''Returns a generator with all the uncertain positions'''

        for modification_dict in uncertain:
            for name, positions in modification_dict.items():
                yield self(name, positions, start)


# PROTEIN MODIFICATIONS
# ---------------------


@logger.init('spreadsheet', 'DEBUG')
class ProteinModifications(base.BaseObject):
    '''
    Creates the protein modifications in a report format similar to
    Protein Prospector
        -> "XL:A-Alkene@7;Carbamidomethyl@11"
    '''

    # FORMATTING
    # ----------
    sep = ';'

    def __init__(self, row):
        super(ProteinModifications, self).__init__()

        self.row = row
        self.formatter = ModificationFormatter(row.engines['matched'])

    @logger.call('spreadsheet', 'debug')
    def __call__(self, indexes):
        '''Converts the datatable and indexes -> "mod@position"'''

        if isinstance(indexes, tuple) and hasattr(indexes, "_fields"):
            indexes = indexes.index

        for index in indexes:
            yield self.sep.join(self.getproteinmods(index))

    #    GETTERS

    def getproteinmods(self, index, keys=('modifications', 'start')):
        '''Gets the protein mods for the given index'''

        modification, start = self.row.data.getrow(index, keys)

        if defaults.DEFAULTS['concatenate_hybrid_modifications']:
            modification = modification.concatenate()

        positions = list(self.getcertain(modification, start))
        if modification['uncertain']:
            positions.append(self.getuncertain(modification, start))

        return positions

    def getcertain(self, modification, start):
        '''Returns the protein modifications from the certain mods'''

        for name, positions in modification['certain'].items():
            for string in self.formatter(name, positions, start):
                yield string

    def getuncertain(self, modification, start):
        '''Returns the protein modifications from the uncertain mods'''

        uncertain = modification['uncertain']
        if all(len(i) == 1 for i in uncertain):
            return self.formatter.one(uncertain, start)

        elif defaults.DEFAULTS['write_hierarchical_modifications']:
            return self.formatter.hierarchical(uncertain, start)

        else:
            return self.formatter.flattened(uncertain, start)


class LabeledProteinModifications(ProteinModifications):
    '''
    Subclass to handle the differing modifications with isotope-labeled
    theoretical peptide pairs.
    '''

    @decorators.overloaded
    def __call__(self, label, spreadsheet):
        '''Processes the labeled modifications for the labeled crosslinks'''

        zipped = ZIP(label.modifications, spreadsheet.getstart())
        for modification, start in zipped:
            yield self.sep.join(self.getproteinmods(modification, start))

    #    GETTERS

    def getproteinmods(self, modification, start):
        '''Gets the protein mods from the manually specified data'''

        if defaults.DEFAULTS['concatenate_hybrid_modifications']:
            modification = modification.concatenate()

        positions = list(self.getcertain(modification, start))
        if modification['uncertain']:
            positions.append(self.getuncertain(modification, start))

        return positions


# REGEXP
# ------
LETTERS = re.compile('([A-Z]{2})')
PARENTHESES = re.compile(r'(\))')

# STRINGS
# -------
TERMINUS = '{0}-{1}'
INTERNAL = '{0}({1}){2}'


# PEPTIDE-EMBEDDED MODIFICATIONS
# ------------------------------


@logger.init('spreadsheet', 'DEBUG')
class ModificationsInPeptide(base.BaseObject):
    '''Adds the given user mods to the target peptide sequence'''

    # ROUNDING
    # --------
    precision = 3

    def __init__(self, row, skyline=False):
        super(ModificationsInPeptide, self).__init__()

        self.row = row
        self.skyline = skyline

        self.engine = row.engines['matched']
        self.nterm = self.engine.defaults.nterm
        self.cterm = self.engine.defaults.cterm

    @logger.call('spreadsheet', 'debug')
    def __call__(self, indexes):
        '''Converts the datatable and indexes -> ['LKK(XL:A-Alkene)K']'''

        if isinstance(indexes, tuple) and hasattr(indexes, "_fields"):
            indexes = indexes.index

        for index in indexes:
            yield self.getformattedpeptide(index)

    #    GETTERS

    def getformattedpeptide(self, index):
        '''
        Adds the peptide modification positions for a given row
        and sorted modification positions
        '''

        row = self.row.data.getrow(index, asdict=True)
        length = len(row['peptide'])

        modpositions = self.getmodpositions(row['modifications'], length)
        for name, position in modpositions:
            if self.skyline:
                name = self.skyline(name)
            peptide = self.formatposition(row['peptide'], name, position)

        return self.formatneutralloss(row['modifications'], peptide)

    def getmodpositions(self, modification, length):
        '''
        Returns a tupleized pair of (name, pos) mods sorted for pos
        and then concatenated
        '''

        termini = self.engine.totermini(length)
        modification = modification.unpack().concatenate(termini, append=False)
        concatenated = list(modification.items())

        # sort reverse to prevent reindexing
        concatenated.sort(key=lambda x: self.engine.key(x[1]), reverse=True)

        return concatenated

    #    FORMATTERS

    def formatposition(self, peptide, name, pos):
        '''
        Adds a single modification to the peptide from a modification name
        and position pair.
        '''

        if pos == self.cterm:
            # check Cterm first, since reversed order
            return TERMINUS.format(peptide, name)
        elif pos == self.nterm:
            return TERMINUS.format(name, peptide)
        else:
            return INTERNAL.format(peptide[:pos], name, peptide[pos:])

    def formatneutralloss(self, modification, peptide):
        '''
        Adds a neutral loss addition to the first position possible within
        the string.
        '''

        neutralloss = modification['neutralloss']
        if neutralloss:
            neutralloss = round(neutralloss, self.precision)
            match = LETTERS.search(peptide)

            if match:
                # position found with free space between letters
                index = match.start()
                peptide = self.formatposition(peptide, neutralloss, index + 1)

            else:
                # mod fully saturated, add (name+neutrallloss) to position
                repl = r'+{}\1'.format(neutralloss)
                peptide = PARENTHESES.sub(repl, peptide, count=1)

        return peptide


class LabeledModificationsInPeptide(ModificationsInPeptide):
    '''
    Subclass to handle the differing modifications with isotope-labeled
    theoretical peptide pairs.
    '''

    @decorators.overloaded
    def __call__(self, label, spreadsheet):
        '''Processes the labeled modifications for the labeled crosslinks'''

        zipped = ZIP(label.modifications, spreadsheet.getpeptide())
        for modification, peptide in zipped:
            yield self.getformattedpeptide(modification, peptide)

    #    GETTERS

    def getformattedpeptide(self, modification, peptide):
        '''
        Adds the peptide modification positions for a given row
        and sorted modification positions
        '''

        length = len(peptide)
        positions = self.getmodpositions(modification, length)

        for name, position in positions:
            if self.skyline:
                name = self.skyline(name)
            peptide = self.formatposition(peptide, name, position)

        return self.formatneutralloss(modification, peptide)
