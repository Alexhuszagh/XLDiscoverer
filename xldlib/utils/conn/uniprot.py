r'''
    Utils/conn/uniprot
    __________________

    Tools to simplify programmatic access to UniProt with GET requests.
    See:
        http://www.uniprot.org/help/programmatic_access

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

    >>> uniprot = UniProtDownloader()
    >>> uniprot.open()
    >>> request = Request("uniprot", "fasta", "P46406")

    >>> uniprot.get_url(request)
    '/uniprot/%3Fsort=score&desc=&query=fasta%3AP46406&fil=&force=no&format=tab&columns=id%2Cgenes%28PREFERRED%29%2Csequence'

    >>> response = uniprot.get_request(request)
    >>> response.status
    200

    >>> response.read()
    b'Entry\tGene names  (primary )\tSequence\nP46406\tGAPDH\tMVKVGVNGFGRIGRLVTRAAFNSGKVDVVAINDPFIDLHYMVYMFQYDSTHGKFHGTVKAENGKLVINGKAITIFQERDPANIKWGDAGAEYVVESTGVFTTMEKAGAHLKGGAKRVIISAPSADAPMFVMGVNHEKYDNSLKIVSNASCTTNCLAPLAKVIHDHFGIVEGLMTTVHAITATQKTVDGPSGKLWRDGRGAAQNIIPASTGAAKAVGKVIPELNGKLTGMAFRVPTPNVSVVDLTCRLEKAAKYDDIKKVVKQASEGPLKGILGYTEDQVVSCDFNSATHSSTFDAGAGIALNDHFVKLISWYDNEFGYSNRVVDLMVHMASKE\n'

    >>> with uniprot:
    ...     # tests error catching
    ...     raise socket.gaierror
    ...

    >>> genes = GeneDownloader()
    >>> for row in genes.get_proteins(['P46406']):
    ...     print(row)
    ...
    {'Gene names  (primary )': 'GAPDH', 'Entry': 'P46406', 'Sequence': 'MVKVGVNGFGRIGRLVTRAAFNSGKVDVVAINDPFIDLHYMVYMFQYDSTHGKFHGTVKAENGKLVINGKAITIFQERDPANIKWGDAGAEYVVESTGVFTTMEKAGAHLKGGAKRVIISAPSADAPMFVMGVNHEKYDNSLKIVSNASCTTNCLAPLAKVIHDHFGIVEGLMTTVHAITATQKTVDGPSGKLWRDGRGAAQNIIPASTGAAKAVGKVIPELNGKLTGMAFRVPTPNVSVVDLTCRLEKAAKYDDIKKVVKQASEGPLKGILGYTEDQVVSCDFNSATHSSTFDAGAGIALNDHFVKLISWYDNEFGYSNRVVDLMVHMASKE'}

    >>> for row in genes.get_proteins(['G3P_RABIT'], field='mnemonic'):
    ...     print(row)
    ...
    {'Gene names  (primary )': 'GAPDH', 'Sequence': 'MVKVGVNGFGRIGRLVTRAAFNSGKVDVVAINDPFIDLHYMVYMFQYDSTHGKFHGTVKAENGKLVINGKAITIFQERDPANIKWGDAGAEYVVESTGVFTTMEKAGAHLKGGAKRVIISAPSADAPMFVMGVNHEKYDNSLKIVSNASCTTNCLAPLAKVIHDHFGIVEGLMTTVHAITATQKTVDGPSGKLWRDGRGAAQNIIPASTGAAKAVGKVIPELNGKLTGMAFRVPTPNVSVVDLTCRLEKAAKYDDIKKVVKQASEGPLKGILGYTEDQVVSCDFNSATHSSTFDAGAGIALNDHFVKLISWYDNEFGYSNRVVDLMVHMASKE', 'Entry name': 'G3P_RABIT'}

'''

# load modules
import codecs
import csv
import operator as op
import socket
import time

from xldlib.definitions import httplib, quote, urlencode
from xldlib.qt.objects import base
from xldlib.utils import logger
from xldlib import resources

# load objects/functions
from collections import namedtuple, OrderedDict


# CONSTANTS
# ---------
# Currently maximum (hard) is 200 entries
MAX_BASKET = 150

# UniProt requests User Agent + email for debugging purposes
HEADERS = {'User-Agent': 'Python {}'.format(resources.MAINTAINER_EMAIL)}

# QUERIES
# -------

UNIPROT_QUERY = OrderedDict([
    ('sort', 'score'),
    ('desc', ''),
    ('query', '{field}:{query}'),
    ('fil', ''),
    ('force', 'no'),
    ('format', 'tab'),
    ('reviewed', 'yes'),
    ('columns', '{columns}')
])

PROTEOMES_QUERY = OrderedDict([
    ('query', '{query}'),
    ('format', 'tab')
])

COLUMNS = [
    'id',
    'entry name',
    'genes(PREFERRED)',
    'sequence'
]

DELIMITERS = {
    'fasta': ',',
    'mnemonic': ' OR '
}

# HELPERS
# -------


def uniprottime(item, getter=op.itemgetter('Last modified')):
    '''Parses the UniProt date into a datetime object'''

    return time.strptime(getter(item), '%Y-%m-%d')


# OBJECTS
# -------

class Request(namedtuple("Request", "directory field query columns")):
    '''Definitions for a URL requests and queries'''

    def __new__(cls, directory, field, query, columns=None):
        return super(Request, cls).__new__(cls,
            directory, field, query, columns)

    #    GETTERS

    def get_query(self):
        '''Returns the URL query string from the request object'''

        if self.directory == 'uniprot':
            return self.__get_uniprot_query()
        elif self.directory == 'proteomes':
            return self.__get_proteomes_query()

    def get_url(self, path):
        '''Request() -? "/uniprot/?<query-field>"'''

        path = quote(path.format(directory=self.directory))
        return path + '?' + self.get_query()

    def __get_uniprot_query(self):
        '''
        Request() -> ("sort=score&desc=&query=fasta:P46406&fil=&force=no
        "&format=tab&columns=id,genes(PREFERRED),sequence")
        '''

        query = UNIPROT_QUERY.copy()
        query['query'] = query['query'].format(
            field=self.field, query=self.query)

        columns = self.columns
        if self.columns is None:
            columns = ','.join(COLUMNS)
        query['columns'] = query['columns'].format(columns=columns)

        return urlencode(query, doseq=True)

    def __get_proteomes_query(self):
        '''
        Request() -> ("sort=score&desc=&query=fasta:P46406&fil=&force=no
        "&format=tab&columns=id,genes(PREFERRED),sequence")
        '''

        query = PROTEOMES_QUERY.copy()
        query['query'] = query['query'].format(query=self.query)
        return urlencode(query, doseq=True)


# BASE DOWNLOADER
# ---------------


@logger.init('bio', 'DEBUG')
class UniProtDownloader(base.BaseObject):
    '''Fetches a query from the UniProt KB server'''

    def __init__(self):
        super(UniProtDownloader, self).__init__()

    def __enter__(self):
        '''Opens a connection with entering "with" statements'''

        self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Closes a connection upon leaving "with" statements'''

        self.close()
        return isinstance(exc_val, (OSError, httplib.HTTPException,
                                    socket.gaierror))

    #      I/O

    @logger.raise_error
    def open(self, host='www.uniprot.org', port=80):
        '''Opens a connection to the UniProt server'''

        self.conn = httplib.HTTPConnection(host, port)

    def close(self):
        '''Closes an open connection to the UniProt server'''

        if hasattr(self, "conn"):
            self.conn.close()
            del self.conn

    #     GETTERS

    @logger.raise_error
    def get_request(self, request):
        '''Returns a GET HTTP request from the UniProt server'''

        request = self._requestchecker(request)
        if not hasattr(self, "conn"):
            self.open()

        url = self.get_url(request)
        self.conn.request('GET', url, headers=HEADERS)
        response = self.conn.getresponse()

        return response

    def get_url(self, request, path='/{directory}/'):
        request = self._requestchecker(request)
        return request.get_url(path)

    #     HELPERS

    def _requestchecker(self, request):
        '''Checks to ensure a proper request object is passed'''

        if isinstance(request, Request):
            return request

        elif isinstance(request, tuple) and len(request) == 4:
            return Request(*request)


# TARGETED DOWNLOADERS
# --------------------


@logger.init('bio', 'DEBUG')
class GeneDownloader(base.BaseObject):
    '''
    Downloads target gene sequence from the UniProt server,
    adds in timeout and processing methods for lazy evaluation.
    '''

    def __init__(self):
        super(GeneDownloader, self).__init__()

        self.uniprot = UniProtDownloader()

    #     GETTERS

    def get_proteins(self, proteins, field='fasta', sep='\t'):
        '''
        Queries the UniProt database for protein sequences. Yields
        an iterable which automatically closes the connection on finishing,
        with fields delineated in a csv.DictReader format.
            field -- {'fasta', 'mnemonic'}, to grab columns for the query
        '''

        delimiter = DELIMITERS[field]
        for index in range(0, len(proteins), MAX_BASKET):
            with self.uniprot:
                query = delimiter.join(proteins[index: index + MAX_BASKET])
                request = Request('uniprot', field, query)

                response = self.uniprot.get_request(request)
                codec = codecs.getreader("ascii")(response)
                reader = csv.DictReader(codec, delimiter=sep)

                for row in reader:
                    yield row

    def get_proteome(self, proteome_id, sep='\t'):
        '''Yields an iterator for all proteins in the reference proteome'''

        request = Request('uniprot', 'proteome', proteome_id)
        with self.uniprot:
            response = self.uniprot.get_request(request)
            codec = codecs.getreader("ascii")(response)
            reader = csv.DictReader(codec, delimiter=sep)

            for row in reader:
                yield row

    def get_proteome_id(self, taxon, sep='\t'):
        '''
        Queries the UniProt database for proteome IDs from a given taxonomic
        identifier, and then yield a sorted iterator by entry data.
        '''

        request = Request('proteomes', None, taxon)
        with self.uniprot:
            response = self.uniprot.get_request(request)
            codec = codecs.getreader("ascii")(response)
            reader = csv.DictReader(codec, delimiter=sep)
            entries = sorted(reader, key=uniprottime)

            assert entries

            for entry in entries:
                yield entry['Proteome ID']
