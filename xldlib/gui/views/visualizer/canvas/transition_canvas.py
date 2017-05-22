'''
    Gui/Views/Visualizer/Canvas/transition_canvas
    _____________________________________________

    PyQtGraph canvas for visualizing extracted ion chromatogram
    transitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
import operator as op

from namedlist import namedlist

import numpy as np

import pyqtgraph as pg
import pyqtgraph.exporters

from PySide import QtCore, QtGui

from xldlib.definitions import ZIP
from xldlib.general import mapping
from xldlib.gui.views import widgets
from xldlib.qt.objects import views
from xldlib.qt import resources as qt
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from . import base_canvas, legends, lines, plots

# OBJECTS
# -------

PeakIndexes = namedlist("PeakIndexes", "start end")


# AXIS
# ----


def tickStrings(values, scale, spacing, str_format = '{:.1e}'):
    return [str_format.format(i) for i in values]


# VIEWBOX
# -------


class CustomViewBox(pg.ViewBox):
    '''Definitions for a draggable, resettable view'''

    def __init__(self, canvas):
        super(CustomViewBox, self).__init__()

        self.canvas = canvas
        self.drag_started = False
        self.setMouseMode(self.RectMode)

    #   EVENT HANDLING

    def mouseClickEvent(self, event):
        '''Reimplements the right click event to reset the range'''

        if event.button() == QtCore.Qt.RightButton:
            event.ignore()

    def mouseDragEvent(self, event, axis=0):
        '''Reimplements the right click event to reset the range'''

        if event.button() == QtCore.Qt.LeftButton:
            pg.ViewBox.mouseDragEvent(self, event, axis=0)
        else:
            self.translate(event)

        if event.isFinish():
            self.canvas.store_view()

    #     PANNING

    def translate(self, event):
        '''Copy of partial method from ViewBox.mouseDragEvent'''

        event.accept()

        difference = self.get_difference(event)
        mask = np.array(self.state['mouseEnabled'], dtype=np.float)
        x, y = self.get_transform(difference, mask)

        self._resetTarget()
        if x is not None or y is not None:
            self.translateBy(x=x, y=y)
        self.sigRangeChangedManually.emit(self.state['mouseEnabled'])

    def get_difference(self, event):
        return event.lastPos() - event.pos()

    def get_transform(self, difference, mask):
        '''Returns the (x, y) transformation coordinates'''

        transform = difference * mask
        transform = self.mapToView(transform) - self.mapToView(pg.Point(0,0))
        x = transform.x() if mask[0] == 1 else None
        y = transform.y() if mask[1] == 1 else None

        return x, y


# SELECTION
# ---------


@logger.init('canvas', 'DEBUG')
class SelectedRegion(pg.LinearRegionItem):
    '''Linear region demonstration the current peak selection'''

    # STYLES
    # ------
    brush = QtGui.QBrush(QtGui.QColor(0, 128, 0, 50))

    # TOOLTIP
    # -------
    color = "<b><span style='color:#3f537c'>{0}</span></b>"
    amplitude = ("<p><u>{title}</u><br>"
                 "Area:\t\t" + color.format("{area:.2e}") + "<br>"
                 "Intensity\t" + color.format("{ymax:.2e}") + "</p>")

    def __init__(self, parent, values, bounds):
        super(SelectedRegion, self).__init__(values=values,
            bounds=bounds,
            movable=True,
            brush=self.brush)

        self.setParent(parent)

    def hoverEnterEvent(self, event):
        '''Adds a status bar with the widget's area'''

        self.setToolTip(self.newtooltip())
        super(SelectedRegion, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        '''Kills the status bar with the widget's area'''

        super(SelectedRegion, self).hoverLeaveEvent(event)

    #     HELPERS

    def newtooltip(self):
        '''Initializes a new tooltip for the display'''

        amplitudes = []
        zipper = ZIP(self.parent().group, self.parent().labels.items)
        for child, legend in zipper:
            kwds = self.getkwds(child, legend)
            amplitudes.append(self.amplitude.format(**kwds))
        return ''.join(amplitudes)

    @staticmethod
    def getkwds(child, legend):
        return {
            'title': legend[1].text,
            'area': child.area(),
            'ymax': child.ymax()
        }

# CANVAS
# ------


@logger.init('canvas', 'DEBUG')
class Canvas(pg.PlotWidget, views.BaseView):
    '''Matplotlib canvas with Qt backends'''

    # SIGNALS
    # -------
    position = QtCore.Signal(float, float)

    def __init__(self, parent, group, indexes):
        self.viewbox = CustomViewBox(self)
        super(Canvas, self).__init__(viewBox=self.viewbox)

        self.group = group
        self.indexes = indexes

        self.set_qt(parent)
        self.set_axes()
        self.set_plots()

        # forced show prevents jumped start
        self.show()

    @property
    def use_aa(self):
        return defaults.DEFAULTS['use_antialiasing']

    #     SETTERS

    def set_qt(self, parent):
        '''Sets the Qt paremeters for the canvas'''

        self.setParent(parent)
        self.set_size_policy('Expanding', 'Expanding')
        self.updateGeometry()

    def set_axes(self, tick_size=12):
        '''Initializes and binds the subplot'''

        self.setTitle(self.__gettitle(), size='30pt')
        yaxis = self.plotItem.getAxis('left')
        xaxis = self.plotItem.getAxis('bottom')

        # labels
        kwds = {'font-size': '15pt'}
        yaxis.setLabel(text="<b>Intensity</b>", units="au", **kwds)
        xaxis.setLabel(text="<b>Retention Time</b>", units='min', **kwds)

    def set_vieworder(self):
        '''Stores the next, previous, etc views for the current plot'''

        self.range_views = [self.plotItem.viewRange()]
        self.current_view = 0

    def set_plots(self):
        '''Initializes the current plots along with colors for the layout'''

        self.plotdata = plots.get_plotdata(self.group, self.indexes)
        self.home()

        x = self.plotdata[0].x
        clustered = self.get_clusteredplots()

        self.plots = []
        for pen, y in clustered:
            plot = self.plot(x, y, antialias=self.use_aa, clipToView=True)
            plot.setPen(pen.color, width=pen.width)
            self.plots.append(plot)

        self.set_linear_box()
        self.set_retentiontime()
        self.set_legend()
        self.set_ppm()

    def set_linear_box(self):
        '''Sets a linear box with the '''

        values = lines.get_groupbounds(self.group)
        if values is not None:
            window = self.group.get_labels().get_window_bounds()

            self.selection = SelectedRegion(self, values, list(window))
            self.addItem(self.selection)

            self.selection.sigRegionChanged.connect(self.emit_position)
            self.selection.sigRegionChangeFinished.connect(self.finished)

    def set_retentiontime(self):
        '''Places dashed lines for all RTs the peptide was sequenced'''

        if self.group.levels.labels is not None:
            rts = self.group.get_labels().precursor_rt
            for rt in rts:
                pen = pg.mkPen('k', width=3)
                pen.setDashPattern([2, 4])
                self.addLine(x=rt, pen=pen)

    def set_legend(self):
        '''Adds the legend handle to the widget'''

        items = legends.get_legend(self.group, self.indexes, self.plotdata)
        if items is not None:
            # anchor top-left
            self.labels = pg.LegendItem()
            self.labels.setParentItem(self.viewbox)
            self.labels.anchor((0,0), parentPos=(0,0), offset=(30, 30))

            for index, item in enumerate(items):
                self.labels.addItem(self.plots[index], item)

    def set_ppm(self, bounds=None):
        '''Adds the ppm handle to the widget'''

        ppms = legends.get_ppm(self.group, self.indexes, self.plotdata, bounds)
        if ppms is not None:
            # anchor top-right
            self.ppm = pg.LegendItem()
            self.ppm.setParentItem(self.viewbox)
            self.ppm.anchor((1,0), parentPos=(1,0), offset=(-30, 30))

            for index, ppm in enumerate(ppms):
                self.ppm.addItem(self.plots[index], ppm)

    def set_xrange(self, start, end):
        self.plotItem.setXRange(start, end, padding=0)

    def set_yrange(self, start, end):
        self.plotItem.setYRange(start, end, padding=0)

    #     GETTERS

    def get_bounds(self, axis):
        return getattr(self, 'get_{}range'.format(axis))()

    def get_xrange(self):
        return self.plotItem.viewRange()[0]

    def get_yrange(self):
        return self.plotItem.viewRange()[1]

    def get_clusteredplots(self):
        '''Speeds up plot generation by combining similar colors'''

        clustered = self.__cluster_plots()
        colors = list(clustered)
        length = max(len(i) for i in clustered.values())
        for index in range(length):
            for color in colors:
                if index < len(clustered[color]):
                    yield color, clustered[color][index]

    def __groupby_color(self):
        '''Groups a given series of plotdata by color'''

        colored = mapping.OrderedDefaultdict(list)
        for plot in self.plotdata:
            colored[plot.color].append(plot.y)

        return colored

    def __cluster_plots(self, clusters=3):
        '''Clusters plotdata'''

        clustered = mapping.OrderedDefaultdict(list)
        for color, ydata in self.__groupby_color().items():
            for index in range(clusters):
                items = ydata[index::clusters]
                if items:
                    clustered[color].append(np.max(items, axis=0))
        return clustered

    def __gettitle(self):
        '''Returns the current plot title'''

        if self.group.type == 'file':
            return 'Extracted Ion Chromatograms'
        else:
            return '-'.join(self.group.get_labels().peptide)

    #      VIEWS

    def next(self):
        '''Show the next view'''

        if self.current_view < (len(self.range_views) -  1):
            self.current_view += 1
            self.update_view()

    def previous(self):
        '''Show the previous view'''

        if self.current_view > 0:
            self.current_view -= 1
            self.update_view()

    def zoomin(self, percentage=0.1, axis='x'):
        '''Zoom in the view by a scalar percentage'''

        bounds = self.get_bounds(axis)
        span = - op.sub(*bounds)
        start = bounds[0] + span * percentage
        end = bounds[1] - span * percentage

        getattr(self, 'set_{}range'.format(axis))(start, end)
        self.store_view()

    def zoomout(self, percentage=0.1, axis='x'):
        '''Zoom out the view by a scalar percentage'''

        bounds = self.get_bounds(axis)
        span = - op.sub(*bounds)
        start = bounds[0] - span * percentage
        end = bounds[1] + span * percentage

        getattr(self, 'set_{}range'.format(axis))(start, end)
        self.store_view()

    def update_view(self):
        x_range, y_range = self.range_views[self.current_view]
        self.setRange(xRange=x_range, yRange=y_range, padding=0)

    def store_view(self):
        self.range_views.append(self.plotItem.viewRange())
        self.current_view += 1

    #    EXPORTERS

    def save_image(self, filepath):
        '''Saves an image to disk from the rendering'''

        exporter = pg.exporters.ImageExporter(self.plotItem)
        exporter.export(filepath)

    #     HELPERS

    def home(self):
        '''Sets the home view for the widget'''

        self.set_xrange(*plots.get_xlimit(self.group))
        self.set_yrange(*plots.get_ylimit(self.group, self.plotdata))

        self.set_vieworder()

    def lines(self):
        return sorted(self.selection.lines, key=op.methodcaller('value'))

    def start(self):
        return self.lines()[0]

    def end(self):
        return self.lines()[1]

    def emit_position(self):
        self.position.emit(self.start().value(), self.end().value())

    def finished(self):
        '''Upon ending the linear region movement'''

        self.emit_position()
        self.parent().connect_finish()

    def update_ppm(self, peak):
        self.set_ppm(peak)

    def autoRangeEnabled(self):
        # due to a bug in finding the ViewBox, where the canvas is assumed
        # to be the viewbox
        return self.viewbox.autoRangeEnabled()


# TOOLBAR
# -------

TOOLBAR_ITEMS = [
    'home',
    'previous',
    'next',
    'zoomin',
    'zoomout'
]


class ToolbarIcon(widgets.Push):
    '''Definitions for a toolbar icon'''

    def __init__(self, icon, connect, parent):
        super(ToolbarIcon, self).__init__(icon=qt.IMAGES[icon],
            connect=connect,
            parent=parent)

    def resize(self, size=0.5*qt.INCREMENT):
        self.setFixedSize(size, size)
        self.setIconSize(QtCore.QSize(0.8*size, 0.8*size))


class PyQtGraphToolbar(widgets.Widget):
    '''Definitions for a matplotlib-like toolbar defined as a QWidget'''

    def __init__(self, parent):
        super(PyQtGraphToolbar, self).__init__(parent)

        self.set_layout(QtGui.QHBoxLayout, alignment='Top')
        self.set_widgets()

        self.setFixedHeight(0.7*qt.INCREMENT)

    def set_widgets(self):
        '''Sets the default widgets in the toolbar'''

        for name in TOOLBAR_ITEMS:
            connect = getattr(self.parent().canvas, name)
            push = ToolbarIcon(name, connect, self)
            self.layout.addSpacing(1)
            self.layout.addWidget(push)

        self.layout.addSpacing(20)


# WIDGET
# ------


@logger.init('canvas', 'DEBUG')
class QtGraphWidget(base_canvas.BasePlotItem):
    '''Embeds a PyQtGraph item within a QWidget'''

    # SIGNALS
    # -------
    picked = QtCore.Signal(bool)
    dropped = QtCore.Signal(bool)

    def __init__(self, parent, group, indexes=None):
        super(QtGraphWidget, self).__init__(parent)

        self.group = group
        if indexes is None:
            indexes = range(len(group))

        self.indexes = indexes
        self.xdata = self.group.get_retentiontime()

        self.set_layout(QtGui.QVBoxLayout)
        self.set_focus()
        self.set_canvas()
        self.set_toolbar()

    #     SETTERS

    def set_focus(self):
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()

    def set_canvas(self):
        '''Initializes a FigureCanvas and a dependent instance variables'''

        self.canvas = Canvas(self, self.group, self.indexes)
        self.layout.addWidget(self.canvas)

        self.canvas.position.connect(self.connect_picked)

    def set_toolbar(self):
        '''Adds a toolbar to the bottom of the frame'''

        self.toolbar = PyQtGraphToolbar(self)
        self.layout.addWidget(self.toolbar)

    def set_indexes(self):
        '''Stores the peak indexes on the callbacks'''

        start = self.group.get_labels().window_start
        if self.group.levels.crosslink is not None:
            group = self.group.get_crosslink()
        else:
            group = self.group[0]
        group.set_peak_indexes(self.peak.start - start, self.peak.end - start)

    #     GETTERS

    def get_xindex(self, position):
        '''Returns the nearest index within the xdata to the position'''

        if not hasattr(self, "window_xdata"):
            window = self.group.get_labels().get_window_indexes()
            self.window_xdata = self.xdata[window.start: window.end]
        return np.argmin(np.abs(self.window_xdata - position))

    #  EVENT HANDLING

    def focusInEvent(self, event):
        '''Overrides the main event to ensure the cursor is a wait'''

        event.accept()
        self.app.setOverrideCursor(qt.CURSOR['Arrow'])

    #     HELPERS

    def connect_picked(self, start, end):
        self.store_peak(start, end)
        self.picked.emit(True)

    def store_peak(self, start, end):
        '''Stores peak data from the current widget'''

        window = self.group.get_labels().window_start
        start_index = self.get_xindex(start)
        end_index = self.get_xindex(end)
        self.peak = PeakIndexes(start_index + window, end_index + window)

    def connect_finish(self):
        '''Connected the finished moving signal to update the widget'''

        self.set_indexes()
        self.redraw()
        self.dropped.emit(True)

        del self.peak

    def redraw(self):
        '''Forces the updated linear region to snap to defined points'''

        if defaults.DEFAULTS['patch_to_grid']:
            start, end = self.canvas.lines()
            start.setValue(self.xdata[self.peak.start])
            end.setValue(self.xdata[self.peak.end])

            self.app.processEvents()
