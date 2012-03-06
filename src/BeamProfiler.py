import numpy as N
from CameraImage import *

class BeamProfiler(object):

    def __init__(self, screen, active=False):
        self._screen = screen
        self.active = active

    def send_frame(self, frame):
        if not self.active:
            return

        frame = N.array(frame, dtype=float)
        bw = (len(frame.shape) == 2)
        if not bw:
            # Use standard NTSC conversion formula
            frame = N.array(
                0.2989 * frame[..., 0] 
                + 0.5870 * frame[..., 1]
                + 0.1140 * frame[..., 2])

        y, x = N.mgrid[:frame.shape[0], :frame.shape[1]]
        m00 = frame.sum() or 1.0
        m10 = (frame * x).sum() / m00
        m01 = (frame * y).sum() / m00
        dx, dy = x - m10, y - m01
        m20 = (frame * dx ** 2).sum() / m00
        m02 = (frame * dy ** 2).sum() / m00
        m11 = (frame * dx * dy).sum() / m00

        print m01, m10
        self._screen.hud('profiler',
            'Centroid: {:.1f}, {:.1f}'.format(m10, m01))

    # Properties
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value):
        self._active = bool(value)
        if not self._active:
            self._screen.hud('profiler', None)
