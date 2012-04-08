import numpy as N
import numpy.random

from Camera import *

class DummyGaussian(Camera):
    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        
        self._supported_resolutions = [(320, 240), (640, 480)]
        self.resolution = (320, 240)
        self.id_string = 'Dummy Gaussian Plugin'

    def open(self):
        pass

    def close(self):
        pass

    def query_frame(self):
        """Returns a Gaussian with uniform random noise"""
        width, height = self.resolution
        x, y = N.ogrid[0:height, 0:width]
        x0, y0 = int(self.height / 2), int(self.width / 2)
        r = N.hypot(x - x0, y - y0)
        w0 = 75.0
        self.frame = N.array(N.exp(-r ** 2 / w0 ** 2) * 60000, dtype=N.uint16)
        self.frame += N.random.uniform(low=0, high=5535, size=(height, width))

    def find_resolutions(self):
        return self._supported_resolutions

    def configure(self):
        pass

#if __name__ == '__main__':
#    cam = DummyGaussian()
#    print cam.find_resolutions()
#    print cam.resolution
#    cam.resolution = (640, 480)
#    print cam.resolution
