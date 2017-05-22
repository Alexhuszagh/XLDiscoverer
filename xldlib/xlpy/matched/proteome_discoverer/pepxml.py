'''
    XlPy/matched/Proteome_Discoverer/pepxml
    _______________________________________

    Implementation-specific parser for Proteome Discoverer pepXML
    formats.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import copy

from models import params
from xldlib.utils import masstools



class StartProteomeDiscoverer(object):
    '''
    Utilities for processing data from XML start elements,
    whcih differs significantly version to version.
    Very atypically, the massdiff for each ID compared to the
    theoretical sequence is reported as 0, so no PPMs can be
    reported and must be calculated.

    Mods are also reported differently, rather than using
    <aminoacid_modification, <terminal_modification> nodes,
    it specifies
    <parameter name="DynModification" value="Name / Mass" Da (Residue)/>
    '''

    _moddec = 3

    def modifications(self, attrs):
        '''Stores the mass modifications from the header'''

        modname, mass = attrs['value'].split('/')
        # trailing and leading spaces
        modname = modname.strip()
        mass = str(round(float(mass.split()[0]), self._moddec))
        if attrs['name'].startswith('DynModification'):
            key = 'mass'
        elif attrs['name'].startswith('DynTerminalModification'):
            key = 'massdiff'

        self._modifications[key][mass] = modname

    def scan(self, attrs):
        '''Initializes the scan data and sets base attributes'''

        self._scan = {}
        self._scan['num'] = int(attrs['start_scan'])
        self._scan['z'] = charge = int(attrs.get('assumed_charge', 1))
        self._scan['fraction'] = self._fraction

        # the neutral mass is actually MH+ in the specification
        mh_plus_mass = float(attrs['precursor_neutral_mass'])
        neutral_mass = mh_plus_mass - params.PROTON_MASS
        self._scan['m/z'] = masstools.mz(neutral_mass, charge, 0)

    def hit(self, attrs):
        '''Processes an individual hit from various candidates'''

        rank = int(attrs['hit_rank'])
        mods = copy.deepcopy(params.TEMPLATES['mods'])
        hit = {'mods': mods, 'rank': rank}
        self._hit = len(self._hits)
        self._hits.append(hit)

        hit['peptide'] = attrs['peptide']
        hit['id'] = attrs['protein']
        hit['name'] = attrs['protein_descr']

    def score(self, attrs):
        '''Processes the score values form a search hit'''

        hit = self._hits[self._hit]
        if attrs['name'] == "Exp Value":
            hit['ev'] = float(attrs["value"])
        if attrs['name'] == "IonScore":
            hit['score'] = float(attrs["value"])

    def term_mods(self, attrs):
        '''Processes each mod for terminal modifications from the element'''

        keys = [i for i in self._term_keys if i in attrs.keys()]
        for mass_key in keys:
            self._store_mod(attrs, mass_key)

    def intern_mods(self, attrs):
        '''Processes each mod for internal modifications from the element'''

        self._store_mod(attrs)

    # ------------------
    #       UTILS
    # ------------------

    def _store_mod(self, attrs, mass_key="mass"):
        '''
        Stores a given mod data, which can either be from the
        name == 'mod_aminoacid_mass' or name == 'modification_info' tags.
        '''

        if mass_key == 'massdiff':
            import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        mass = str(round(float(attrs[mass_key]), self._moddec))
        # grab mod name and make blank list if not in
        # internal mods use mass
        # need to convert to 4 decimal accuracy since older pepXML specs
        # do not have identical accuracy for mods
        key = self._get_modkey(mass_key)
        mod_name = self._modifications[key][mass]

        # pep xml schema doesn't have uncertain mods, so... grab hit
        hit = self._hits[self._hit]
        hit['mods']['certain'].setdefault(mod_name, [])

        pos = self._get_pos(mass_key, attrs)
        hit['mods']['certain'][mod_name].append(pos)

    @staticmethod
    def _get_modkey(mass_key):
        '''Returns the modification key whether the mod is term or intern'''

        if mass_key == 'mass':
            key = 'mass'
        # nterm mods use massdiff
        else:
            key = 'massdiff'

        return key

    @staticmethod
    def _get_pos(mass_key, attrs):
        '''Grabs the position whether mod is term or intern'''

        if mass_key == 'mass':
            pos = int(attrs['position'])
        elif mass_key == 'mod_nterm_mass':
            pos = 'nterm'
        elif mass_key == 'mod_cterm_mass':
            pos = 'cterm'

        return pos


class EndProteomeDiscoverer(object):
    '''Utilities for processing data from XML end elements'''


class ProteomeDiscoverer(StartProteomeDiscoverer, EndProteomeDiscoverer):
    '''pepXML-specific startElement and endElement processing functions'''

    _term_keys = ['mod_nterm_mass', 'mod_cterm_mass']

    def __init__(self, fraction):
        super(ProteomeDiscoverer, self).__init__()

        self._fraction = fraction
        # store modifications as mass: name, since they appear
        # in the schema later as mass
        self._modifications = {'mass': {}, 'massdiff': {}}
