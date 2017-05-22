'''
    Gui/Views/Crosslink_Discoverer/Profiles/base
    ____________________________________________

    Base classes for the profile views.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.controllers import bindings


# CLASSES
# -------


class ViewChild(bindings.Keys):
    '''Defines properties for the childl of a profiles instance'''

    #    PROPERTIES

    @property
    def index(self):
        return self.parent().index

    @index.setter
    def index(self, value):
        self.parent().index = value

    @property
    def profile(self):
        return self.parent().profile

    @profile.setter
    def profile(self, value):
        self.parent().profile = value



class TableChild(bindings.Keys):
    '''Defines properties for the childl of a profiles instance'''

    #    PROPERTIES

    @property
    def table(self):
        return self.parent().parent()

    @property
    def index(self):
        return self.table.index

    @index.setter
    def index(self, value):
        self.table.index = value

    @property
    def profile(self):
        return self.table.profile

    @profile.setter
    def profile(self, value):
        self.table.profile = value
