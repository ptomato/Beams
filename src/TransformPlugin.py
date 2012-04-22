from traits.api import HasTraits, Bool

class TransformPlugin(HasTraits):

    active = Bool(False)

    def process_frame(self, frame):
        if not self.active:
            return frame
        return self._process(frame)

    def _active_changed(self, value):
        if value:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        pass

    def deactivate(self):
        pass
