'''
    Utils/Bio/uniprot_xml
    _____________________

    UniProt XML schema parser.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import xml.etree.cElementTree as cET

from xldlib.utils import logger
from xldlib.utils.io_ import high_level, ziptools

# load objects/functions
from xml.etree.ElementTree import ParseError


# CONSTANTS
# ---------

UNIPROT_UPPER_TAG = '{HTTP://UNIPROT.ORG/UNIPROT}'
UNIPROT_LOWER_TAG = UNIPROT_UPPER_TAG.lower()

UPPER_PATHS = {
    'id': "./{0}accession".format(UNIPROT_UPPER_TAG),
    'mnemonic': "./{0}name".format(UNIPROT_UPPER_TAG),
    'name': ".//{0}fullName".format(UNIPROT_UPPER_TAG),
    'sequence': "./{0}sequence".format(UNIPROT_UPPER_TAG)
}

LOWER_PATHS = {
    'id': "./{0}accession".format(UNIPROT_LOWER_TAG),
    'mnemonic': "./{0}name".format(UNIPROT_LOWER_TAG),
    'name': ".//{0}fullName".format(UNIPROT_LOWER_TAG),
    'sequence': "./{0}sequence".format(UNIPROT_LOWER_TAG)
}


# OBJECTS
# -------


@logger.init('bio', 'DEBUG')
class Parse(object):
    '''
    Iterative XML parser which acts as a generator, yielding
    data to a downstream target.

    It lazily evaluates records to be processed as needed,
    within a context manager, allowing automated cleanup.
    '''

    def __init__(self, path=None):
        super(Parse, self).__init__()

        self.fileobj = None
        self.parser = None
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

        if self.parser is not None:
            try:
                for item in self._iterparser():
                    yield item
            except ParseError:
                raise AssertionError("Non-XML document")

    #     PUBLIC

    def open(self, path, mode='r'):
        '''Open file handle and initialize parser'''

        path = ziptools.decompress(path).name
        self.fileobj = open(path, mode)
        self.parser = cET.iterparse(self.fileobj)

    def close(self):
        '''Remove temp files and close parser and file object'''

        self.fileobj.close()
        high_level.remove_tempfiles()

        self.parser = None
        self.fileobj = None

    #   NON-PUBLIC

    def _iterparser(self):
        '''Iterator over the active parser object'''

        for event, element in self.parser:
            if element.tag == UNIPROT_UPPER_TAG + 'entry':
                yield self._upper(element)
            if element.tag == UNIPROT_LOWER_TAG + 'entry':
                yield self._lower(element)

    def _upper(self, element):
        '''
        Parse single XML node with upper-case tags.
        For full arg specs, see `self._entry`.
        '''

        return self._entry(element, UPPER_PATHS)

    def _lower(self, element):
        '''
        Parse single XML node with lower-case tags.
        For full arg specs, see `self._entry`.
        '''

        return self._entry(element, LOWER_PATHS)

    def _entry(self, element, paths):
        '''
        Parse single XML node with tag 'entry' to dict
        Args:
            element (cET.Element):      parent node to find path
            paths (dict):               {key: xpaths} for choldren
        '''

        entry = {}
        for key, path in paths.items():
            entry[key] = element.find(path).text

        entry['sequence'] = ''.join(entry['sequence'].splitlines())
        return entry
