import numpy as N
import gobject
import gtk.gdk

from CameraImage import *

class DeltaDetector(object):

    def __init__(self, screen, active=False, threshold=20.0):
        self._screen = screen
        self._previous_frame = None
        self._frame = None
        self.active = active
        self.threshold = threshold
        self._timed_out = False
    
    def send_frame(self, frame):
        self._previous_frame = self._frame
        self._frame = N.array(frame, dtype=float)
        
        if self._timed_out:
            return
        if not self.active:
            return
        if self._previous_frame is None:
            return
        if(self._previous_frame.shape != self._frame.shape):
            self._previous_frame = None
            return
        
        maximum_delta = N.max(N.abs(self._frame - self._previous_frame))
        if maximum_delta > self.threshold:
            gtk.gdk.beep()
            
            # Don't beep more than once per second
            self._timed_out = True
            gobject.timeout_add(1000, self._switch_on_timeout)

        self._screen.hud('delta',
            'Current average delta: {:.3f}\n'.format(self.average)
            + 'Current maximum delta: {:.3f}'.format(maximum_delta))

    def _switch_on_timeout(self):
        self._timed_out = False
        return False

    # Properties
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value):
        self._active = bool(value)
        if not self._active:
            self._screen.hud('delta', None)
    
    @property
    def threshold(self):
        return self._threshold
    
    @threshold.setter
    def threshold(self, value):
        self._threshold = float(value)
    
    @property
    def average(self):
        if self._frame is None or self._previous_frame is None:
            return 0.0
        return N.mean(self._frame - self._previous_frame)
    