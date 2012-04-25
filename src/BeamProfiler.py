#coding: utf8
import numpy as N
from traits.api import Int, Float, Tuple, Range, on_trait_change
from traitsui.api import View, VGroup, Item
from enable.api import ColorTrait
from DisplayPlugin import DisplayPlugin

class BeamProfiler(DisplayPlugin):

    # These traits control the calculation of the Gaussian fit
    background_percentile = Range(0.0, 100.0, 15.0)
    num_crops = Range(0, 5, 1)
    crop_radius = Range(1.0, 4.0, 1.5)  # in beam diameters

    # These are the results of the calculation
    _centroid = Tuple(Float(), Float())
    _minor_axis = Float()
    _major_axis = Float()
    _angle = Float()
    _ellipticity = Float()
    _baseline = Float()
    _include_radius = Float()

    # These control the visualization
    num_points = Int(40)
    color = ColorTrait('white')

    view = View(
        VGroup(
            Item('active'),
            Item('background_percentile'),
            Item('num_crops', label='Crop # times'),
            Item('crop_radius'),
            label='Beam Profiler',
            show_border=True))

    def __init__(self, **traits):
        super(BeamProfiler, self).__init__(**traits)
        self.screen.data_store['centroid_x'] = N.array([])
        self.screen.data_store['centroid_y'] = N.array([])
        self.screen.data_store['ellipse_x'] = N.array([])
        self.screen.data_store['ellipse_y'] = N.array([])
        renderers = self.screen.plot.plot(('centroid_x', 'centroid_y'),
            type='scatter',
            marker_size=2.0,
            color=self.color,
            marker='circle')
        self._centroid_patch = renderers[0]
        self._centroid_patch.visible = self.active
        renderers = self.screen.plot.plot(('ellipse_x', 'ellipse_y'),
            type='line',
            color=self.color)
        self._ellipse_patch = renderers[0]
        self._ellipse_patch.visible = self.active
        
        # Connect handlers
        self.on_trait_change(self._move_centroid, '_centroid', dispatch='ui')
        self.on_trait_change(self._redraw_ellipse,
            '_centroid,_width,_height,_angle', dispatch='ui')
        self.on_trait_change(self._update_hud,
            '_centroid,_width,_height,_angle,_ellipticity,_baseline,'
            '_include_radius',
            dispatch='ui')

    def _move_centroid(self):
        self.screen.data_store['centroid_x'] = N.array([self._centroid[0]])
        self.screen.data_store['centroid_y'] = N.array([self._centroid[1]])

    def _redraw_ellipse(self):
        # Draw an N-point ellipse at the 1/e radius of the Gaussian fit
        # Using a parametric equation in t
        t = N.linspace(0, 2 * N.pi, self.num_points)
        angle = N.radians(self._angle)
        x0, y0 = self._centroid
        sin_t, cos_t = N.sin(t), N.cos(t)
        sin_angle, cos_angle = N.sin(angle), N.cos(angle)
        r_a = self._minor_axis / 2.0
        r_b = self._major_axis / 2.0
        x = x0 + r_a * cos_t * cos_angle - r_b * sin_t * sin_angle
        y = y0 + r_a * cos_t * sin_angle - r_b * sin_t * cos_angle
        self.screen.data_store['ellipse_x'] = x
        self.screen.data_store['ellipse_y'] = y

    def _update_hud(self):
        self.screen.hud('profiler',
            'Centroid: {0._centroid[0]:.1f}, {0._centroid[1]:.1f}\n'
            'Major axis: {0._major_axis:.1f}\n'
            'Minor axis: {0._minor_axis:.1f}\n'
            u'Rotation: {0._angle:.1f}°\n'
            'Ellipticity: {0._ellipticity:.3f}\n'
            'Baseline: {0._baseline:.1f}\n'
            'Inclusion radius: {0._include_radius:.1f}'.format(self))

    def _process(self, frame):
        bw = (len(frame.shape) == 2)
        if not bw:
            # Use standard NTSC conversion formula
            frame = N.array(
                0.2989 * frame[..., 0] 
                + 0.5870 * frame[..., 1]
                + 0.1140 * frame[..., 2])

        # Calibrate the background
        background = N.percentile(frame, self.background_percentile)
        frame -= background
        #N.clip(frame, 0.0, frame.max(), out=frame)

        m00, m10, m01, m20, m02, m11 = _calculate_moments(frame)

        bc, lc = 0, 0
        for count in range(self.num_crops):
            include_radius, dlc, dbc, drc, dtc, frame = _crop(frame,
                self.crop_radius, m00, m10, m01, m20, m02, m11)
            lc += dlc
            bc += dbc

            # Recalibrate the background and recalculate the moments
            new_bkg = N.percentile(frame, self.background_percentile)
            frame -= new_bkg
            background += new_bkg
            #N.clip(frame, 0.0, frame.max(), out=frame)

            m00, m10, m01, m20, m02, m11 = _calculate_moments(frame)

        m10 += lc
        m01 += bc

        # Calculate Gaussian boundary
        q = N.sqrt((m20 - m02) ** 2 + 4 * m11 ** 2)
        self._major_axis = 2 ** 1.5 * N.sqrt(m20 + m02 + q)
        self._minor_axis = 2 ** 1.5 * N.sqrt(m20 + m02 - q)
        self._angle = N.degrees(0.5 * N.arctan2(2 * m11, m20 - m02))
        self._ellipticity = self._minor_axis / self._major_axis
        
        self._centroid = (m10, m01)
        self._baseline = background
        self._include_radius = include_radius

    def activate(self):
        self._centroid_patch.visible = self._ellipse_patch.visible = True

    def deactivate(self):
        self.screen.hud('profiler', None)
        self._centroid_patch.visible = self._ellipse_patch.visible = False

def _calculate_moments(frame):
    """Calculate the moments"""
    # From Bullseye
    y, x = N.mgrid[:frame.shape[0], :frame.shape[1]]
    m00 = frame.sum() or 1.0
    m10 = (frame * x).sum() / m00
    m01 = (frame * y).sum() / m00
    dx, dy = x - m10, y - m01
    m20 = (frame * dx ** 2).sum() / m00
    m02 = (frame * dy ** 2).sum() / m00
    m11 = (frame * dx * dy).sum() / m00
    return m00, m10, m01, m20, m02, m11

def _crop(frame, crop_radius, m00, m10, m01, m20, m02, m11):
    """crop based on 3 sigma region"""
    w20 = crop_radius * 4 * N.sqrt(m20)
    w02 = crop_radius * 4 * N.sqrt(m02)
    include_radius = N.sqrt((w20 ** 2 + w02 ** 2) / 2)
    w02 = max(w02, 4)
    w20 = max(w20, 4)
    lc = int(max(0, m10 - w20))
    bc = int(max(0, m01 - w02))
    tc = int(min(frame.shape[0], m01 + w02))
    rc = int(min(frame.shape[1], m10 + w20))
    frame = frame[bc:tc, lc:rc]
    return include_radius, lc, bc, rc, tc, frame
