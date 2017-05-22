'''
    Qt/Resources/stylesheets
    ________________________

    Qt stylesheets for widgets

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
from . import fonts

__all__ = [
    'STYLESHEETS'
]

# CONSTANTS
# ---------

APP_WIDTH = 400


# QLISTVIEW
# ---------

QLISTVIEW_STYLE = '''
QListView::item {
    background: #f9f9f9;
    border-left: 2px solid #989898;
    border-right: 2px solid #989898;
    border-top: 1px solid #989898;
    border-bottom: 1px solid #989898;
    padding-top: 3px;
    padding-bottom: 3px;
}

QListView::item:alternate {
    background: #EEEEEE;
}

QListView::item:selected {
    border: 1px solid #6183f7;
}

QListView::item:selected:!active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ABAFE5, stop: 1 #8588B2);
}

QListView::item:selected:active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #6183f7, stop: 1 #888dd9);
}

QListView::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FAFBFE, stop: 1 #DCDEF1);
}
'''


# QLISTWIDGET
# -----------

QLISTWIDGET_STYLE = '''
QListWidget::item {
    border-left: 2px solid #989898;
    border-right: 2px solid #989898;
    border-top: 1px solid #989898;
    border-bottom: 1px solid #989898;
    padding-top: 3px;
    padding-bottom: 3px;
}

QListWidget::item:alternate {
    background: #EEEEEE;
}

QListWidget::item:selected {
    border: 1px solid #6183f7;
}

QListWidget::item:selected:!active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ABAFE5, stop: 1 #8588B2);
}

QListWidget::item:selected:active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #6183f7, stop: 1 #888dd9);
}

QListWidget::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FAFBFE, stop: 1 #DCDEF1);
}
'''

# QTABLEWIDGET
# ------------

QTABLEWIDGET_STYLE = '''
QTableWidget {
    background-color:white;
}
'''


# QLABEL
# ------

QLABEL_STYLE = '''
QLabel {{
    font-weight: bold;
    font-size: {font}pt;
}};
'''

LABEL = QLABEL_STYLE.format(font=fonts.DEFAULT_SIZE)

QLABEL_HEADER_STYLE = '''
QLabel {{
    font-weight: bold;
    font-size: {font}pt;
    border-bottom: 2px outset #545454;
    padding-left: {padding}px;
    padding-right: {padding}px;
    margin-left: {margin}px;
    margin-right: {margin}px;
    padding-top: 10 px;
    padding-bottom: 0 px;
    margin-top: 10 px;
    margin-bottom: 10 px
}};
'''

HEADER = QLABEL_HEADER_STYLE.format(font=fonts.HEADER_SIZE,
    padding=APP_WIDTH/20,
    margin=0)

QLABEL_BANNER_STYLE = '''
QLabel {{
    font-weight: bold;
    font-size: {font}pt;
    alignment: center;
    border-bottom: 4px solid #000000;
}};
'''

BANNER = QLABEL_BANNER_STYLE.format(font=fonts.BANNER_SIZE)

QLABEL_WHITE_BANNER_STYLE = '''
QLabel {{
    font-weight: bold;
    background-color: black;
    font-size: {font}pt;
    color: white;
}};
'''

WHITE_BANNER = QLABEL_WHITE_BANNER_STYLE.format(font=fonts.BANNER_SIZE)

QLABEL_KEY_STYLE = '''
QLabel {
    font-weight: bold;
    background-color: black;
    color: white;
};
'''

QLABEL_DESCRIPTION_STYLE = '''
QLabel {
    background-color: black;
    color: white;
};
'''

# QPUSHBUTTON
# -----------

QPUSHBUTTON_STYLE = '''
QPushButton {{
    border-width: 2px;
    border-color: black;
    padding-left: {padding}px;
    padding-right: {padding}px;
    margin-left: {margin_left}px;
    margin-right: {margin_right}px;
}}

QPushButton:pressed {{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #dadbde, stop: 1 #f6f7fa);
}}

QPushButton:checked {{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #949fc4, stop: 1 #f6f7fa);
}}


