#coding: utf8
import numpy as N
from traits.api import Button
from traitsui.api import View, VGroup, Item
from TransformPlugin import TransformPlugin


class BackgroundSubtract(TransformPlugin):

    capture_background = Button()

    view = View(
        VGroup(
            Item('active'),
            Item('capture_background', show_label=False),
            label='Background Subtract',
            show_border=True))

    def __init__(self, **traits):
        super(BackgroundSubtract, self).__init__(**traits)
        self._background_frame = None
        self._capture_next_frame = True

    def _process(self, frame):
        if self._capture_next_frame:
            self._background_frame = frame
            self._capture_next_frame = False
        temp = N.asfarray(frame) - self._background_frame
        if frame.dtype.kind == 'u':
            temp[temp < 0] = 0.0
        return N.asarray(temp, dtype=frame.dtype)

    def _capture_background_fired(self):
        self._capture_next_frame = True
