import time
import numpy as N
import numpy.random
from traits.api import Tuple, Int, Float
from traitsui.api import View, Item, HGroup, Label

from Camera import Camera


class DummyGaussian(Camera):

    centroid = Tuple(Int(160), Int(120))
    radius = Float(75.0)
    amplitude = Int(60000)
    noise_amplitude = Int(5535)

    view = View(
        HGroup(
            Item('frame_rate', style='custom'),
            Label('fps')),
        Item('centroid'),
        Item('radius'),
        Item('amplitude'),
        Item('noise_amplitude'),
        title='Dummy Gaussian Plugin')

    def __init__(self, **traits):
        super(DummyGaussian, self).__init__(resolution=(320, 240),
            id_string='Dummy Gaussian Plugin',
            **traits)
        self._supported_resolutions = [(320, 240), (640, 480)]

    def open(self):
        pass

    def close(self):
        pass

    def query_frame(self):
        """Returns a Gaussian with uniform random noise"""
        width, height = self.resolution
        x, y = N.ogrid[0:height, 0:width]
        y0, x0 = self.centroid
        r = N.hypot(x - x0, y - y0)
        self.frame = N.array(N.exp(-r ** 2 / self.radius ** 2) * self.amplitude,
            dtype=N.uint16)
        self.frame += N.random.uniform(low=0, high=self.noise_amplitude,
            size=(height, width))

        # Simulate frame rate
        time.sleep(1.0 / self.frame_rate)

    def find_resolutions(self):
        return self._supported_resolutions

#if __name__ == '__main__':
#    cam = DummyGaussian()
#    print cam.find_resolutions()
#    print cam.resolution
#    cam.resolution = (640, 480)
#    print cam.resolution
