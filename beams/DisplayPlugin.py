import numpy as N
from traits.api import HasTraits, Bool, Instance
from CameraImage import CameraImage


class DisplayPlugin(HasTraits):

    active = Bool(False)
    screen = Instance(CameraImage)

    def process_frame(self, frame):
        if not self.active:
            return

        # Make sure we are operating on a copy, since the array can change
        self._process(N.array(frame, dtype=float, copy=True))

    def _active_changed(self, value):
        if value:
            self.activate()
        else:
            self.deactivate()

    def _process(self, frame):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass
