'''
    XlPy/Matched/proteins
    _____________________

    Downloads target gene names from the UniProt KB server.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import copy
import operator as op
import weakref

from collections import namedtuple

from xldlib import resources
from xldlib.chemical import proteins
from xldlib.qt.objects import base
from xldlib.utils.conn import uniprot
from xldlib.utils import logger
from xldlib.xlpy import wrappers


# HELPERS
# -------


def getids(ids, regex=resources.ID_REGEX):
    '''
    Returns entries that are any database-defined ID, filtering for those
    that match the custom regex.
    '''

    return {i for i in ids if regex.match(i)}


# OBJECTS
# -------

UniProtQuery = namedtuple("UniProtQuery", "fasta mnemonic")


# DOWNLOADER
# ----------


@logger.init('matched', 'DEBUG')
class DownloadGenes(base.BaseObject):
    '''
    Makes query to UniProt KB server to download not local gene
    names, adds resulting proteins to dictionary and dumps to JSON.
    '''

    def __init__(self, ids):
        super(DownloadGenes, self).__init__()

        self.ids = ids

        source = self.app.discovererthread
        self.proteins = weakref.proxy(source.proteins)
        self.protein_model = weakref.proxy(source.protein_model)
        self.fingerprinting = source.matched.getattr('fingerprinting')

        self.downloader = uniprot.GeneDownloader()

    @wrappers.threadprogress(7, 2, op.attrgetter('quantitative'))
    @wrappers.threadmessage("Downloading target genes...")
    def __call__(self):
        '''
        On start. Removes decoys and local entries, and
        fetches the remaining entries form the UniProt KB server.
        '''

        self.protein_model.setTable('proteins')
        self.protein_model.select()

        query = self.getquery()
        for field, items in query._asdict().items():
            rows = self.downloader.get_proteins(items, field=field)
            protein_objs = (proteins.Protein.from_uniprot(i) for i in rows)
            for protein_obj in protein_objs:
                self.protein_model.addprotein(protein_obj)

        self.proteins.set_mapping()
        self.setdepricated()
        self.protein_model.submit_all(False)

    #      SETTERS

    def setdepricated(self):
        '''Stores the depricated IDs to ignore on future queries'''

        self.protein_model.setTable('depricated')
        self.protein_model.select()

        proteins = copy.copy(self.ids)
        proteins.difference_update(self.proteins.mapping['depricated'])
        proteins.difference_update(self.proteins.mapping['proteins'])

        for protein in proteins:
            self.protein_model.adddepricated(protein)

    #      GETTERS

    def getquery(self):
        '''Returns the uniprot protein query for gene downloads'''

        if self.fingerprinting:
            # limited database, don't add anything
            return UniProtQuery([], [])

        # grab the to-fetch proteins, and the subtract the local proteins
        proteins = copy.copy(self.ids)
        proteins.difference_update(self.proteins.mapping['depricated'])
        ids = getids(proteins)
        ids.difference_update(self.proteins.mapping['proteins'])

        mnemonics = getids(proteins, resources.MNEMONIC_REGEX)
        mnemonics.difference_update(self.proteins.mapping['proteins'])

        return UniProtQuery(list(ids), list(mnemonics))
