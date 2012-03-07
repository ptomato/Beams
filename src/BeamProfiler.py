#coding: utf8
import numpy as N
import matplotlib.patches
from CameraImage import *

class BeamProfiler(object):

    def __init__(self, screen, active=False):
        self._screen = screen
        self.active = active
        self._centroid_patch = matplotlib.patches.CirclePolygon(
            (0, 0), radius=1,
            edgecolor='black', facecolor='white')
        self._ellipse_patch = matplotlib.patches.Ellipse(
            (0, 0), width=1, height=1, angle=0,
            edgecolor='white', facecolor='none'
            )

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

        # Calculate the moments
        y, x = N.mgrid[:frame.shape[0], :frame.shape[1]]
        m00 = frame.sum() or 1.0
        m10 = (frame * x).sum() / m00
        m01 = (frame * y).sum() / m00
        dx, dy = x - m10, y - m01
        m20 = (frame * dx ** 2).sum() / m00
        m02 = (frame * dy ** 2).sum() / m00
        m11 = (frame * dx * dy).sum() / m00

        # Calculate Gaussian boundary
        q = N.sqrt((m20 - m02) ** 2 + 4 * m11 ** 2)
        major_axis = 2 ** 1.5 * N.sqrt(m20 + m02 + q)
        minor_axis = 2 ** 1.5 * N.sqrt(m20 + m02 - q)
        rotation = N.degrees(0.5 * N.arctan2(2 * m11, m20 - m02))
        ellipticity = minor_axis / major_axis

        self._screen.hud('profiler',
            'Centroid: {:.1f}, {:.1f}\n'.format(m10, m01)
            + 'Major axis: {:.1f}\n'.format(major_axis)
            + 'Minor axis: {:.1f}\n'.format(minor_axis)
            + u'Rotation: {:.1f}°\n'.format(rotation)
            + 'Ellipticity: {:.3f}\n'.format(ellipticity))
        self._centroid_patch.xy = (m10, m01)
        self._ellipse_patch.center = (m10, m01)
        self._ellipse_patch.width = minor_axis
        self._ellipse_patch.height = major_axis
        self._ellipse_patch.angle = rotation

    # Properties
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value):
        self._active = bool(value)
        if not self._active:
            self._screen.hud('profiler', None)
            self._screen.overlay('profiler', None)
        else:
            self._screen.overlay('profiler', [
                self._centroid_patch,
                self._ellipse_patch])
