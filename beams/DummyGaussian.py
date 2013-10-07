import time
import numpy as N
import numpy.random
from traits.api import Int, Constant, Range, Property, cached_property
from traitsui.api import View, Item, HGroup, VGroup, Label

from Camera import Camera


class DummyGaussian(Camera):
    plugin_info = {
        'name': 'Dummy Gaussian',
        'description': 'Fake Gaussian data with uniform random noise',
        'author': 'Philip Chimento',
        'copyright year': '2011',
    }

    # All these proxy properties are necessary because you can only enter the
    # name of a trait as the dynamic boundary of a range, not an expression.
    _zero = Constant(0.0)
    _x_resolution = Property(fget=lambda self: self.resolution[0],
        depends_on='resolution')
    _y_resolution = Property(fget=lambda self: self.resolution[1],
        depends_on='resolution')
    _half_x_resolution = Property(depends_on='resolution')
    _half_y_resolution = Property(depends_on='resolution')
    _half_minimum_resolution = Property(depends_on='resolution')
    centroid_x = Range('_zero', '_x_resolution', '_half_x_resolution')
    centroid_y = Range('_zero', '_y_resolution', '_half_y_resolution')
    # Necessary because Tuple(Range('trait_name', ...), ...) doesn't work
    centroid = Property(depends_on='centroid_x, centroid_y')
    radius = Range('_zero', '_half_minimum_resolution', 75)
    amplitude = Int(60000)
    noise_amplitude = Int(5535)

    view = View(
        HGroup(
            Item('frame_rate', style='custom'),
            Label('fps')),
        VGroup(
            Item('centroid_x'),
            Item('centroid_y')),
        Item('radius'),
        Item('amplitude'),
        Item('noise_amplitude'),
        title='Dummy Gaussian Plugin')

    def __init__(self, **traits):
        super(DummyGaussian, self).__init__(resolution=(320, 240),
            id_string='Dummy Gaussian Plugin',
            **traits)
        self._supported_resolutions = [(320, 240), (640, 480)]

    @cached_property
    def _get__half_x_resolution(self):
        return self.resolution[0] / 2.0

    @cached_property
    def _get__half_y_resolution(self):
        return self.resolution[1] / 2.0

    @cached_property
    def _get__half_minimum_resolution(self):
        return min(self._half_x_resolution, self._half_y_resolution)

    @cached_property
    def _get_centroid(self):
        return (self.centroid_x, self.centroid_y)

    def _set_centroid(self, value):
        self.centroid_x, self.centroid_y = value

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
