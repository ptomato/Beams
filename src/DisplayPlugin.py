from traits.api import HasTraits, Bool, Array, Instance
from CameraImage import CameraImage

class DisplayPlugin(HasTraits):

    active = Bool(False)
    frame = Array(dtype=float)
    screen = Instance(CameraImage)

    def _frame_changed(self, old_frame, new_frame):
        if not self.active:
            return
        self.process_frame(old_frame, new_frame)

    def _active_changed(self, value):
        if value:
            self.activate()
        else:
            self.deactivate()

    def process_frame(self, old_frame, new_frame):
        pass

    def activate(self):
        pass
   
    def deactivate(self):
        pass
