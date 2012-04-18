import numpy as N
from traits.api import HasTraits, Bool, Array, Instance, Property
from traitsui.api import View, Group, Item, Label
from CameraImage import CameraImage

class MinMaxDisplay(HasTraits):

    active = Bool(False)
    frame = Array(dtype=float)
    screen = Instance(CameraImage)
    minimum = Property(depends_on='frame')
    maximum = Property(depends_on='frame')

    view = View(
        Group(
            Item('active'),
            label='Minimum-maximum',
            show_border=True))
    
    def _frame_changed(self, frame):
        if not self.active:
            return

        self.screen.hud('minmax',
            'Minimum: {}\nMaximum: {}'.format(self.minimum, self.maximum))

    def _active_changed(self, value):
        if not value:
            self.screen.hud('minmax', None)

    def _get_minimum(self):
        return self.frame.min()

    def _get_maximum(self):
        return self.frame.max()
