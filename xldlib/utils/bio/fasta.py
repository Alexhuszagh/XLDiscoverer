'''
    Utils/Bio/Fasta
    _______________

    Intelligent fasta parser, which attempts to parse the header fields
    and parse all meaningful detail, including 'gb', 'sp', 'emb', and other
    identifiers, as well sequence cleanup including truncating at stop
    codons.

    This module aims for high performance, for a quick test of
    the revised UniProt (Swiss-Prot) database (with 549,381 entries), the
    file was parsed in ~6 seconds, or about 1 record every 9e-6 seconds
    (comparable to BioPython).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib import exception
from xldlib.definitions import re
from xldlib.utils import logger
from xldlib.utils.io_ import high_level, ziptools

# REGEXP
# ------

ISOFORM = re.compile(r'^(.*)\.\d$')
HYPHEN = re.compile(r'-')
ASTERIX = re.compile(r'\*')

# OBJECTS
# -------


class FastaParserMixin(object):
    '''
    Mixin to provide methods to parse FASTA records using
    specific identifiers.
    '''

    #   NON-PUBLIC

    @exception.except_error(IndexError)
    def _parse_gi(self, headers):
        '''
        Extract GenBank identifier number (GI) from the `headers`
        For more information on a gi number, see:
            http://www.ncbi.nlm.nih.gov/Sitemap/sequenceIDs.html
        '''

        self['gi'] = headers.pop(0)

    @exception.except_error(IndexError)
    def _parse_gb(self, headers):
        '''
        Extract GenBank identifier and locus from `headers`.
        For more information on a gi number, see:
            http://www.ncbi.nlm.nih.gov/Sitemap/sequenceIDs.html
        '''

        accession = headers.pop(0)
        locus = _trailing(headers)
        self['gb'] = (accession, locus)

    @exception.except_error(IndexError)
    def _parse_emb(self, headers):
        '''
        Extract EMBL Data Library identifier and locus
        For more information on EMB identifiers, see:
            https://www.ncbi.nlm.nih.gov/pmc/articles/PMC99098/
        '''

        accession = headers.pop(0)
        locus = _trailing(headers)
        self['emb'] = (accession, locus)

    @exception.except_error(IndexError)
    def _parse_dbj(self, headers):
        '''
        Extract DNA identifier and locus:
        For more information on DNA DBJ identifiers, see:
            http://www.ddbj.nig.ac.jp/intro-e.html
        '''

        accession = headers.pop(0)
        locus = _trailing(headers)
        self['dbj'] = (accession, locus)

    @exception.except_error(IndexError)
    def _parse_pir(self, headers):
        '''
        Extract Protein Information Resources identifier
        For more information on PIR identifiers, see:
            https://www.ncbi.nlm.nih.gov/pubmed/12520019
        '''

        headers.pop(0)      # discard first item
        self['pir'] = _trailing(headers)

    @exception.except_error(IndexError)
    def _parse_prf(self, headers):
        '''
        Extract Protein Research Foundation identifier.
        For more information on PRF identifiers, see:
            http://www.prf.or.jp/index-e.html
        '''

        headers.pop(0)      # discard first item
        self['prf'] = _trailing(headers)

    @exception.except_error(IndexError)
    def _parse_sp(self, headers):
        '''
        Extract SWISS-PROT accession number (UniProt ID) and mnemonic
        For more information on SWISS-PROT accession numbers, see:
            http://www.uniprot.org/help/accession_numbers
        '''

        accession = headers.pop(0)

        # 'Z_OLVVA RING finger' -> entry='Z_OLVVA'
        # -> headers[0] = 'RING finger'
        entry = _trailing(headers)
        self['sp'] = (accession, entry)

    @exception.except_error(IndexError)
    def _parse_pdb(self, headers):
        '''
        Extract Protein Data Bank identifier and chain
        For more information on PDB identifiers, see:
            http://www.rcsb.org/pdb/home/home.do
        '''

        entry = headers.pop(0)
        chain = _trailing(headers)
        self['pdb'] = (entry, chain)

    @exception.except_error(IndexError)
    def _parse_pat(self, headers):
        '''Extract patent identifier with counter and number'''

        country = headers.pop(0)
        number = _trailing(headers)
        self['pat'] = (country, number)

    @exception.except_error(IndexError)
    def _parse_bbs(self, headers):
        '''
        Extract GenInfo Backbone Id number
        For more information on GenBank Backbone identifiers, see:
            https://www.ncbi.nlm.nih.gov/IEB/ToolBox/SDKDOCS/SEQLOC.HTML
        '''

        self['bbs'] = headers.pop(0)

    @exception.except_error(IndexError)
    def _parse_gnl(self, headers):
        '''
        Extract General Database Identifier, which comprises two
        separate fields, the database and identifier.
        '''

        database = headers.pop(0)
        identifier = _trailing(headers)
        self['gnl'] = (database, identifier)

    @exception.except_error(IndexError)
    def _parse_ref(self, headers):
        '''
        Extract NCBI Reference Sequence accession number and locus
        For more information on NCBI identifiers, see:
            https://www.ncbi.nlm.nih.gov/refseq/about/
        '''

        accession = headers.pop(0)

        # 'BACDNAE B.subtilis' -> locus='BACDNAE'
        # -> headers[0] = 'B.subtilis
        locus = _trailing(headers)
        self['ref'] = (accession, locus)

    @exception.except_error(IndexError)
    def _parse_lcl(self, headers):
        '''
        Extract Local Sequence identifier.
        For more information on LCL identifiers, see:
            https://en.wikipedia.org/wiki/FASTA_format
        '''

        self['lcl'] = headers.pop(0)


class ProteinData(dict, FastaParserMixin):
    '''
    Definition for a Protein record, which parses lines from
    FASTA files, and generates a record for the protein.
    '''

    def __init__(self, *args, **kwds):
        super(ProteinData, self).__init__(*args, **kwds)

        self.setdefault('sequence', '')
        self.stop = False

    #     PUBLIC

    def header(self, line):
        '''
        Return FASTA file line is a header line.

        Args:
            line (str): single line within FASTA file
        '''

        return line.startswith('>')

    def finished(self, line):
        '''
        Check if current record is finished.
        See `self.header` for full arg specs.

        Returns (bool): Record is finished
        '''

        return self.stop or self.header(line)

    def parse(self, line):
        '''
        Parse `line` and add data to `self`.
        See `self.header` for full arg specs.
        '''

        if self.header(line):
            self._parse_header(line)
        else:
            self._parse_sequence(line)

    #    NON-PUBLIC

    def _parse_header(self, line):
        '''
        Parse a header line (stars with '>') within the FASTA file,
        and add the metadata to the record.

        Args:
            line (str):  single line within FASTA file
        '''

        headers = line[1:].split('|')
        while len(headers) > 1:
            # use pop and lookup for O(1) searching, no lookups
            field = headers.pop(0)
            fun = getattr(self, "_parse_{}".format(field), None)
            if fun is not None:
                fun(headers)

        # last header is the name information
        if headers:
            self['description'] = headers[0]

    def _parse_sequence(self, line, clean=True):
        '''
        Parse a protein sequence line, and add the line to
        `self['sequence]`.
        See `_sequence` for full arg specs.
        '''

        sequence, stop = _sequence(line.strip(), clean)
        self['sequence'] += sequence
        self.stop = stop


@logger.init('bio', 'DEBUG')
class Parse(object):
    '''
    Toolkit to parse FASTA files. This module aims to be extensible,
    lightweight, and quick.

    A typical NCBI fasta header looks as follows:
        >gi|160332366|sp|P46406.3|G3P_RABIT RecName: Full=Glyce...

    The first field is 'gi' followed by a GenBank identifier. The following
    fields are delineated below, which can differ from ID to ID.

    : Fields
            NOTE: Text delimiting fields is from BioPerl, and can be found
            here: http://doc.bioperl.org/releases/bioperl-current/bioperl-live/Bio/Search/Hit/GenericHit.html#CODE40
        GenBank                           gb|accession|locus
        EMBL Data Library                 emb|accession|locus
        DDBJ, DNA Database of Japan       dbj|accession|locus
        NBRF PIR                          pir||entry
        Protein Research Foundation       prf||name
        SWISS-PROT                        sp|accession|entry name
        Brookhaven Protein Data Bank      pdb|entry|chain
        Patents                           pat|country|number
        GenInfo Backbone Id               bbs|number
        General database identifier       gnl|database|identifier
        NCBI Reference Sequence           ref|accession|locus
        Local Sequence identifier         lcl|identifier
    '''

    def __init__(self, path=None):
        super(Parse, self).__init__()

        self.fasta = None

        if path is not None:
            self.open(path)

    @logger.call('bio', 'debug')
    def __enter__(self):
        '''Enter `open` state of the parser.'''

        return self

    @logger.call('bio', 'debug')
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Exit `open` state and close parsers and file handles.'''

        self.close()

    def __iter__(self):
        '''
        Return parser-based iterator yielding individual entries
        Yields: entry (dict):
        '''

        if self.fasta is not None:
            return self.parse()

    #       I/O

    def open(self, path, mode='r'):
        '''Open file handle'''

        path = ziptools.decompress(path).name
        self.fasta = open(path, mode)

    def close(self):
        '''Remove temp files and close file object'''

        if self.fasta is not None:
            self.fasta.close()
            high_level.remove_tempfiles()
            self.fasta = None

    #     PARSERS

    def parse(self, clean_sequence=True):
        '''
        Parse open fasta file, making educated guesses on the
        header fields.
            clean_sequence -- Remove '*-' characters from the sequence
                '*' is a stop codon, which aborts the rest of the sequence
                '-' signifies a gap of undetermined length
        '''

        assert self.fasta is not None

        protein = ProteinData()
        for line in self.fasta:
            if protein and protein.finished('line'):
                yield protein
                protein = ProteinData()

            protein.parse(line)

        if protein:
            yield protein


