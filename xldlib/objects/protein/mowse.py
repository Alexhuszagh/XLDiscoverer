'''
    Objects/Protein/mowse
    _____________________

    Implementation of the MOWSE algorithm for high-speed peptide
    sequencing.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

    >>> db = MowseDatabase()
    >>> db.new(1e4, 1e5)
    >>> matrix = db.mowsematrix
    >>> axis = matrix.protein.getsize(1e4)
    /mowsematrix/protein/1/3 (Table(0,), shuffle, blosc(5)) 'Peptide Search Node'
      description := {
      "id": StringCol(itemsize=11, shape=(), dflt=b'', pos=0),
      "mass": Float64Col(shape=(), dflt=0.0, pos=1),
      "mods": Int64Col(shape=(52,), dflt=0, pos=2),
      "sequence": StringCol(itemsize=50, shape=(), dflt=b'', pos=3),
      "start": Int64Col(shape=(), dflt=0, pos=4)}
      byteorder := 'little'
      chunkshape := (132,)
'''

# load future
from __future__ import division

# load modules
import operator as op
import weakref

import tables as tb

from xldlib.chemical import proteins
from xldlib.utils import logger
from xldlib.resources import chemical_defs, paths
from xldlib.resources.parameters import defaults

from .. import pytables

# load objects/functions
from collections import namedtuple


# DATA
# ----

INVERSE_SCALE = {
    'protein': 'peptide',
    'peptide': 'protein'
}


# TABLES
# ------



def description():
    '''Dynamically generates a PeptideQuery description'''

    maxid = defaults.DEFAULTS['protein_identifier_length']
    maxpeptide = defaults.DEFAULTS['maximum_peptide_length']

    class PeptideQuery(tb.IsDescription):
        id       = tb.StringCol(maxid)
        sequence = tb.StringCol(maxpeptide)
        mods     = tb.Int64Col(shape=(maxpeptide + 2))
        start    = tb.Int64Col()
        mass     = tb.Float64Col()

    return PeptideQuery


# OBJECTS
# -------

Point = namedtuple("Point", "protein peptide")


class MowseInterval(namedtuple("MowseInterval", "protein peptide")):
    '''Definitions for scaling factors for the mowse database'''

    @classmethod
    def default(cls):
        return cls(defaults.DEFAULTS['protein_interval'],
                   defaults.DEFAULTS['peptide_interval'])


class PeptideRange(namedtuple("PeptideRange", "min max")):
    '''Definitions for a peptide range object'''

    def __new__(cls, min, max):
        return super(PeptideRange, cls).__new__(cls, int(min), int(max))

    @classmethod
    def default(cls):
        return cls(defaults.DEFAULTS['minimum_peptide_mass'],
                   defaults.DEFAULTS['maximum_peptide_mass'])

    def __div__(self, other):
        return PeptideRange(*(op.div(i, other) for i in self))

    def __floordiv__(self, other):
        return PeptideRange(*(op.floordiv(i, other) for i in self))

    def __truediv__(self, other):
        return PeptideRange(*(op.truediv(i, other) for i in self))


class ProteinRange(namedtuple("ProteinRange", "min max")):
    '''Definitions for a protein range object'''

    def __new__(cls, min, max):
        return super(ProteinRange, cls).__new__(cls, int(min), int(max))

    def __div__(self, other):
        return PeptideRange(*(op.div(i, other) for i in self))

    def __floordiv__(self, other):
        return PeptideRange(*(op.floordiv(i, other) for i in self))

    def __truediv__(self, other):
        return PeptideRange(*(op.truediv(i, other) for i in self))


