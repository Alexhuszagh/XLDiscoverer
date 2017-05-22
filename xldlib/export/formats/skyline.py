'''
    Export/Formats/skyline
    ______________________

    Exports with internal modifications converted to masses in a
    format suitable for importation into Skyline.
        No affiliation with XLDiscoverer, original reference:
            10.1093/bioinformatics/btq054

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# load modules/submodules
import copy
import sys

from collections import Counter, defaultdict, namedtuple

from xldlib import chemical
from xldlib.definitions import re
from xldlib.qt.objects import base
from xldlib.utils import logger

from . import modifications


# CONSTANTS
# ---------
REPLACE = '[REPLACE]'
SKYLINE = r'\[CROSSLINKER(\+-?[0-9]+\.[0-9])?\]'

CROSSLINKER_POSITIVE = '[CROSSLINKER+{0}]'
CROSSLINKER_NEGATIVE = '[CROSSLINKER{0}]'
CROSSLINKER = '[CROSSLINKER]'

SKYLINE_POSITIVE = '[+{0}]'
SKYLINE_NEGATIVE = '[-{0}]'

# REGEXES
# -------
PARENTHESES = re.compile(r'\(|\)')
LETTERS = re.compile('([A-Z]{2})')
MASS_MODIFICATION = re.compile(r'(\[(?:\+|-)([0-9]*\.?[0-9]?)\])')


# HELPERS
# -------


def mappedresidues(deadends):
    '''Maps the CSV residue keys as values to each individual residue'''

    mapped = defaultdict(list)
    for key in deadends:
        for residue in key.split(','):
            mapped[residue].append(key)
    return mapped


def subtract_dict(d, other):
    '''Int subtracts a temp, abstract dict from a d'''

    d = d.copy()
    mapped = mappedresidues(d)

    for residue, value in other.items():
        keys = mapped[residue]
        for key in keys:
            if d[key] > 0:
                d[key] -= value
                break
        else:
            d[keys[0]] -= value

    return d


def replacement_string(mass):
    '''Converts the mass change into a string for Skyline importation'''

    # make replacement string
    if mass > 0:
        string = '[+{0}]'.format(mass)
    else:
        string = '[{0}]'.format(mass)
    return string


# OBJECTS
# -------

Position = namedtuple("Position", "name regexp")
Replacement = namedtuple("Replacement", "replaced "
    "reactivity counts bridge deadends ends")

POSITIONS = [
    Position('nterm', re.compile(SKYLINE + '-')),
    Position('cterm', re.compile('-' + SKYLINE)),
    Position('interior', re.compile(SKYLINE))
]


# REPLACER
# --------


class Replacer(base.BaseObject):
    '''
    Executes replacement events to convert "CROSSLINKER" -> "REPLACE"
    placeholders to allow the keeping of complicated bridging modes
    in the reported Skyline-formatted peptide.
    '''

    def __init__(self):
        super(Replacer, self).__init__()

        source = self.app.discovererthread
        self.crosslinkers = source.parameters.crosslinkers

    def __call__(self, linear, crosslink, crosslink_number):
        '''Replaces one bridge of the internal "CROSSLINKER" placeholders'''

        mass = 0
        replacement = self.get_crosslinker_replacement(crosslink)

        while sum(replacement.replaced.values()) < len(replacement.reactivity):
            for position in POSITIONS:
                value = self.check_replacement(linear, position, replacement)
                if value is not None:
                    linear = value[0]
                    mass += value[1]
                    break
            else:
                # positions can be exhausted for multilinks,
                # creating a never-ending loop
                break

            # if the linkends fall under crosslink_num,
            # the rest are singly bound deadends
            if sum(replacement.ends.link.values()) < crosslink_number:
                break

        # adjust the mass to add in the crosslinker fragments
        mass += sum(self.get_replacement_mass(replacement))
        mass += replacement.bridge
        return linear, mass

    def check_replacement(self, linear, position, replacement):
        '''Checks for a replace event and executes it if possible'''

        match = position.regexp.search(linear)
        if match is not None:
            residue = self.get_residue(position, linear, match, replacement)
            self.set_replace_residue(residue, replacement)
            return self.get_replacement(linear, match)

    #     SETTERS

    def set_replace_residue(self, residue, replacement):
        '''
        Attempts to set the residue and matched counts and link ends,
        since the PMF can return the CSV residues without specifying
        the actual point of modification ('D,E' rather than 'D'), which
        is specified during replacement.
        Need to adjust counts for proper CSV res in self and
        link_ends accordingly.
        '''

        try:
            replacement.replaced[residue] += 1

        except KeyError:
            if self.specific:
                raise

            values = {k: v for k, v in replacement.replaced.items()
                      if residue in k.split(',')}
            residue = min(values, key=values.get)
            replacement.replaced[residue] += 1

        replacement.ends.link[residue] -= 1

    #     GETTERS

    def get_crosslinker_replacement(self, crosslink):
        '''Returns the crosslinker reactivity'''

        replaced = {k: 0 for k in crosslink.ends.link}

        crosslinker = self.crosslinkers[crosslink.crosslinker]
        bridge = chemical.Molecule(crosslinker.bridge).mass
        deadends = [chemical.Molecule(i) for i in crosslinker.ends.deadend]
        counts = Counter(crosslinker.ends.aminoacid)

        return Replacement(replaced, crosslinker.ends.aminoacid, counts,
            bridge, deadends, crosslink.ends)

    def get_residue(self, position, *args):
        '''
        Returns the residue for corresponding adjusted to consider N-/
        C-terminal reactivities
            -> get_residue('LKEAR', <_sre.SRE_Match...>, 'nterm') -> 'K'
        '''

        if position.name == 'nterm':
            return 'K'
        elif position.name == 'cterm':
            return 'D'
        else:
            return self.get_residue_frompeptide(*args)

    def get_residue_frompeptide(self, linear, match, replacement):
        '''
        Extracts the residue fro, the peptide and checks the position,
        making educated guesses.
        '''

        index = match.start() - 1
        residue = linear[index]

        no_reactivity = any(residue == i for item in replacement.counts
            for i in item.split(','))

        if index == 0 and not no_reactivity:
            # then an N-terminal peptide
            return 'K'
        else:
            return residue

    def get_replacement(self, linear, match):
        '''
        Processes a replacement event and extracts the mass
        and the replacement sub for subsequent replacement.
        '''

        replace = match.group(0)
        mass = match.group(1) or 0

        return linear.replace(replace, REPLACE, 1), float(mass)

    def get_replacement_mass(self, replacement):
        '''
        Adjusts the crosslinker bridge mass based on the number
        of dead ends, those not linked to a peptide.
        '''

        deadends = subtract_dict(replacement.counts, replacement.replaced)

        for residue, count in deadends.items():
            # for each end not bound, add deadend mass
            # replacement.reactivity and deadends are CSV-separated residues
            index = [i for i, j in enumerate(replacement.reactivity)
                     if residue in j][0]

            yield replacement.deadends[index].mass * count


# FORMATTER
# ---------


@logger.init('spreadsheet', 'DEBUG')
class SkylineNameFormatter(base.BaseObject):
    '''
    Converts post-translational modification names to modification
    masses for importation into Skyline.
    '''

    # FORMATTING
    # ----------
    precision = 1

    def __init__(self, row):
        super(SkylineNameFormatter, self).__init__()

        self.row = row
        self.engine = row.engines['matched']

        source = self.app.discovererthread
        self.modifications = source.parameters.modifications

    def __call__(self, name, delimiter='+'):
        '''Returns the skyline formatted name for the modification'''

        atom_counts = chemical.Molecule()

        names = name.split(delimiter)
        modifications = self.getmodifications(names)
        crosslinkernumber = 0

        for modification in modifications:
            if not modification.fragment:
                atom_counts.update_formula(modification.formula)
            else:
                crosslinkernumber += 1

        return self.getskylinemass(atom_counts, crosslinkernumber)

    #     GETTERS

    def getmodifications(self, names):
        '''Returns a chemical_defs.Modification instance from the name'''

        for name in names:
            try:
                ids = self.engine.defaults.modifications.get(name)
                yield self.modifications[ids[0]]

            except TypeError:
                # Nonetype from .get(name), modifications is dict factory
                print("Modification not recognized: " + name, file=sys.stderr)

    def getskylinemass(self, atom_counts, crosslinkernumber):
        '''
        Formats atom counts to a string to be used by Skyline. Can
        handle any number of standard mods concatenated to a given
        crosslinker mod.
        '''

        if crosslinkernumber > 1:
            # check if more than 1 crosslinker at the same position
            # -- POTENTIAL BUG
            print("Unsupported crosslinking modification", file=sys.stderr)
            raise NotImplementedError("More than 1 fragment at a site")

        mass = round(atom_counts, self.precision)
        if mass > 0 and crosslinkernumber:
            return CROSSLINKER_POSITIVE.format(mass)
        elif mass > 0:
            return SKYLINE_POSITIVE.format(mass)
        elif mass < 0 and crosslinkernumber:
            return CROSSLINKER_NEGATIVE.format(mass)
        elif crosslinkernumber:
            return CROSSLINKER
        else:
            return SKYLINE_NEGATIVE.format(mass)


# SKYLINE WRITER
# --------------


@logger.init('spreadsheet', 'DEBUG')
class ToSkyline(base.BaseObject):
    '''
    Writes a linear peptide with Skyline-style modifications.
    >>> ToSkyline()() -> 'DLLHPSPEEEK[+158.0]RK'
    '''

    # FORMATTING
    # ----------
    precision = 1

    def __init__(self, row):
        super(ToSkyline, self).__init__()

        self.row = row

        self.format = SkylineNameFormatter(row)
        self.replacer = Replacer()
        self.moddata = modifications.ModificationsInPeptide(row, self.format)

    @logger.call('report', 'DEBUG')
    def __call__(self, crosslink):
        '''Converts the data into a linear peptide with mass modifications'''

        peptides = self.moddata(crosslink.index)
        peptides = (PARENTHESES.sub('', i) for i in peptides)
        linear = ''.join(peptides)

        linear = self.get_replaced_crosslinkers(linear, crosslink)
        return self.format_water(linear)

    #     GETTERS

    def get_replaced_crosslinkers(self, linear, crosslink):
        '''
        Replaces the linear [CROSSLINKER] mods with masses corresponding to
        the bridge in reverse order.
        '''

        crosslink_number = crosslink.ends.number
        # make a deepcopy to avoid changes to the stored link
        crosslink = copy.deepcopy(crosslink)

        while crosslink_number:
            linear, mass = self.replacer(linear, crosslink, crosslink_number)
            linear = self.format_mass(linear, mass)
            crosslink_number -= 1

        return linear

    #     FORMATTERS

    def format_mass(self, linear, mass):
        '''Replaces the REPLACE placeholders with the bridge mass'''

        string = replacement_string(round(mass, self.precision))
        linear = linear.replace(REPLACE, string, 1)
        return linear.replace(REPLACE, '')

    def format_water(self, linear):
        '''Adds a water modification to the linearized peptide'''

        match = LETTERS.search(linear)
        if match:
            index = match.start()
            return '{0}[+18.0]{1}'.format(linear[:index+1], linear[index+1:])

        else:
            sub, mass = MASS_MODIFICATION.findall(linear)[-1]
            mass = round(float(mass) + 18.0, self.precision)
            string = replacement_string(mass)
            return linear[::-1].replace(sub[::-1], string[::-1], 1)[::-1]


@logger.init('spreadsheet', 'DEBUG')
class LabeledToSkyline(ToSkyline):
    '''
    Subclass to handle the differing modifications with isotope-labeled
    theoretical peptide pairs.
    '''

    def __init__(self, row):
        super(LabeledToSkyline, self).__init__(row)

        self.moddata = modifications.LabeledModificationsInPeptide(
            row, self.format)

    @logger.call('report', 'DEBUG')
    def __call__(self, label, spreadsheet, labeledcrosslink):
        '''Processes the labeled modifications for the labeled crosslinks'''

        peptides = self.moddata(label, spreadsheet)
        peptides = (PARENTHESES.sub('', i) for i in peptides)
        linear = ''.join(peptides)

        crosslink = self.__get_crosslink(labeledcrosslink, label)
        linear = self.get_replaced_crosslinkers(linear, crosslink)
        return self.format_water(linear)

    def __get_crosslink(self, labeledcrosslink, label):
        '''
        Returns the data indexes from the isotope-labeled crosslink
        Translates the index pointing to an unlabeled crosslink to
        one pointing at the matched data.
        '''

        crosslink = self.row.data['crosslinks'][labeledcrosslink.index]
        return crosslink._replace(crosslinker=label.crosslinker)
