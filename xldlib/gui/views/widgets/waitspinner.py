'''
    Original Work Copyright (c) 2012-2014 Alexander Turkin
    Modified 2014 by William Hallatt
    Modified 2015 by Jacob Dawid
    Ported to Python3 2015 by Luca Weiss
    Modified 2015 by Alex Huszagh, to port to PySide and support both Python2
        and Python3, as well as add PEP8-compliance.

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject
    to the following conditions: The above copyright notice and this
    permission notice shall be included in all copies or substantial
    portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# load modules
import copy
import math

from PySide import QtCore, QtGui


# SPINNER
# -------


class QtWaitingSpinner(QtGui.QWidget):
    '''
    Definitions for a loading spinner, with translucent lines
    spinning on another QWidget.
    '''

    def __init__(self, parent, **kwds):
        super(QtWaitingSpinner, self).__init__(parent)

        self._center_parent = kwds.get('center_parent', True)
        self._disable_parent = kwds.get('disable_parent', True)

        self.initialize()
        self.setWindowModality(kwds.get('modality', QtCore.Qt.NonModal))
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    #  EVENT HANDLING

    def paintEvent(self, event):
        '''Repaint the widget to translate the lines'''

        self.update_position()
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtCore.Qt.transparent)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        if self._counter >= self.lines:
            self._counter = 0

        painter.setPen(QtCore.Qt.NoPen)
        for index in range(0, self.lines):
            painter.save()
            adjust = self.inner_radius + self.line_length
            painter.translate(adjust, adjust)

            rotate_angle = float(360 * index) / float(self.lines)
            painter.rotate(rotate_angle)
            painter.translate(self.inner_radius, 0)
            distance = self.line_distance(index)
            color = self.line_color(distance)
            painter.setBrush(color)

            rect = QtCore.QRect(0, -self.line_width / 2,
                self.line_length, self.line_width)
            painter.drawRoundedRect(rect, self.roundness,
                self.roundness, QtCore.Qt.RelativeSize)
            painter.restore()

    #     PUUBLIC

    def initialize(self):
        '''Initializes the spinner with default parameters'''

        self._color = QtGui.QColor(QtCore.Qt.black)
        self._roundness = 100.0
        self._min_opacity = 3.14159265358979323846
        self._tail_fade = 80.0
        self._periodicity = 1.57079632679489661923
        self._lines = 20
        self._line_length = 10
        self._line_width = 2
        self._inner_radius = 10
        self._counter = 0
        self._spinning = False

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.rotate)
        self.update_size()
        self.update_timer()
        self.hide()

    def start(self):
        '''Start spinning'''

        self.update_position()
        self._spinning = True
        self.show()

        if self.parent and self._disable_parent:
            self.parent().setEnabled(False)

        if not self._timer.isActive():
            self._timer.start()
            self._counter = 0

    def stop(self):
        '''Stop spinning'''

        self._spinning = False
        self.hide()

        if self.parent() and self._disable_parent:
            self.parent().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._counter = 0

    #    PROPERTIES

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color=QtCore.Qt.black):
        self._color = QtGui.QColor(color)

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, value):
        self._lines = value
        self._counter = 0
        self.update_timer()

    #    LINE LENGTH

    @property
    def line_length(self):
        return self._line_length

    @line_length.setter
    def line_length(self, value):
        '''Sets the length of lines visible on the widget.'''

        self._line_length = value
        self.update_size()

    #    LINE WIDTH

    @property
    def line_width(self):
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        '''Sets the width of lines visible on the widget.'''

        self._line_width = value
        self.update_size()

    @property
    def roundness(self):
        return self._roundness

    @roundness.setter
    def roundness(self, value):
        self._roundness = max(0.0, min(100.0, value))

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        self._inner_radius = value
        self.update_size()

    @property
    def periodicity(self):
        return self._periodicity

    @periodicity.setter
    def periodicity(self, value):
        '''Sets the number of revolution per second, related to period'''

        self._periodicity = value
        self.update_timer()

    @property
    def tail_fade(self):
        return self._tail_fade

    @tail_fade.setter
    def tail_fade(self, value):
        self._tail_fade = value

    @property
    def min_opacity(self):
        return self._min_opacity

    @min_opacity.setter
    def min_opacity(self, value):
        self._min_opacity = value

    @property
    def spinning(self):
        return self._spinning

    #     PUBLIC

    def rotate(self):
        '''Updates the view by spinning the lines'''

        self._counter += 1
        if self._counter >= self.lines:
            self._counter = 0
        self.update()

    def update_size(self):
        size = (self.inner_radius + self.line_length) * 2
        self.setFixedSize(size, size)

    def update_timer(self):
        '''Sets the timer interval for the timeout'''

        period = self.lines * self.periodicity
        self._timer.setInterval(1000 / period)

    def update_position(self):
        '''Moves the spinner position relative to the parent widget'''

        if self.parent() and self._center_parent:
            width = self.parent().width() / 2 - self.width() / 2
            height = self.parent().height() / 2 - self.height() / 2
            self.move(width, height)

    def line_distance(self, current):
        '''Returns the line distance relative the the primary line'''

        distance = self._counter - current
        if distance < 0:
            distance += self.lines
        return distance

    def line_color(self, distance):
        '''Returns the current line color while painting'''

        color = copy.deepcopy(self.color)
        if distance == 0:
            return color
        min_alpha_f = self.min_opacity / 100.0

        threshold = (self.lines - 1) * self.tail_fade / 100.0
        distance_threshold = int(math.ceil(threshold))
        if distance > distance_threshold:
            color.setAlphaF(min_alpha_f)
        else:
            alpha_diff = color.alphaF() - min_alpha_f
            gradient = alpha_diff / float(distance_threshold + 1)
            resultAlpha = color.alphaF() - gradient * distance
            # If alpha is out of bounds, clip it.
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color
