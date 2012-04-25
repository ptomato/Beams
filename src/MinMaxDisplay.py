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

    def __init__(self, **traits):
        super(MinMaxDisplay, self).__init__(**traits)
        self.on_trait_change(self._update_hud, '_minimum,_maximum',
            dispatch='ui')

    def _update_hud(self):
        self.screen.hud('minmax',
            'Minimum: {0._minimum}\n'
            'Maximum: {0._maximum}'.format(self))

    def _process(self, frame):
        self._minimum = frame.min()
        self._maximum = frame.max()

    def deactivate(self):
        self.screen.hud('minmax', None)
