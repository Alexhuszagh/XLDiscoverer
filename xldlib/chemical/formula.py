'''
    Chemical/formula
    ________________

    Objects for chemical formulas, as well as mixins for chemical
    formula parsers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import Counter, defaultdict, Mapping

import six

from namedlist import namedlist

from xldlib.definitions import re
from xldlib.utils import serialization

from .building_blocks import AMINOACIDS, ELEMENTS, MONOMERS

__all__ = [
    'Molecule'
]


# CONSTANTS
# ---------

CHEMICAL = r'(\d{1,3})?([A-Z]{1}[a-z]?)(?:(-?\d+)|\((-?\d+)\))?'
MONOMER = r'(\w+)(?:(-?\d+)|\((-?\d+)\))?'
WATER_FORMULA = 'H2 O'


# OBJECTS
# -------

Aminoacid = namedlist("Aminoacid", [('letter'), ('formula', False)])

# DATA
# ----

NON_STRICT = {
    'B': Aminoacid('D'),
    'J': Aminoacid('I'),
    'X': Aminoacid('C9 H3', True),
    'Z': Aminoacid('E'),
}

# CHEMICALS
# ---------


class Atom(defaultdict):
    '''
    Object definition for isotopes and counts from a single atom.
    Provides a representation as a standard dictionary.

    Implements methods for `__mul__` and `__imul__`, to allow
    multiplication of atomic counts for each isotope.
    '''

    def __init__(self, *args, **kwds):
        super(Atom, self).__init__(int, *args, **kwds)

    #     MAGIC

    def __repr__(self):
        '''Return the standard dictionary representation'''

        return repr(dict(self))

    def __mul__(self, other):
        '''Multiply self by other'''

        return self._constructor({k: v*other for k, v in self.items()})

    def __imul__(self, other):
        '''Inplace multiplication of self and other'''

        for isotope in self:
            self[isotope] *= other
        return self

    #    NON-PUBLIC

    def _constructor(self, obj=None):
        '''New object constructor mathematical and copy operations'''

        if obj is None:
            return Atom()
        return Atom(obj)


class ChemicalParserMixin(object):
    '''Mixin for parsing chemical formulas and updating a mapping object'''

    # REGEX
    # -----
    chemical = re.compile(r'^{}$'.format(CHEMICAL))
    monomer = re.compile(r'^{}$'.format(MONOMER))
    atom = re.compile(r'[A-Z][a-z]?')

    #      PUBLIC

    def update_chemical(self, formula, count):
        '''
        Update atomic counts from a string or mapping `formula`, and
        multiple by `count`.

        Args:
            formula (string, mapping):  chemical or glycan formula
            count (int):                scalar for elemental counts
        '''

        if isinstance(formula, Mapping):
            self._update_mapping(formula, count)
        elif isinstance(formula, six.string_types):
            self._update_str(formula, count)

    #    NON-PUBLIC

    def _update_mapping(self, formula, count):
        '''
        Update the elemental counts from a mapping `formula` multiplied
        by a scalar `count`. See `update_chemical` for full arg specs.
        '''

        for symbol, isotopes in formula.items():
            for isotope, number in isotopes.items():
                self[symbol][isotope] += number * count

    def _update_str(self, formula, count):
        '''
        Update the elemental counts from a str `formula` multiplied
        by a scalar `count`. See `update_chemical` for full arg specs.
        '''

        for item in formula.split():
            for symbol, isotope, number in self._parse(item):
                self[symbol][isotope] += number * count

    def _parse(self, item):
        '''
        Extract atomic symbol, isotope, and atomic counts from
        the `item` string.

        Args:
            item (str):  str in format of "13C6", "13C(6)", "Hex", "C6"
        '''

        match = self.chemical.match(item)
        if match:
            return [self._parse_element(match)]
        else:
            return self._parse_monomer(self.monomer.match(item))

    def _parse_element(self, match):
        '''Extract elemental data from re `match` group'''

        isotope, symbol, free, parentheses = match.groups()

        assert self._symbolchecker(symbol)
        isotope = int(isotope or -1)
        count = _element_count(free, parentheses)

        return symbol, isotope, count

    def _parse_monomer(self, match):
        '''Extract glycan monomer data from re `match` group'''

        monomer, free, parentheses = match.groups()
        count = _element_count(free, parentheses)
        formula = MONOMERS[monomer]

        for item in formula.split():
            match = self.chemical.match(item)
            symbol, isotope, number = self._parse_element(match)
            yield symbol, isotope, number * count

    #    HELPERS

    def _symbolchecker(self, symbol):
        '''Check validity of atomic `symbol`'''

        return self.atom.match(symbol)


class AminoAcidParserMixin(ChemicalParserMixin):
    '''Mixin for parsing aminoacid formulas and updating a mapping object'''

    #      PUBLIC

    def update_peptide(self, peptide, count, add_water=True):
        '''
        Update atomic counts from a `peptide` sequence. By default,
        add a `WATER_FORMULA` to the isotopic counts, to mimic the
        N-/C-term water addition to the residues.

        Args:
            peptide (str):      aminoacid sequence
            count (int):        scalar for elemental counts
        '''

        for residue, number in Counter(peptide).items():
            formula = self._residue_formula(residue)
            self.update_chemical(formula, count * number)

        if add_water:
            self.update_chemical(WATER_FORMULA, count=count)

    #    NON-PUBLIC

    def _residue_formula(self, residue):
        '''Find the chemical formula from `residue`'''

        if residue in AMINOACIDS:
            return AMINOACIDS[residue].formula

        elif not self.strict and residue in NON_STRICT:
            aminoacid = NON_STRICT[residue]
            if aminoacid.formula:
                return aminoacid.letter
            else:
                return AMINOACIDS[aminoacid.letter].formula

        raise KeyError


@serialization.register('Molecule')
class Molecule(defaultdict, AminoAcidParserMixin):
    '''
    Convert string chemical formulas into dictionary-based formulas,
    with toolkits to calculate formula mass, lookup elements,
    add more monomers, etc.

    `Molecule` supports both elemental composition and defined,
    monomeric building blocks, most notably aminoacids and simple sugars
    (for glycans).

    The default, monoisotopic chemical formula for an element is specified
    with a `-1`, to avoid overlapping with any real elemental isotopes.

        Ex. 'C H2 O' --> {'C':{-1:1} , 'H':{-1:2} , 'O':{-1:1}}
    '''

    def __init__(self, formula=None, peptide=None, count=1, strict=True):
        '''
        See `update_formula` for full arg specs.
        Args:
            strict  (bool):         Use strict aminoacids only
        '''
        super(Molecule, self).__init__(Atom)

        self.strict = strict
        try:
            self.update_formula(formula, peptide, count)
        except AssertionError:
            # ignore blank arguments during initialization
            pass

    #     MAGIC

    @serialization.tojson
    def __json__(self):
        '''
        Serialize data for object reconstruction to JSON
        Returns (dict): serialized data
        '''

        return {
            'formula': self.tostr(),
            'strict': self.strict
        }

    def __float__(self):
        return self.mass

    def __round__(self, precision):
        return round(self.mass, precision)

    def __mul__(self, other):
        '''Multiply self by other'''

        assert isinstance(other, six.integer_types)
        return self._constructor({k: v*other for k, v in self.items()})

    def __imul__(self, other):
        '''Inplace multiplication of self and other'''

        assert isinstance(other, six.integer_types)
        for atom in self.values():
            atom *= other
        return self

    def __repr__(self):
        '''Simplified image to facilitate diagnosing atom changes'''

        keys = sorted(self, key=_mass, reverse=True)
        out = [(k, repr(self[k])) for k in keys]
        out = [': '.join(i) for i in out]
        return 'Molecule({' + ', '.join(out) + '})'

    #   CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        '''
        Deserialize JSON data into object constructor

        Args:
            data (dict, mapping):   serialized object data
        Returns (Molecule):         class instance
        '''

        formula = formula=data['formula']
        strict = data['strict']
        return cls(formula, strict=strict)

    #    PROPERTIES

    def get_mass(self):
        '''
        Calculate exact isotopic mass, assuming monoisotopic for all
        non-labeled (-1 for isotope) elements.
        Ex.
            >>> self
            {'N': {15: 4}, 'C': {13: 13, 12: 7}}
            >>> self.mass
            300.0406936472
        '''

        masses = []

        for symbol, atom in self.items():
            for isotope, count in atom.items():
                masses.append(_mass(symbol, isotope) * count)
        return float(sum(masses))

    mass = property(get_mass)

    #     PUBLIC

    def update_formula(self, formula=None, peptide=None, count=1):
        '''
        Update `self` with element counts from a chemical or monomeric
        formula, and multiple counts by `count`.
        Args:
            formula (None, str):    Chemical or glycan-based chemical formula
            peptide (None, str):    Aminoacid sequence.
            count   (int):          Add formula or peptide `count` times
        '''

        if not (formula or peptide):
            return
        if formula is not None:
            self.update_chemical(formula, count)
        if peptide is not None:
            self.update_peptide(peptide, count)

    def tostr(self):
        '''Return string representation of the chemical formula'''

        out = []
        symbols = sorted(self, key=_mass, reverse=True)
        for symbol in symbols:
            isotopes = sorted(self[symbol].items())
            atoms = ((symbol, k, v) for k, v in isotopes if v)
            out += map(_as_string, atoms)

        return ' '.join(out)

    #   NON-PUBLIC

    def _constructor(self, obj=None):
        '''New object constructor mathematical and copy operations'''

        if obj is None:
            return Molecule(strict=self.strict)
        return Molecule(obj, strict=self.strict)


# PRIVATE
# -------


def _mass(atom, isotope=-1, key=min):
    '''
    Sort isotopes from a given atom by molecular weight, by default
    return the light isotope for the given atom.

    Args:
        atom (str): elemental symbol
    '''

    isotopes = ELEMENTS[atom].isotopes
    if isotope == -1:
        isotope = key(isotopes)
    return isotopes[int(isotope)].mass


def _element_count(free, parentheses):
    '''
    Return total isotope count, which is either the free or
    parentheses-enclosed isotope count, since the regex matches
    both using separate match groups.

    Args:
        free (str, None):          isdigit() str or Nonetype
        parentheses (str, None):   isdigit() str or Nonetype
    '''

    if free is None and parentheses is None:
        return 1
    elif free is None:
        return int(parentheses)
    else:
        return int(free)


def _as_string(item):
    '''Return string representation of an atom and isotope counts'''

    symbol, isotope, count = item
    if isotope == -1:
        return '{0}{1}'.format(symbol, count)
    else:
        return '{0}{1}{2}'.format(isotope, symbol, count)