class _2DIndexes(namedtuple("_2DIndexes", "scale min max")):
    '''Definitions for mapped indexes in pseudo 2D matrix'''

    @classmethod
    def fromrange(cls, proteinrange, peptiderange):
        '''Initializes the indexes set from a set of protein/peptide ranges'''

        scale = MowseInterval.default()
        protein = proteinrange // scale.protein
        peptide = peptiderange // scale.peptide

        min_ = Point(protein.min, peptide.min)
        max_ = Point(protein.max, peptide.max)

        return cls(scale, min_, max_)

    #       PUBLIC

    def proteinrows(self):
        return range(self.min.protein, self.max.protein + 1)

    def peptiderows(self):
        return range(self.min.peptide, self.max.peptide + 1)

    def getindex(self, size, scale):
        return int(size // getattr(self.scale, scale))

    def getotherindex(self, size, scale):
        '''Maps the index to the other scale'''

        return self.getindex(size, INVERSE_SCALE[scale])


# HDF5
# ----


@logger.init('mowse', 'DEBUG')
class Axis(pytables.Group):
    '''Definitions for a protein or peptide axis in the MowseDatabase'''

    def __init__(self, parent, group):
        super(Axis, self).__init__()

        self.parent = parent
        self.group = group

        self.setweakrefs()

    #      SETTERS

    def setweakrefs(self):
        self.view = weakref.ref(self.parent)
        self.matrix = weakref.ref(self.view().parent)
        self.document = weakref.ref(self.matrix().parent)

    #      GETTERS

    def getcell(self, index):
        return self.group._v_children[str(index)]

    def getsize(self, size):
        index = self.matrix().index.getotherindex(size, scale=self.view().name)
        return self.getcell(index)

    #      PUBLIC

    # TODO: need to add definitions upon spectral library creation...


@logger.init('mowse', 'DEBUG')
class MatrixView(pytables.Group):
    '''Definitions for a protein or peptide view in the MowseDatabase'''

    def __init__(self, parent, group):
        super(MatrixView, self).__init__()

        self.parent = parent
        self.group = group
        self.name = group._v_name

        self.setweakrefs()

    #      SETTERS

    def setweakrefs(self):
        self.matrix = weakref.ref(self.parent)
        self.document = weakref.ref(self.matrix().parent)

    #      PUBLIC

    @pytables.silence_naturalname
    def newtable(self, proteinindex, peptideindex):
        '''Initializes a new peptide search table'''

        return self.document().file.create_table(
            where='/mowsematrix/protein/{}'.format(proteinindex),
            name=str(peptideindex),
            description=description(),
            title="Peptide Search Node",
            filters=self.document().filter,
            createparents=True)

    @pytables.silence_naturalname
    def newlink(self, proteinindex, peptideindex, target):
        '''Creates a hard link between a protein/peptide to peptide/protein'''

        self.document().file.create_hard_link(
            where='/mowsematrix/peptide/{}'.format(peptideindex),
            name=str(proteinindex),
            target=target,
            createparents=True)

    def getsize(self, size):
        index = self.matrix().index.getindex(size, scale=self.name)
        return Axis(self, self.getgroup(str(index)))


class MowseMatrix(pytables.Group):
    '''Definitions for pseudo-2D matrix for the mowse database'''

    def __init__(self, parent, group, new=False):
        super(MowseMatrix, self).__init__()

        self.parent = parent
        self.group = group

        self.proteinrange = self.getattr('protein')
        self.peptiderange = self.getattr('peptide')
        self.index = _2DIndexes.fromrange(self.proteinrange, self.peptiderange)

        self.protein = MatrixView(self, self.getgroup('protein'))
        self.peptide = MatrixView(self, self.getgroup('peptide'))

        self.setweakrefs()

        if new:
            self.setdimensions()

    @classmethod
    def new(cls, parent, group, minprotein, maxprotein):
        '''Initializes a new matrix with a protein range'''

        # attrs
        group._v_attrs.protein = ProteinRange(minprotein, maxprotein)
        group._v_attrs.peptide = PeptideRange.default()

        # groups
        group._v_file.create_group(group, name='protein', title='Protein View')
        group._v_file.create_group(group, name='peptide', title='Peptide View')

        return cls(parent, group, new=True)

    #      SETTERS

    def setweakrefs(self):
        self.document = weakref.ref(self.parent)

    def setdimensions(self):
        '''Sets the mowse database dimensions and initiates the templates'''

        for proteinindex in self.index.proteinrows():
            for peptideindex in self.index.peptiderows():
                table = self.protein.newtable(proteinindex, peptideindex)
                self.peptide.newlink(proteinindex, peptideindex, table)


# DATABASE
# --------


@logger.init('mowse', 'DEBUG')
class MowseDatabase(pytables.Root):
    '''Creates an HDF5 matrix for generating a MowseDatabase'''

    def __init__(self, **kwds):
        super(MowseDatabase, self).__init__()

        self.mowsematrix = None

        if kwds.get('new', False):
            self.new(kwds['minprotein'], kwds['maxprotein'])
        elif kwds.get('open', False):
            self.open()
        elif kwds.get('tryopen', False):
            self.tryopen()

    @classmethod
    def fromproteins(cls, db, modifications=None):
        '''
        Initializes the Mowse database and constructs the queries
        from an HDF5 protein database
        '''

        if modifications is None:
            modifications = chemical_defs.MODIFICATIONS.selected

        group = db.get_group('proteins')
        mwrange = group.get_mwrange()

        inst = cls(new=True,
            minprotein=mwrange.min,
            maxprotein=mwrange.max)

        for row in group.iterrows(as_dict=True):
            protein = proteins.Protein(**row)
            protein.cut_sequence()
            for peptide in protein.peptides:
                # TODO: sample permutations...
                pass

        return inst

    def new(self, minprotein, maxprotein, path=paths.FILES['mowse']):
        '''Creates a new matrix within the dimensions'''

        self._new(path)

        group = self.create_group(name='mowsematrix', title='MowseMatrix')
        self.mowsematrix = MowseMatrix.new(self, group, minprotein, maxprotein)

    #      I/O

    def open(self, path=paths.FILES['mowse']):
        '''Opens a pre-existing file object'''

        self._open(path)

        self.mowsematrix = MowseMatrix(self, self.root.mowsematrix)

    def close(self):
        '''Closes an open file object'''

        self._close()

        self.mowsematrix = None

