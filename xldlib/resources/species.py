'''
    Resources/species
    _________________

    Species definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import OrderedDict

from namedlist import namedlist

__all__ = [
    'TAXA'
]


# OBJECTS
# -------


Species = namedlist("Species", [
    'id',
    'species',
    'genus',
    ('family', None),
    ('order', None),
    ('class_', None),
    ('phylum', None),
    ('kingdom', None),
    ('domain', None),
])


# DATA
# ----

TAXA = OrderedDict([
    ('M. musculus', Species(id='10090',
        species='musculus',
        genus='Mus',
        family='Muridae',
        order='Rodentia',
        class_='Mammalia',
        phylum='Chordata',
        kingdom='Animalia',
        domain='Eukaryota')),
    ('S. cerevisiae', Species(id='559292',
        species='cerevisiae',
        genus='Saccharomyces',
        family='Saccharomycetaceae',
        order='Saccharomycetales',
        class_='Saccharomycetes',
        phylum='Ascomycota',
        kingdom='Fungi',
        domain='Eukaryota')),
    ('S. pombe', Species(id='284812',
        species='pombe',
        genus='Schizosaccharomyces',
        family='Schizosaccharomycetaceae',
        order='Schizosaccharomycetales',
        class_='Schizosaccharomycetes',
        phylum='Ascomycota',
        kingdom='Fungi',
        domain='Eukaryota')),
    ('M. cuniculus', Species(id='9986',
        species='cuniculus',
        genus='Oryctolagus',
        family='Leporidae',
        order='Lagomorpha',
        class_='Mammalia',
        phylum='Chordata',
        kingdom='Animalia',
        domain='Eukaryota')),
    ('H. sapiens', Species(id='9606',
        species='sapiens',
        genus='Homo',
        family='Hominidae',
        order='Haplorhini',
        class_='Primates',
        phylum='Mammalia',
        kingdom='Chordata',
        domain='Animalia'))
])
