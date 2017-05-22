'''
    XlPy/matched/positions
    ______________________

    Indexes the peptide position within the protein sequence as well
    as limits for biologically relevant cut sites (proteolytic enzyme
    MUST be specified) for uncleaved moficiations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import defaultdict

from xldlib import exception
from xldlib.chemical import proteins
from xldlib.definitions import re
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger
from xldlib.xlpy import wrappers

from . import remove

# HELPERS
# -------


def get_cterm(protease):
    '''
    Returns a regex pattern matching the N-terminal side of the
    peptide since the cut-specificity N-terminal is unknown if it
    cuts C-terminal of the cut site.
    '''

    cut = ''.join(protease.enzyme.cut)
    # add in setting for N-term or N-term w/ Met-loss due to
    # high percentage of Methionine loss
    cut_sites = r'(?P<cut>^|^M|[{}])'.format(cut)
    cut_regex = cut_sites + r'{peptide}'

    return cut_regex


def get_nterm(protease):
    '''
    Returns a regex pattern matching the C-terminal side of the
    peptide since the cut-specificity C-terminal is unknown if it
    cuts N-terminal of the cut site.
    '''

    cut = ''.join(protease.enzyme.cut)
    cut_sites = r'(?:$|[{0}])'.format(cut)
    # have a 0-length match group 1 in front
    cut_regex = r'(?P<cut>){peptide}' + cut_sites

    return cut_regex


def getsequences(proteins):
    '''Returns an hashmap of ids to sequences from records in the table'''

    sqlquery = "SELECT UniProtID, Sequence FROM Proteins"
    iterable = proteins.fetchiter(sqlquery)
    return {i.value(0): i.value(1) for i in iterable}


@logger.init('matched', 'DEBUG')
class PeptideStart(base.BaseObject):
    '''Calculates the peptide starts for a given data holder'''

    # DEFAULTS
    # --------
    # Protein 1-indexing
    offset = 1

    def __init__(self, parent, sequences):
        super(PeptideStart, self).__init__(parent)

        self.sequences = sequences

    @logger.call('matched', 'debug')
    def __call__(self, row, protease):
        '''Add all the starts to the current data holder'''

        if protease.enzyme.side == proteins.TERMINI['N']:
            cut = get_nterm(protease)
        else:
            cut = get_cterm(protease)
        row.data['matched']['start'][:] = self.getstarts(row, cut)

    def getstarts(self, row, cut_regex):
        '''Sequentially indexes the start positions within the sequence'''

        for rowdata in row.data.iterrows(('peptide', 'id'), asdict=True):
            try:
                sequence = self.sequences[rowdata['id']]
                regex = cut_regex.format(peptide=rowdata['peptide'])
                match = re.search(regex, sequence)
                offset = self.offset + len(match.group('cut'))

                yield match.start() + offset

            except (KeyError, AttributeError):
                # sequence does not match determined, or sequence no in db
                yield float("nan")


KEYS = (
    'start',
    'modifications',
    'id',
    'peptide'
)


@logger.init('matched', 'DEBUG')
class FilterCleaved(base.BaseObject):
    '''
    Filters false N-/C-term cross-linker and standard modifications.
    For each modification, associates a cleaved or uncleaved status
    to it, with the default being uncleaved for cross-linker mods,
    and cleaved for standard mods. These can be edited in
    models/params/mods/.

    For each identified peptide, if the mod is an internal
    '''

    def __init__(self, parent, sequences):
        super(FilterCleaved, self).__init__(parent)

        self.sequences = sequences
        self.deleterows = []

        source = self.app.discovererthread
        self.fragments = source.parameters.fragments
        self.modifications = source.parameters.modifications

        self.setuncleaved()

    @logger.call('matched', 'debug')
    @remove.deleterows
    def __call__(self, row, protease):
        self.row = row
        self.finduncleaved(row, protease)

    #      SETTERS

    def setuncleaved(self):
        '''Creates a mapping structure so each fragment is a ref to the xler'''

        self.uncleaved = defaultdict(list)
        for fragment in self.fragments.values():
            if fragment.uncleaved:
                self.uncleaved[fragment.name].append(fragment)

    #      PUBLIC

    def finduncleaved(self, row, protease, keys=KEYS):
        '''Finds indexes to remove because of false terminal cross-linkers'''

        engine = row.engines['matched']
        for index, rowdata in enumerate(row.data.iterrows(keys, asdict=True)):
            if protease.enzyme.side == proteins.TERMINI['N']:
                toremove = self.checknterm(engine, rowdata)
            else:
                toremove = self.checkcterm(engine, rowdata)
            if toremove:
                self.deleterows.append(index)

    #      CHECKERS

    def checknterm(self, engine, rowdata):
        '''Checks whether any mods are N-Terminal within the sequence'''

        try:
            self.sequences[rowdata['id']]
            assert rowdata['start'] <= 1
        except (KeyError, AssertionError):
            # KeyError -> no sequence information on file
            # AssertionError -> not N-terminal peptide
            #   -> Filter uncleaved mods at peptide N-term

            positions = {0, 1, engine.defaults.nterm}
            return self.checktermini(engine, positions, rowdata)

    def checkcterm(self, engine, rowdata):
        '''Checks whether any mods are C-Terminal within the sequence'''

        try:
            length = len(self.sequences[rowdata['id']])
            assert rowdata['start'] + len(rowdata['peptide']) >= length

        except (KeyError, AssertionError):
            # KeyError -> no sequence information on file
            # AssertionError -> not C-terminal peptide
            #   -> Filter uncleaved mods at peptide C-term

            positions = {len(rowdata['peptide']), engine.defaults.cterm}
            return self.checktermini(engine, positions, rowdata)

    def checktermini(self, engine, positions, rowdata):
        '''Checks whether any modification are uncleaved and terminal'''

        mod = rowdata['modification']
        remove = self._checkcertain(engine, positions, mod['certain'])
        if not remove:
            remove = self._checkuncertain(engine, positions, mod['uncertain'])
        return remove

    def _checkcertain(self, engine, positions, certain):
        '''
        Checks whether there are any uncleaved mods in cleavage positions
        for the certain mods.
        '''

        for name, position in certain.items():
            if any(i in positions for i in position):
                if name in self.uncleaved:
                    return True
                else:
                    return self.modifications.isuncleaved(name, engine.name)

    def _checkuncertain(self, engine, positions, uncertain):
        '''
        Checks whether there are any uncleaved mods at cleavage positions
        for all uncertain mod permutations.
        '''

        remove = []
        for combination in uncertain:
            bool_ = self._checkcertain(engine, positions, combination)
            remove.append(bool_)

        # all([]) -> True, when means no uncertain, use & bool([])
        return all(remove) & bool(remove)


# POSITIONS
# ---------


@logger.init('matched', 'DEBUG')
class ProcessPeptidePositions(base.BaseObject):
    '''
    Process peptide positions, which includes the following tasks:
        1. Indexes the peptide start positions within a protein sequence,
        assuming peptide relative starts are turned off.
        Requires the following information:
            1. All unique identifiers (UniProt IDs or mnemonics) to
                acquire sequences, to pass as {id: sequence}
            2. Enzyme cut site prediction
        2. Filters false N-term and C-term modifications, assuming
        uncleaved mods.
    '''

    def __init__(self):
        super(ProcessPeptidePositions, self).__init__()

        self.relativestart = defaults.DEFAULTS['peptide_relative_start']

        source = self.app.discovererthread
        sequences = getsequences(source.proteins)

        self.starts = PeptideStart(self, sequences)
        self.filterer = FilterCleaved(self, sequences)

    @wrappers.warnonerror(KeyError, exception.CODES['025'])
    def __call__(self, row):
        '''On start'''

        protease = row.data.protease
        if protease is not None:
            if not self.relativestart and 'start' not in row.data['matched']:
                self.starts(row, protease)

            self.filterer(row, protease)
