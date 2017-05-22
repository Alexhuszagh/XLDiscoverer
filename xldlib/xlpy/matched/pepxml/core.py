'''
    XlPy/matched/PepXML/core
    ________________________

    Main parser for pepXML, toggleable with various search engine
    specifications.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import xml.sax

from xldlib.utils import logger

from . import mascot, protein_prospector, proteome_discoverer

# DATA
# ----

DYNAMIC_MODS = (
    'DynModification',
    'DynTerminalModification'
)

MODULES = {
    'Protein Prospector': protein_prospector,
    'Mascot': mascot,
    'Proteome Discoverer': proteome_discoverer
}


# HANDLERS
# --------


@logger.init('matched', 'DEBUG')
class PepXmlHandler(xml.sax.handler.ContentHandler):
    '''xml.sax parser for the pepXML file formats'''

    # BUGS
    # ----
    # Proteome Discoverer has nested search_summary nodes,
    # so need to ensure proper one is selected
    _search_summary = False

    def __init__(self, row):
        xml.sax.ContentHandler.__init__(self)

        self.row = row

        name = row.data['attrs']['engines']['matched'][0]
        module = MODULES[name]
        self.start = module.Start()
        self.end = module.End()

    #    XML ELEMENTS

    def startElement(self, name, attrs):
        '''XML element started'''

        if name == 'msms_run_summary':
            self._search_summary = True

        elif name == 'sample_enzyme':
            self.row.data['attrs']['enzyme'] = attrs['name']

        # grab general search summary data
        elif name == "search_summary" and self._search_summary:
            self.start.fraction(attrs)

        # process intro modifications
        elif name in {"aminoacid_modification", "terminal_modification"}:
            self.start.modifications.store(attrs)

        elif name == 'parameter' and self._search_summary:
            # only for Proteome Discoverer, also has null databases to ignore
            if attrs['name'].startswith(DYNAMIC_MODS) and attrs['value']:
                self.start.modifications.store(attrs)

        elif name == "spectrum_query":
            self.start.scan(attrs)
            self._scan = self.start._scan

        elif name == "search_hit":
            self.start.hit(attrs)

        elif name == "search_score":
            self.start.score(attrs)

        elif name == 'modification_info':
            self.start.terminal(attrs)

        elif name == "mod_aminoacid_mass":
            self.start.internal(attrs)

    def endElement(self, name):
        '''XML element ended'''

        if name == 'msms_run_summary':
            self._search_summary = False

        elif name == 'spectrum_query':
            self.row.data.newscan(self._scan)
            self._scan = None
