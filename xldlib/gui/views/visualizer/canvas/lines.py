'''
    Gui/Views/Visualizer/Canvas/lines
    _________________________________

    Pickable rectangles with an adjustable width for defining peak
    bounds.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# BOUNDS
# ------


def get_groupbounds(group):
    '''Returns the start and end bounds for the retention times'''

    if group.levels.crosslink is not None:
        return group.get_crosslink().get_peak_bounds()

    elif (group.get_document().retentiontime_lock
          and group.levels.labels is not None):
        return group.get_labels()[0].get_peak_bounds()
