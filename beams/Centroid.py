import numpy as N
from traits.api import Float, Tuple
from traitsui.api import View, VGroup, Item
from enable.api import ColorTrait
from DisplayPlugin import DisplayPlugin


class Centroid(DisplayPlugin):

    # These are the results of the calculation
    _centroid = Tuple(Float(), Float())

    # These control the visualization
    color = ColorTrait('white')

    view = View(
        VGroup(
            Item('active'),
            label='Centroid',
            show_border=True))

    def __init__(self, **traits):
        super(Centroid, self).__init__(**traits)
        self.screen.data_store['centroid_x'] = N.array([])
        self.screen.data_store['centroid_y'] = N.array([])
        renderers = self.screen.plot.plot(('centroid_x', 'centroid_y'),
            type='scatter',
            marker_size=2.0,
            color=self.color,
            marker='circle')
        self._centroid_patch = renderers[0]
        self._centroid_patch.visible = self.active

        # Connect handlers
        self.on_trait_change(self._move_centroid, '_centroid', dispatch='ui')
        self.on_trait_change(self._update_hud, '_centroid', dispatch='ui')

    def _move_centroid(self):
        self.screen.data_store['centroid_x'] = N.array([self._centroid[0]])
        self.screen.data_store['centroid_y'] = N.array([self._centroid[1]])

    def _update_hud(self):
        self.screen.hud('centroid',
            'Centroid: {0[0]:.1f}, {0[1]:.1f}\n'.format(self._centroid))

    def _process(self, frame):
        bw = (len(frame.shape) == 2)
        if not bw:
            # Use standard NTSC conversion formula
            frame = N.array(
                0.2989 * frame[..., 0]
                + 0.5870 * frame[..., 1]
                + 0.1140 * frame[..., 2])

        self._centroid = _calculate_centroid(frame)

    def activate(self):
        self._centroid_patch.visible = True

    def deactivate(self):
        self.screen.hud('centroid', None)
        self._centroid_patch.visible = False


def _calculate_centroid(frame):
    """Calculate the centroid"""
    # From Bullseye
    y, x = N.mgrid[:frame.shape[0], :frame.shape[1]]
    m00 = frame.sum() or 1.0
    m10 = (frame * x).sum() / m00
    m01 = (frame * y).sum() / m00
    return m10, m01
