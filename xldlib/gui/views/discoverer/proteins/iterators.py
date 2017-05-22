'''
    Gui/Views/Crosslink_Discoverer/Proteins/iterators
    _________________________________________________

    Iterators for adding items to the proteins database via files
    (XML, FASTA) or database queries (UniProt KB).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op

from xldlib.chemical import proteins
from xldlib.definitions import re
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger
from xldlib.utils.bio import fasta, uniprot_xml
from xldlib.utils.conn import uniprot

from . import dialog


# ITERATORS
# ---------


@logger.init('database', 'DEBUG')
class UniProtFastaIterator(base.BaseObject):
    '''Definitions for a row-wise UniProt FASTA-format iterator'''

    def __init__(self, path):
        super(UniProtFastaIterator, self).__init__()

        self.path = path

    def __iter__(self):
        '''Custom iterator which transfers each object to Protein names'''

        with fasta.Parse(self.path) as parser:
            for entry in parser:
                self.app.processEvents()
                if 'sp' in entry:
                    yield proteins.Protein.from_fasta(entry)


@logger.init('database', 'DEBUG')
class UniProtXmlIterator(base.BaseObject):
    '''Definitions for a row-wise UniProt XML-format iterator'''

    def __init__(self, path):
        super(UniProtXmlIterator, self).__init__()

        self.path = path

    def __iter__(self):
        '''Custom iterator which transfers each object to Protein names'''

        with uniprot_xml.Parse(self.path) as parser:
            for entry in parser:
                self.app.processEvents()
                yield proteins.Protein(**entry)


@logger.init('database', 'DEBUG')
class UniProtServerIterator(base.BaseObject):
    '''Definitions for a UniProt KB iterator from a server query'''

    def __init__(self):
        super(UniProtServerIterator, self).__init__()

        self.downloader = uniprot.GeneDownloader()

        if self.escape_filter:
            self.regex = re.compile(re.escape(self.filter))
        else:
            self.regex = re.compile(self.filter)

    #    PROPERTIES

    @property
    def taxon(self):
        return defaults.DEFAULTS['taxonomy']

    @property
    def filter(self):
        return defaults.DEFAULTS['taxonomy_filter']

    @property
    def escape_filter(self):
        return defaults.DEFAULTS['escape_taxonomy_filter']

    @property
    def filter_mode(self):
        return defaults.DEFAULTS['taxonomy_filtermode']

    #      MAGIC

    def __iter__(self):
        '''Custom iterator which transfers each object to Protein names'''

        searchmode = op.attrgetter(dialog.MODES[self.filter_mode])
        proteome_id = next(self.downloader.get_proteome_id(self.taxon))
        for entry in self.downloader.get_proteome(proteome_id):
            self.app.processEvents()

            protein_obj = proteins.Protein.from_uniprot(entry)
            if self.regex.search(searchmode(protein_obj)):
                yield protein_obj
