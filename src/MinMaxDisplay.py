import numpy as N
from traits.api import Float, on_trait_change
from traitsui.api import View, Group, Item
from DisplayPlugin import DisplayPlugin

class MinMaxDisplay(DisplayPlugin):

    _minimum = Float()
    _maximum = Float()

    view = View(
        Group(
            Item('active'),
            label='Minimum-maximum',
            show_border=True))

    @on_trait_change('_minimum,_maximum')
    def _update_hud(self):
        self.screen.hud('minmax',
            'Minimum: {}\nMaximum: {}'.format(self._minimum, self._maximum))

    def _process(self, frame):
        self._minimum = frame.min()
        self._maximum = frame.max()

    def deactivate(self):
        self.screen.hud('minmax', None)
