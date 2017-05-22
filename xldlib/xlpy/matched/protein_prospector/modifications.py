'''
    XlPy/Matched/Protein_Prospector/modifications
    _____________________________________________

    Parses the outputted mod strings frp.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

    Process:
        -- Delimiters:
            Basic:
                ';'   separates different mods, where each separated segment
                always occurs (and).
            Differential Mod Composition:
                '||'  separates different mod compositions. Either instance
                occurs (or) for everything after the ';'.
            Differential Mod Position:
                 -- Hierarchical/Flattened formats
                '&'   separates multiple combinations within a given mod
                composition.
                '@'   separates mod name and positions.
    Filters:
        -- N-term:
            Problem: Peptide N-term sequences can be falsely assigned.
                N-term should be protein N-term, not peptide N-term.
            Solution: If start != 1 and residue reactivity
            is not 'K' (free-amine), then a false ID.
                -- Procedure:
                    If certain mod, reject mod list
                    If uncertain, reject uncertain list
        -- C-term
            Problem: Same as above, only C-terminal
            Solution: Same as above, only with 'D,E' rather than 'K'
'''

# load modules
from xldlib import exception
from xldlib.definitions import re, ZIP
from xldlib.objects import matched
from xldlib.qt.objects import base
from xldlib.utils import logger

from . import hierarchical


# REGEXES
# -------

NUMBER = re.compile(r'-?[0-9]*\.?[0-9]+')


# HELPERS
# -------


@logger.init('matched', 'DEBUG')
class CheckTermini(base.BaseObject):
    '''Helper class which identifies false modification termini'''

    def __init__(self, engine):
        super(CheckTermini, self).__init__()

        self.nterm = engine.defaults.nterm
        self.engine_modifications = engine.defaults.modifications

        source = self.app.discovererthread
        self.source_modifications = source.parameters.modifications

    @logger.except_error(IndexError)
    def __call__(self, modname, position, modification):
        '''Returns whether the modification is a false terminus'''

        if position == self.nterm:
            # check all modifications to see if any are fragments
            # don't worry about splitting concatenated mods, since
            # the this is a simple check
            for name in modname.split('+'):
                id_ = self.engine_modifications[name][0]
                db_modification = self.source_modifications[id_]
                if db_modification.fragment:
                    residue = modification.peptide[0]

                    if not (residue == 'K' or modification.start == 1):
                        raise exception.ModificationError


@logger.init('matched', 'DEBUG')
class FilterModificationComposition(base.BaseObject):
    '''
    Helper class which selects the best possible modification
    composition to continue with the crosslink discovery.
    '''

    # WEIGHTING
    # ---------
    crosslinker_weight = -1

    def __init__(self):
        super(FilterModificationComposition, self).__init__()

        source = self.app.discovererthread
        self.fragments = source.parameters.fragments

    def __call__(self, string):
        '''Returns the most weight of the mod string (lower is better)'''

        weight = []
        modifications = string.split('@')[0].split('&')
        for name in modifications:
            if name in self.fragments:
                weight.append(1 - self.crosslinker_weight)
            else:
                weight.append(1)

        return sum(weight)


# PARSERS
# -------


@logger.init('matched', 'DEBUG')
class ModificationBase(base.BaseObject):
    '''
    Base modification object which forms the basis of the flattened,
    hierarchical and default parsers
    '''

    def __init__(self, row):
        super(ModificationBase, self).__init__()

        self.engine = row.engines['matched']
        self.checktermini = CheckTermini(self.engine)

    #     PARSERS

    def parse_certain(self, string, modification):
        '''Parses a certain modification, which consists of name@pos pairs'''

        name, position = string.split('@')
        # remove the uncertainty from the position
        position = position.split('=')[0]

        if name == self.engine.defaults.neutralloss:
            return float(position)
        elif position == self.engine.defaults.neutralloss:
            return float(name)
        else:
            return self._modchecker(name, position, modification)

    #     HELPERS

    def _modchecker(self, name, position, modification):
        '''
        Checks the following criteria for the modification:
            No false termini
            Removes any neutral losses
        '''

        if NUMBER.match(name):
            return float(name)

        elif position.isdigit():
            position = int(position)
        else:
            self.checktermini(name, position, modification)

        return name, position

    def _add_certain(self, modification, value):
        '''Adds a certain modification to the holder'''

        if isinstance(value, float):
            modification.neutralloss += value
        else:
            self.__addname(modification.certain, *value)

    def _add_uncertain(self, modification, uncertain, value, index):
        '''Adds an uncertain modification to the holder'''

        if isinstance(value, float):
            if not index:
                # only add for the first combination
                modification.neutralloss += value
        else:
            self.__addname(uncertain, *value)

    @staticmethod
    def __addname(holder, names, position):
        '''Adds a name to the crosslinker modification holder'''

        # break concatenated mods
        for name in names.split('+'):
            holder[name].append(position)


