import numpy as N
import numpy.random

from Camera import *

class DummyGaussian(Camera):
    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        
        self._supported_resolutions = [(320, 240), (640, 480)]
        self._resolution = (320, 240)

    def open(self):
        pass

    def close(self):
        pass

    def query_frame(self):
        """Returns a Gaussian with uniform random noise"""
        x, y = N.ogrid[0:self._resolution[1], 0:self._resolution[0]]
        x0, y0 = int(self._resolution[1] / 2), int(self._resolution[0] / 2)
        r = N.hypot(x - x0, y - y0)
        w0 = 75.0
        self.frame = N.array(N.exp(-r ** 2 / w0 ** 2) * 60000, dtype=N.uint16)
        self.frame += N.random.uniform(low=0, high=5535, size=self._resolution[::-1])

    @property
    def resolution(self):
        return self._resolution
    
    @resolution.setter
    def resolution(self, value):
        if value not in self._supported_resolutions:
            raise ValueError('Resolution {} not supported'.format(value))
        self._resolution = value
    
    def find_resolutions(self):
        return self._supported_resolutions

#if __name__ == '__main__':
#    cam = DummyGaussian()
#    print cam.find_resolutions()
#    print cam.resolution
#    cam.resolution = (640, 480)
#    print cam.resolution
#    cam.resolution = (1200, 900) # exception