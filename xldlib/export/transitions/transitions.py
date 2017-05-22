'''
    Export/Transitions/transitions
    ______________________________

    Generates the transition list dataframes and sheets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op

from collections import defaultdict, namedtuple

from xldlib.definitions import ZIP
from xldlib.export.dataframes import quantitative
from xldlib.objects.abstract import dataframe
from xldlib.qt.objects import base
from xldlib.resources.parameters import reports
from xldlib.utils import logger, xictools


# OBJECTS
# -------

Crosslink = namedtuple("Crosslink", "linkname linktype")
Sheet = namedtuple("Sheet", "title")
Column = namedtuple("Column", "name type join")


# COLUMNS
# -------


SPREADSHEET = [
    Column('Search Name', quantitative.ColumnTypes['null'], False),
    Column('DB Peptide', quantitative.ColumnTypes['null'], True),
    Column('Protein Mods', quantitative.ColumnTypes['labeled'], True),
]

XIC = [
    'Charge',
    'Isotope'
]


# DATAFRAMES
# -----------


@logger.init('spreadsheet', 'DEBUG')
class Dataframe(dataframe.DataFrameDict):
    '''Export dataframe for the transition list parameters'''

    def __init__(self, profile, mixing):
        super(Dataframe, self).__init__()

        self.profile = profile
        self.mixing = mixing
        self.columns = None

    @logger.call('spreadsheet', 'debug')
    def __call__(self, labels, key='area'):
        '''Adds the data to each set of columns and initiate rows'''

        length = len(labels.peptide)
        headers = self.profile.getheaders(length, self.mixing)

        for index, isotopes in enumerate(self.iter(labels)):
            if index:
                row = {}
            else:
                row = self.getrowtemplate(labels, headers[0])

            levels = isotopes[0].levels
            row['Charge'] = levels.charge
            row['Isotope'] = levels.isotope

            amplitudes, noise = self.getamplitudes(isotopes, headers, row, key)
            row['Ratio'] = xictools.Ratios(amplitudes, noise).tostr()

            index = self.get_last_index()
            self.loc[index] = row

        self.set_sums(labels, headers, key)
        self.set_value()

    #     SETTERS

    def set_version(self):
        self.set_header()
        self.set_value()

    def set_dimensions(self, lengths):
        '''Returns the maximum crosslink dimensions among the crosslinks'''

        headers = self.profile.getheaders(lengths, self.mixing)
        columns = [i.name for i in SPREADSHEET] + XIC + headers + ['Ratio']
        self.set_columns(columns)

    def set_sums(self, labels, headers, key):
        '''Sets a row total for the summed amplitude and ratios'''

        row = {'Isotope': 'Sum'}
        used = labels.getusedcharges()

        integrated = [i.integrate_data(used) for i in labels]
        amplitudes = [op.attrgetter(key+'.value')(i) for i in integrated]
        for (amplitude, header) in ZIP(amplitudes, headers):
            row[header] = amplitude
        row['Ratio'] = xictools.Ratios.fromintegrated(key, integrated).tostr()

        index = self.get_last_index()
        self.loc[index] = row

    #    GETTERS

    def getrowtemplate(self, labels, header):
        '''Generates a row to add to the dataframe'''

        row = {}
        spreadsheet = labels.spreadsheet
        for column in SPREADSHEET:
            row[column.name] = self.getvalues(column, spreadsheet, header)
        return row

    def getamplitudes(self, isotopes, headers, row, key):
        '''Returns the function processed data for the spectral amplitude'''

        integrated = []
        noises = []
        for (isotope, header) in ZIP(isotopes, headers):
            noise = op.methodcaller(key)(isotope)
            if isotope.ischecked():
                row[header] = integral = noise
            else:
                row[header] = integral = float('nan')
            integrated.append(integral)
            noises.append(noise)

        return integrated, noises

    @staticmethod
    def getvalues(column, spreadsheet, header):
        '''Processes the values to an exportable Python type'''

        if column.type == quantitative.ColumnTypes['null']:
            values = spreadsheet[(' ', column.name)]

        else:
            values = spreadsheet[(header, column.name)]

        if column.join:
            return ' - '.join(values)
        else:
            return values[0]

    #    HELPERS

    def iter(self, labels):
        '''Returns an iterator returning all crosslinks from the same charge'''

        for charges in ZIP(*labels):
            for isotopes in ZIP(*charges):
                yield isotopes


# WORKSHEETS
# ----------


class TransitionWorkSheets(base.BaseObject):
    '''Generates the worksheets for dataframe creation'''

    @logger.call('spreadsheet', 'debug')
    def __call__(self, document, key='area'):
        '''On call'''

        # no key required, since the values are tuples of enums
        crosslinks = self.getcrosslinks(document)
        return zip(*self.getdataframes(document, crosslinks, key))

    #     GETTERS

    def getcrosslinks(self, document):
        '''Returns a unique list of Crosslink instances in the document'''

        crosslinks = defaultdict(list)
        with document.togglememory():
            for transition_file in document:
                for labels in transition_file:

                    item = Crosslink(*map(labels.getattr, Crosslink._fields))
                    crosslinks[item].append(labels)

        return crosslinks

    def getdataframes(self, document, crosslinks, key):
        '''Generates a dummy sheet instance for title purposes'''

        profile = document.profile
        mixing = document.include_mixed_populations
        for item in sorted(crosslinks):
            report = reports.REPORTS[item.linkname, item.linktype]
            sheet = Sheet("Transition {}".format(report.name))

            dataframe = Dataframe(profile, mixing)
            labels_list = crosslinks[item]
            lengths = {len(i.peptide) for i in labels_list}
            dataframe.set_dimensions(lengths)
            dataframe.set_version()

            for labels in labels_list:
                dataframe(labels, key)

            yield sheet, dataframe

