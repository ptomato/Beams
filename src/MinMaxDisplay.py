import numpy as N
from CameraImage import *

class MinMaxDisplay(object):

    def __init__(self, screen, active=False):
        self._screen = screen
        self._previous_frame = None
        self.active = active
        self._min = None
        self._max = None
    
    def send_frame(self, frame):
        if not self.active:
            return
        self._min = frame.min()
        self._max = frame.max()

        self._screen.hud('minmax',
            'Minimum: {}\nMaximum: {}'.format(self._min, self._max))

    # Properties
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value):
        self._active = bool(value)
        if not self._active:
            self._screen.hud('minmax', None)

    @property
    def min(self):
    	return self._min

    @property
    def max(self):
    	return self._max
        