QPushButton:default {{
    border-color: navy;
}}
'''

TABLE_BUTTON = QPUSHBUTTON_STYLE.format(padding=0,
    margin_left=0,
    margin_right=0)

BUTTON = QPUSHBUTTON_STYLE.format(padding=0,
    margin_left=APP_WIDTH/32,
    margin_right=APP_WIDTH/20)

DRAG_QPUSHBUTTON_STYLE = '''
QPushButton {{
    border-width: 2px;
    border-color: solid black;
    border-top: 2px solid black;
    border-left: 2px solid black;
    border-bottom: 1px solid black;
    border-right: 1px solid black;
    font-size: {font}pt;
    margin-top: {margin}px;
    margin-bottom: {margin}px;
}};
'''

DRAG_BUTTON = DRAG_QPUSHBUTTON_STYLE.format(font=fonts.DRAG_SIZE,
    margin=8)

CROSSLINKER_QPUSHBUTTON_STYLE = '''
QPushButton {{
    border: 3px solid #6183f7;
    border-radius: 6px;
    font-weight: bold;
    /* font-size: {font}pt; */
}}

QPushButton:pressed {{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #e7e8ea, stop: 1 #f6f7fa);
}}

QPushButton:checked {{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #dadbde, stop: 1 #f6f7fa);
}}

QPushButton:flat {{
    border: none;
}}

QPushButton:default {{
    border-color: navy;
}}'''

GRADIENT_BUTTON = CROSSLINKER_QPUSHBUTTON_STYLE.format(font=fonts.HEADER_SIZE)

# QLINEEDIT
# ----------

QLINEEDIT_STYLE = '''
QLineEdit::hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FAFBFE, stop: 1 #DCDEF1);
}
'''

QSPINBOX_STYLE = '''
QSpinBox:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FAFBFE, stop: 1 #DCDEF1);
}
'''

# QFRAME
# ------

QFRAME_STYLE = '''
QFrame
{{
padding: 5px;
border-style : solid #000000;
border-width: 1px;
margin-left: {margin}px;
margin-right: {margin}px;
}};
'''

FRAME = QFRAME_STYLE.format(margin=0)

# QCHECKBOX
# ---------

QCHECKBOX_STYLE = '''
'''


# QCOMBOBOX
# ---------

QCOMBOBOX_STYLE = '''
QComboBox::hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FAFBFE, stop: 1 #DCDEF1);
};
'''


# QGROUPBOX
# ---------

QGROUPBOX_STYLE = '''
QGroupBox
{
    border: 5px solid black; background-color: white
};
'''

# QLISTWIDGET
# -----------

QLIST_STYLE = '''
QListWidget::item {
    border-style: outset;
    border-width: 0.5px;
    border-color: black;
};
QListWidget::item:selected {
    background-color: blue;
};
'''

# QMENU
# -----

QMENU_STYLE = '''
QMenu::item:selected {
    background-color: blue;
};
'''

# QPROGRESSBAR
# ------------

QPROGRESSBAR_STYLE = '''
QProgressBar {
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #CD96CD;
    width: 10px;
    margin: 0.5px;
}
'''

# QDIALOG
# -------

QDIALOG_STYLE = '''
QDialog {
    background: #000000;
}
'''


# DATA
# ----

STYLESHEETS = {
    'banner': BANNER,
    'header': HEADER,
    'label': LABEL,
    'bannerwhite': WHITE_BANNER,
    'button': BUTTON,
    'drag_button': DRAG_BUTTON,
    'gradient_button': GRADIENT_BUTTON,
    'table_button': TABLE_BUTTON,
    'frame': FRAME,
    'lineedit': QLINEEDIT_STYLE,
    'spinbox': QSPINBOX_STYLE,
    'listview': QLISTVIEW_STYLE,
    'listwidget': QLISTWIDGET_STYLE,
    'table': QTABLEWIDGET_STYLE,
    'keywhite': QLABEL_KEY_STYLE,
    'descriptionwhite': QLABEL_DESCRIPTION_STYLE,
    'checkbox': QCHECKBOX_STYLE,
    'combobox': QCOMBOBOX_STYLE,
    'groupbox': QGROUPBOX_STYLE,
    'list': QLIST_STYLE,
    'menu': QMENU_STYLE,
    'progressbar': QPROGRESSBAR_STYLE,
    'dialog': QDIALOG_STYLE,
}
