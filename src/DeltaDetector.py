import numpy as N
from traits.api import Range, Float, on_trait_change
from traitsui.api import View, VGroup, Item
from pyface.timer.api import do_after
from DisplayPlugin import DisplayPlugin

class DeltaDetector(DisplayPlugin):

    threshold = Range(low=0.0, high=10000.0, value=20.0)
    _maximum_delta = Float()
    _average_delta = Float()

    view = View(
        VGroup(
            Item('active'),
            Item('threshold'),
            label='Delta Detector',
            show_border=True))

    def __init__(self, **traits):
        self._previous_frame = None
        self._timed_out = False
        super(DeltaDetector, self).__init__(**traits)
    
    def _process(self, frame):
        if (self._previous_frame is None 
            or self._previous_frame.shape != frame.shape):
            self._maximum_delta = self._average_delta = 0.0
            self._previous_frame = frame
            return
        
        self._maximum_delta = N.max(N.abs(frame - self._previous_frame))
        self._average_delta = N.mean(frame - self._previous_frame)
        
        self._previous_frame = frame
    
    @on_trait_change('_maximum_delta,_average_delta')
    def _update_hud(self):
        if self._maximum_delta > self.threshold and not self._timed_out:
            print 'BEEP'  # FIXME
            
            # Don't beep more than once per second
            self._timed_out = True
            do_after(1000, self._switch_on_timeout)

        self.screen.hud('delta',
            'Current average delta: {0._average_delta:.3f}\n'
            'Current maximum delta: {0._maximum_delta:.3f}'.format(self))

    def _switch_on_timeout(self):
        self._timed_out = False

    def deactivate(self):
        self.screen.hud('delta', None)