class Flattened(ModificationBase):
    '''
    Parses flattened modifications, the old format for Protein
    Prospector.
        Ex: "Phospho@14&Phospho@15|Phospho@15&Phospho@16|"
            "Phospho@14&Phospho@16"
    '''

    def __call__(self, string, modification):
        '''Parses the modification position from the flattened format'''

        falsetermini = []
        if string:
            combinations = string.split('|')
            for index, combination in enumerate(combinations):
                bool_ = self.setposition(index, combination, modification)
                falsetermini.append(bool_)

        if all(falsetermini) & bool(falsetermini):
            raise exception.ModificationError

    #     SETTERS

    def setposition(self, index, combination, modification):
        '''Sets the positions for each of the modific'''

        uncertain = matched.ModificationDict()
        try:
            for combination in combination.split('&'):
                value = self.parse_certain(combination, modification)
                self._add_uncertain(modification, uncertain, value, index)

            # for uniqueness, check if already added
            if uncertain not in modification.uncertain:
                modification.uncertain.append(uncertain)

        except exception.ModificationError:
            return True
        return False


class Hierarchical(ModificationBase):
    '''
    Parses hierarchical modifications, the new format for Protein
    Prospector.
        Ex: "Deamidated&Deamidated@((1&(13|18|22))|(13&(18|22)))"
    '''

    def __call__(self, string, modification):
        '''Parses the modification position from the nested format'''

        falsetermini = []
        if string:
            names, positions = string.split('@')
            names = names.split('&')
            positions = hierarchical.flatten(positions)

            for index, position in enumerate(positions):
                bool_ = self.setposition(names, position, index, modification)
                falsetermini.append(bool_)

        if all(falsetermini) & bool(falsetermini):
            raise exception.ModificationError

    #     SETTERS

    def setposition(self, names, positions, index, modification):
        '''Stores a singular position for the modification'''

        positions = self.getpositions(positions)
        try:
            uncertain = matched.ModificationDict()

            for name, position in ZIP(names, positions):
                value = self._modchecker(name, position, modification)
                self._add_uncertain(modification, uncertain, value, index)

            # for uniqueness, check if already added
            if uncertain not in modification.uncertain:
                modification.uncertain.append(uncertain)

        except exception.ModificationError:
            return True
        return False

    #     GETTERS

    @staticmethod
    def getpositions(string):
        '''Returns the split and certainty-removed positions'''

        positions = string.split('&')
        return [i.split('=')[0] for i in positions]


# MAIN PARSER
# -----------


@logger.init('matched', 'DEBUG')
class ModificationParser(ModificationBase):
    '''
    Core object which parses a list of mods in a Protein Prospector
    mod format
    '''

    def __init__(self, row):
        super(ModificationParser, self).__init__(row)

        self.error = False

        self.filter = FilterModificationComposition()
        self.flattened = Flattened(row)
        self.hierarchical = Hierarchical(row)

    def __call__(self, modification):
        '''Parses the modification and adds it to the mod data'''

        if not modification.string:
            return

        self._checktruncated(modification.string)

        try:
            certain_strings = modification.string.split(';')
            remainder = certain_strings.pop(-1)

            self.processcertain(certain_strings, modification)
            self.processuncertain(remainder, modification)

        # uncaught mod error, which means false certain nterm/cterm pos
        # or all uncertain possibilities contain false nterm/cterm pos
        except exception.ModificationError:
            # delete from list and return null
            modification.certain.clear()
            del modification.uncertain[:]

        self.sort(modification)

    #    PROCESSORS

    def processcertain(self, certain_strings, modification):
        '''Iteratively processes all the certain strings'''

        for string in certain_strings:
            value = self.parse_certain(string, modification)
            self._add_certain(modification, value)

    def processuncertain(self, string, modification):
        '''
        Parses an certain modification, which can have a lot of intricate,
        confusing delimiters and hierarchies.
        '''

        string = min(string.split('||'), key=self.filter)

        # just a trailing modification, a normal certain modification
        if not any(i in string for i in {'|', '&'}) and string.count('@') == 1:
            self.processcertain([string], modification)

        elif string.count('@') == 1:
            self.hierarchical(string, modification)

        else:
            self.flattened(string, modification)

    def sort(self, modification):
        '''Sorts the certain and uncertain mod entries to avoid redundancy'''

        for positions in modification.certain.values():
            positions.sort(key=self.engine.key)

        for uncertain in modification.uncertain:
            for positions in uncertain.values():
                positions.sort(key=self.engine.key)

    #     HELPERS

    def _checktruncated(self, string):
        '''
        Checks whether a modification was truncated by a Protein
        Prospector bug, present around the 5.13.x versions.
        '''

        if not self.error and (string[-1] == ';' or ';||' in string):
            self.error = True

            source = self.app.discovererthread
            source.message.emit(exception.CODES['009'], "green", False)
