'''
    Gui/Views/Visualizer/Styles/colorer
    ___________________________________

    HTML-based colorer for the current QTreeView delegate.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from collections import defaultdict

from xldlib.definitions import ZIP
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.resources import engines
from xldlib.utils import logger, math_

from .. import base


# DATA
# ----

TRANSITION_COLORS = {
    'crosslinker': 'blue',
    'isotope_label': 'green',
    'standard': 'red'
}
HTML_COLOR = "<font color={0}>{1}</font>"


# PEPTIDES
# --------


@logger.init('document', 'DEBUG')
class TransitionPeptides(base.DocumentChild):
    '''Adds HTML-style labels to a peptide list'''

    def __init__(self, parent):
        super(TransitionPeptides, self).__init__(parent)

    def __call__(self, labels):
        '''Returns a colorized peptide from the labels HDF5 group'''

        if not hasattr(labels, "treeview"):
            treeview = self.treeview(labels)
            labels.setattr('treeview', treeview)
            return treeview
        return labels.treeview

    def treeview(self, labels):
        '''Creates an HTML-colorized peptide'''

        # use a copy to avoid writing to file
        peptides = labels.peptide[:]
        modifications = labels[0].modifications
        certain = [i['certain'] for i in modifications]

        zipped = ZIP(peptides, certain)
        for index, (peptide, modification) in enumerate(zipped):
            peptides[index] = self.getcolors(peptide, modification)

        return ' - '.join(peptides)

    #      SETTERS

    def setattrs(self):
        '''Sets the base attributes to extract the modification positions'''

        self.setfragments()
        self.setisotopelabels()

        # create a position key from the engin e
        profile = self.document.profile
        self.engine = engines.SEARCH[profile.engine][profile.version]

    def setfragments(self):
        '''Sets the crosslinker fragments from the document'''

        self.fragments = defaultdict(list)
        fragments = self.document.fragments
        for modification in fragments.values():
            self.fragments[modification.name].append(modification)

    def setisotopelabels(self):
        '''Sets the isotope labels from the document'''

        self.isotope_labels = defaultdict(list)
        profile = self.document.profile
        for population in profile.populations:
            for modification in population.getmodifications():
                self.isotope_labels[modification.name].append(modification)

    #      GETTERS

    def getcolors(self, peptide, modification):
        '''Colors the peptide based on modifications and positions'''

        grouped = self.getgrouped(peptide, modification)
        positions = sorted(grouped, reverse=True)
        for position in positions:
            names = grouped[position]
            if any(i in self.fragments for i in names):
                peptide = self.format_position(
                    peptide, position, 'crosslinker')
            elif any(i in self.isotope_labels for i in names):
                peptide = self.format_position(
                    peptide, position, 'isotope_label')
            else:
                peptide = self.format_position(peptide, position, 'standard')

        return peptide

    def getgrouped(self, peptide, modification):
        '''Returns the modifications grouped by position'''

        positions = modification.byposition()
        keys = list(positions)
        for key in keys:
            newkey = self.engine.inpeptide(key, peptide)
            positions[newkey] = positions.pop(key)

        return positions

    #     FORMATTERS

    @staticmethod
    def format_position(peptide, position, modification_type):
        '''adds an HTML color to the peptide at the position'''

        residue = peptide[position]
        color = TRANSITION_COLORS[modification_type]

        return (peptide[:position] +
            HTML_COLOR.format(color, residue) +
            peptide[position + 1:])


@logger.init('document', 'DEBUG')
class FingerprintPeptides(base.DocumentChild):
    '''Adds HTML-style labels to a peptide list'''

    def __init__(self, parent):
        super(FingerprintPeptides, self).__init__(parent)

    def __call__(self):
        pass

    #      SETTERS

    def setattrs(self):
        pass


# STRINGS
# -------

RED_HYPHEN = "<font color=red>-</font>"
FONT_ELEMENT = ' <font'
SCORE_STRING = '{{0}} {{1}} {{2}} {{3:0.{0}f}}'


# STYLES
# ------


@logger.init('document', 'DEBUG')
class Stylizer(base.DocumentChild):
    '''Provides methods to color items within the QTreeView'''

    # QT
    # --

    _qt = qt_config.TRANSITIONS

    def __init__(self, fileformat, parent):
        super(Stylizer, self).__init__(parent)

        self.set_format(fileformat)

    def __call__(self, child, group):
        '''Sets the icon and HTML formatting for the child'''

        if hasattr(group, 'dotp'):
            self.set_dotp(child, group.dotp)

        elif hasattr(group, 'gaussian'):
            self.set_gaussian(child, group.gaussian)

    def crosslinks(self, group):
        '''Sets the name for cross-link level peptides'''

        populations = group.populations
        profile = group.get_document().profile
        headers = [profile.populations[i].header for i in populations]

        return ' {} '.format(RED_HYPHEN).join(headers)

    #      SETTERS

    def set_format(self, fileformat):
        '''Sets the current stylizer format {'transition', 'fingerprint'}'''

        self.fileformat = fileformat
        if fileformat == 'transition':
            self.peptides = TransitionPeptides(self.parent())

        elif fileformat == 'fingerprint':
            self.peptides = FingerprintPeptides(self.parent())

    def setattrs(self):
        self.peptides.setattrs()

    def set_dotp(self, child, score):
        self.set_icon(child, score, self.qt['dotp_thresholds'])
        self.set_score(child, score, 'dotp')

    def set_gaussian(self, child, score):
        self.set_icon(child, score, self.qt['gaussian_thresholds'])
        self.set_score(child, score, 'corr')

    def set_score(self, child, score, name):
        '''
        Sets the scoring parameter in the child name, assuming the
        name has not been priorly added to the child.
        '''

        text = child.text().split(FONT_ELEMENT)[0]

        if math_.isnan(score):
            score = 0
            string = SCORE_STRING.format(1)
        elif math_.isinf(score):
            score = 1
            string = SCORE_STRING.format(1)
        else:
            # 2 decimals if 0 < score < 1, else 1
            string = SCORE_STRING.format(2)

        child.setText(string.format(text, RED_HYPHEN, name, score))

    def set_icon(self, child, score, thresholds):
        '''
        Sets the icon of a dot given the available thresholds and
        the value relative to them. The thresholds are tristate, ie,
        it's above all, 1/2, or none of the two.
        '''

        if score > thresholds.upper:
            child.setIcon(qt.IMAGES['green_dot'])
        elif score > thresholds.lower:
            child.setIcon(qt.IMAGES['orange_dot'])
        else:
            child.setIcon(qt.IMAGES['red_dot'])