# PRIVATE
# -------


def _sequence(line, clean=True):
    '''
    If clean_sequence, returns a r'[a-zA-Z]' matching sequence

    Args:
        line (str):     single line within FASTA file
        clean (bool):   Remove '*-' characters from the sequence
            '*' is a stop codon, which aborts the rest of the sequence
            '-' signifies a gap of undetermined length
    '''

    stop = False
    if clean:
        line = HYPHEN.sub('', line)
        match = ASTERIX.search(line)

        if match is not None:
            # stop codon found
            line = line[:match.start()]
            stop = True

    return line, stop


def _trailing(headers):
    '''
    Guess file format from first item within headers, and return
    trailing values from the header item.
    Args:
        headers (list):     list of header fields
    '''

    line = headers[0]
    if line.startswith(' '):
        # '| agglutinin [Amaranthus caudatus] ' case, no ID there
        headers[0] = line.strip()
        return

    else:
        line = line.split(None, 1)
        headers[0] = ''.join(line[1:])
        return line[0]


def _remove_isoform(accession):
    '''
    Remove isoform number from the accession number

    Args:
        accession (str):    UniProt identifier with isoform
    Returns:    (str)       identifier without isoform
    Ex:
        _remove_isoform('P46406.1') -> 'P46406'
    '''

    match = ISOFORM.match(accession)
    if match:
        return match.group(1)
    else:
        return accession
