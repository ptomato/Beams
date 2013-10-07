#coding: utf8
import numpy as N
from traits.api import Range
from traitsui.api import View, VGroup, Item, EnumEditor
from TransformPlugin import TransformPlugin


class Rotator(TransformPlugin):

    rotation_angle = Range(0, 3)

    view = View(
        VGroup(
            Item('active'),
            Item('rotation_angle', editor=EnumEditor(values={
                0: u'0:0°',
                1: u'1:90°',
                2: u'2:180°',
                3: u'3:270°'
            })),
            label='Rotation',
            show_border=True))

    def _process(self, frame):
        return N.rot90(frame, self.rotation_angle)
