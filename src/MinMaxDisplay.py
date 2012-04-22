import numpy as N
from traits.api import Property
from traitsui.api import View, Group, Item, Label
from DisplayPlugin import DisplayPlugin

class MinMaxDisplay(DisplayPlugin):

    minimum = Property(depends_on='frame')
    maximum = Property(depends_on='frame')

    view = View(
        Group(
            Item('active'),
            label='Minimum-maximum',
            show_border=True))
    
    def process_frame(self, old_frame, new_frame):
        self.screen.hud('minmax',
            'Minimum: {}\nMaximum: {}'.format(self.minimum, self.maximum))

    def deactivate(self):
        self.screen.hud('minmax', None)

    def _get_minimum(self):
        return self.frame.min()

    def _get_maximum(self):
        return self.frame.max()
