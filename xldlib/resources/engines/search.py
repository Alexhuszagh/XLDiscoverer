'''
    Resources/Other/search
    ______________________

    Default parameters for Protein Prospector, Mascot, Proteome Discoverer,
    etc.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import copy

from collections import OrderedDict

from namedlist import namedlist

import tables as tb

from xldlib import exception
from xldlib.general import sequence
from xldlib.resources import chemical_defs
from xldlib.utils import serialization
from xldlib.utils.io_ import typechecker

from . import dicttools

# ENUMS
# -----

SEARCH_IDENTIFIERS = tb.Enum([
    'Protein Prospector',
    'Mascot',
    'Proteome Discoverer'
])

MATCHED_FORMATS = tb.Enum([
    'XML',
    'TEXT',
    'SQLITE',
    'MIME'
])


# DATA
# ----

MATCHED_TYPES = [
    "modifications",
    "num",
    "peptide",
    "start",
    "fraction",
    "id",
    "name",
    "mz",
    "z",
    "ppm",
    "score",
    "ev"
]


# HELPERS
# -------


def checkheader(headers, items):
    '''Checks if all items are in the headers'''

    for item in items:
        yield all(i in headers for i in item)


def convertmessage(items, message=exception.CODES['022']):
    '''Generates an error message for missing CSV headers'''

    pluralized = exception.convert_number(message, items)
    return pluralized.format(', '.join(['"{0}"'.format(i) for i in items]))


# OBJECTS
# -------


@sequence.serializable("SearchEngineDefaults")
class Defaults(namedlist("Defaults", "query optional_query header "
    "delimiter decoys nterm cterm neutralloss modifications")):
    '''Adds methods for modification additions/removals'''

    #     SETTERS

    def set_modifications(self, name):
        self.clear()
        modifications = chemical_defs.MODIFICATIONS.filter(engine=name)
        self.modifications.update(modifications)

    #     GETTERS

    def getheaders(self, header):
        '''Returns the CSV headers for a text-formatted file'''

        try:
            # split header into key columns
            headers = header.splitlines()[self.header]
            return set(headers.split(self.delimiter))
        except IndexError:
            # empty file
            raise TypeError

    def getquery(self):
        '''Returns the query with the optional_query added'''

        query = copy.copy(self.query)
        if self.optional_query is not None:
            if isinstance(query, (dict, set)):
                query.update(self.optional_query)
            elif isinstance(query, list):
                query.extend(self.optional_query)
        return query

    def getflatquery(self):
        '''Returns the query with the optional_query added'''

        query = self.getquery()
        if isinstance(query, dict):
            flatter = (i for item in query.values() for i in item)
            return [i for item in flatter for i in item]
        else:
            return query

    #     HELPERS

    def checktext(self, header, error=None):
        '''Checks a structured text file to see if any match exists'''

        matcheditems = []
        matched = True

        headers = self.getheaders(header)
        for matchedtype in MATCHED_TYPES:
            items = self.query.get(matchedtype, [])
            conditions = list(checkheader(headers, items))
            matched &= any(conditions) or not conditions

            if not matched:
                if matcheditems:
                    error = convertmessage(items)
                break
            matcheditems.extend(items)

        return matched, error

    def clear(self):
        self.modifications.clear()


@sequence.serializable("SearchEngineVersion")
class Version(namedlist("Version", "name major minor "
    "revision format defaults")):
    '''Peptide search database engine and version format.'''

    #     SETTERS

    def set_modifications(self):
        self.defaults.set_modifications(self.name)

    #     PUBLIC

    def tostr(self):
        '''Return string representation'''

        fileformat = MATCHED_FORMATS(self.format)
        return "{0}.{1}.{2}, {3}".format(self.major,
            self.minor,
            self.revision,
            fileformat)

    def key(self, position):
        '''Normalized protein termini for the relative peptide position'''

        #import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        if position == self.defaults.nterm:
            return 0
        elif position == self.defaults.cterm:
            return float("inf")
        else:
            return position

    def inpeptide(self, position, peptide):
        '''Returns the peptide-relative position, with 1-indexes removed'''

        #import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        if position == self.defaults.nterm:
            return 0
        elif position == self.defaults.cterm:
            return len(peptide) - 1
        else:
            return position - 1

    def totermini(self, length):
        return (1, length, self.defaults.nterm, self.defaults.cterm)


@serialization.register("SearchEngine")
class SearchEngine(dicttools.EngineDict):
    '''Method definitions for search engine objects'''

    # SETTINGS
    # --------
    mode = 'matched'

    #     SETTERS

    def setmodifications(self):
        '''Sets the modification entries on runtime'''

        for versions in self.values():
            for version in versions.values():
                version.set_modifications()

    #     PUBLIC

    def matchfile(self, fileobj):
        '''Matche fileobj to known spectral database format'''

        fileformat = _fileformat(fileobj)
        return getattr(self, '_match' + fileformat.lower())(fileobj)

    #    NON-PUBLIC

    def _matchsqlite(self, fileobj, error=None):
        '''Matches to spectral databases with SQLite3 formats'''
        raise NotImplementedError

    @dicttools.read_header
    def _matchxml(self, header, error=None):
        '''Matches to spectral databases with XML formats'''

        # TODO: need to match binary not text
        for name, version, engine in self.iterengines('XML'):
            if all(i in header for i in engine.defaults.header):
                return name, version, error

    @dicttools.read_header
    def _matchmime(self, header, error=None):
        '''Matches to spectral databases with MIME formats'''

        for name, version, engine in self.iterengines('MIME'):
            if engine.defaults.header[0] == header.splitlines()[0]:
                return name, version, error

    @dicttools.read_header
    def _matchtext(self, header, error=None):
        '''Matches to spectral databases with text (mostly CSV) formats'''

        for name, version, engine in self.iterengines('TEXT'):
            matched, error = engine.defaults.checktext(header)
            if matched or error:
                return name, version, error

    def clearmodifications(self):
        '''Clears the defined modifications'''

        for versions in self.values():
            for version in versions.values():
                version.clear()


# PRIVATE
# -------


def _fileformat(fileobj):
    '''
    Call file type-checkers to determine the type of
    file. A header, typically under 100 bytes, is read from the
    file and matched to a known filetype. If the file has a known
    format, return that format, Otherwise, if no encoding/decoding
    error is raised, return 'TEXT'.
    '''

    if typechecker.sqlite(fileobj):
        return 'SQLITE'
    elif typechecker.xml(fileobj):
        return 'XML'
    elif typechecker.mime(fileobj):
        return 'MIME'
    else:
        return 'TEXT'

# DATA
# ----


SEARCH = SearchEngine({
    'Protein Prospector': {
        '5.13.1, TEXT': Version('Protein Prospector', 5, 13, 1,
            format='TEXT',
            defaults=Defaults(
                query=OrderedDict([
                    ("num", [["MSMS Info"]]),
                    ("peptide", [["DB Peptide"]]),
                    ("start", [["Start"]]),
                    ("fraction", [["Fraction"]]),
                    ("id", [["Acc #"]]),
                    ("name", [["Protein Name"]]),
                    ("mz", [["m/z"]]),
                    ("z", [["z"]]),
                    ("ppm", [["ppm"]]),
                    ("score", [["Score"]]),
                    ("ev", [["Expect"]]),
                    ("modifications",
                        [["Mods"], ["Constant Mods", "Variable Mods"]])
                ]),
                optional_query={'rank': [["Rank"]]},
                header=2,
                delimiter='\t',
                decoys=['decoy'],
                nterm='N-term',
                cterm='C-term',
                neutralloss='Neutral loss',
                modifications={})),
        '5.13.1, XML': Version('Protein Prospector', 5, 13, 1,
            format='XML',
            defaults=Defaults(
                query=[
                    "modifications",
                    "num",
                    "peptide",
                    "fraction",
                    "id",
                    "name",
                    "mz",
                    "z",
                    "ppm",
                    "score",
                    "ev"
                ],
                optional_query=None,
                header=['search_engine="Protein Prospector Search Compare"'],
                delimiter=None,
                decoys=[],
                nterm='nterm',
                cterm='cterm',
                neutralloss='Neutral loss',
                modifications={})),
    },
    "Mascot": {
        "2.1.4, MIME": Version('Mascot', 2, 1, 4,
            format='XML',
            defaults=Defaults(
                query=[
                    "modifications",
                    "num",
                    "peptide",
                    "fraction",
                    "id",
                    "name",
                    "mz",
                    "z",
                    "ppm",
                    "score",
                    "ev"
                ],
                optional_query=None,
                header=[
                    'search_engine="MASCOT"',
                    '<parameter name="FORMAT" value="Mascot generic"/>'
                ],
                delimiter=None,
                decoys=[],
                nterm='nterm',
                cterm='cterm',
                neutralloss='Neutral loss',
                modifications={})),
        "2.1.4, XML": Version('Mascot', 2, 1, 4,
            format='MIME',
            defaults=Defaults(
                query=[
                    "modifications",
                    "num",
                    "peptide",
                    "fraction",
                    "id",
                    "name",
                    "mz",
                    "z",
                    "ppm",
                    "score",
                    "ev"
                ],
                optional_query=None,
                header=['MIME-Version: 1.0 (Generated by Mascot version 1.0)'],
                delimiter=None,
                decoys=[],
                nterm='nterm',
                cterm='cterm',
                neutralloss='Neutral loss',
                modifications={}))
    },
    "Proteome Discoverer": {
        '1.3.0, SQLITE': Version('Proteome Discoverer', 1, 3, 0,
            format='SQLITE',
            defaults=Defaults(
                query=[
                    "modifications",
                    "num",
                    "peptide",
                    "fraction",
                    "id",
                    "name",
                    "mz",
                    "z",
                    "ppm",
                    "score",
                    "ev"
                ],
                optional_query=None,
                decoys=[],
                header={
                    'table': 'SchemaInfo',
                    'column': 'SoftwareVersion',
                    'expected': r'^1\..*$'
                },
                delimiter=None,
                nterm="N-Terminus",
                cterm="C-Terminus",
                neutralloss=None,
                modifications={})),
        '1.3.0, TEXT': Version('Proteome Discoverer', 1, 3, 0,
            format='TEXT',
            defaults=Defaults(
                query=OrderedDict([
                    ("num", [["First Scan"]]),
                    ("peptide", [["Sequence"]]),
                    ("fraction", [["Spectrum File"]]),
                    ("id", [["Protein Group Accessions"]]),
                    ("name", [["Protein Descriptions"]]),
                    ("mz", [["m/z [Da]"]]),
                    ("z", [["Charge"]]),
                    # "ppm": [],
                    ("score", [["IonScore"]]),
                    ("ev", [["Exp Value"]]),
                    ("modifications", [["Modifications"]])
                    # no peptide start position defined
                    # 'start': []
                ]),
                optional_query={"rank": [["Rank"]]},
                decoys=[],
                header=0,
                delimiter='\t',
                nterm="N-Term",
                cterm="C-Term",
                neutralloss=None,
                modifications={})),
        '1.3.0, XML': Version('Proteome Discoverer', 1, 3, 0,
            format='XML',
                defaults=Defaults(
                    query=[
                        "modifications",
                        "num",
                        "peptide",
                        "fraction",
                        "id",
                        "name",
                        "mz",
                        "z",
                        "ppm",
                        "score",
                        "ev"
                    ],
                    optional_query=None,
                    decoys=[],
                    header=['<WorkflowMessages>'],
                    delimiter=None,
                    nterm="nterm",
                    cterm="cterm",
                    neutralloss="Neutral loss",
                    modifications={}))
    }
})
