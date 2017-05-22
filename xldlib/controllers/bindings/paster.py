'''
    Controllers/Bindings/paster
    ___________________________

    Inheritable methods to exec copy operations in QTableWidgets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib import exception
from xldlib.controllers import messages
from xldlib.general import mapping


# PASTER
# ------


class HandlePaste(messages.BaseMessage):
    r'''
    Excel-like paste function. Pastes selection into selected cells,
    splitting '\t' separators and '\n' newlines. Warns user about possible
    cropped data/missing data.
        (Row, Column) [Value] Selection:
        AA\tBB\nCC\t\DD
        --> (1,2) ["AA"], (1,3) ["BB"], (2,2) ["CC"], (2,3) ["DD"]
    '''

    def __init__(self, table):
        super(HandlePaste, self).__init__(table)

        self.table = table

    # PUBLIC FUNCTIONS

    def paste(self, clipboard_text):
        '''
        Paste data from the clipboard into the QTable after all possible
        validation/warnings.
            exec_paste(<PySide.QtGui.QTableWidget ...>,
                {'A': [..], 'B': [...]},
                       [['2', 'J'], ['D', 'E']], (0, 1), (1, 2))->void
        '''

        paste = self.get_clipboard(clipboard_text)
        if paste:
            selection = self.table.get_selected_indexes()
            selectionrange = self.table.selection.fromiter(*zip(*selection))
            pasterange = self.get_paste_dimensions(paste)

            if self.check_paste(selectionrange, pasterange):
                start = selection[0]
                self.set_row_count(start, pasterange)
                self.table.paste(paste, start)

                if hasattr(self.table, "changed"):
                    self.table.changed = True

    #     SETTERS

    def set_row_count(self, start, pasterange):
        '''Sets a new row count'''

        oldrows = self.table.rowCount()
        rows = start.row + pasterange.rows.max + 1
        if rows > oldrows:
            self.table.setRowCount(rows)

            for row in range(oldrows, rows):
                self.table.set_comboboxes(row)

    #     GETTERS

    def get_clipboard(self, clipboard_text, delimiter='\t'):
        '''
        Grab clipboard and process dimensions.
            get_clipboard()->[['A', 'B'], ['C', 'D'], ['E', 'F']] # (2x3)
        '''

        lines = clipboard_text.splitlines()

        values = mapping.OrderedDefaultdict(list)
        for line in lines:
            for index, value in enumerate(line.split(delimiter)):
                values[index].append(value)
        return values

    def get_paste_dimensions(self, values):
        '''Returns the current selection dimensions'''

        rows = len(next(iter(values.values())))
        columns = len(values)
        return self.table.selection.fromint(0, rows, 0, columns)

    #     HELPERS

    @messages.warningbox(AssertionError, btn_names=['Yes', 'No'])
    def check_paste(self, selectionrange, pasterange):
        '''Checks whether data loss would occur upon an attempted paste'''

        if selectionrange.columns.max > self.table.columnCount():
            raise AssertionError(exception.CODES['005'])

        if not self.equal_dimensions(selectionrange, pasterange):
            raise AssertionError(exception.CODES['006'])

        return True

    def equal_dimensions(self, selectionrange, pasterange):
        '''
        Returns whether dimensions of selection_list and values
        are identical, or single cell was copied or selected.
        :
            rows -- Axis instance for rows
            columns -- Axis instance for columns
            values -- list of '\t'-split data
            equal_dim([[0, 0], [0, 1]], [['A', 'J']], 'A\tB')->False
        '''

        zeroed = selectionrange.tozero()
        if zeroed == pasterange:
            return True

        elif all(i.max == 1 for i in zeroed):
            # single item selected
            return True

        else:
            # single item pasting
            return all(i.max == 1 for i in pasterange)
