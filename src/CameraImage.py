import numpy as N
from traits.api import (HasTraits, Array, Range, Instance, Enum, DictStrStr,
    DictStrAny)
from traitsui.api import View, Item
from chaco.api import (ArrayPlotData, Plot, TextBoxOverlay, DataRange1D,
    gray, bone, pink, jet)
from enable.api import ComponentEditor

class CameraImage(HasTraits):

    data = Array()
    plot = Instance(Plot)
    hud_overlay = Instance(TextBoxOverlay)
    
	# Number of steps of 90 degrees to rotate the image before
    # displaying it - must be between 0 and 3
    rotate = Range(0, 3)

    # Colormap to use for display; None means use the image's natural
    # colors (if RGB data) or grayscale (if monochrome). Setting @cmap
    # to a value coerces the image to monochrome.
    cmap = Enum(None, gray, bone, pink, jet)  # isoluminant, awesome

    view = View(Item('plot', show_label=False, editor=ComponentEditor()))

    def __init__(self):
        self._dims = (320, 200)
        self.data_store = ArrayPlotData(image=self.data)
        self._hud = dict()
        self._overlays = dict()
        self.plot = Plot(self.data_store)
        # Draw the image
        renderers = self.plot.img_plot('image', name='camera_image')
        self._image = renderers[0]
        color_range = DataRange1D()
        color_range.set_bounds(0, 255)
        self._image.color_range = color_range
        self._image.color_mapper = gray(color_range)
        #self._ax.set_aspect('equal')
        #self._fig.tight_layout()

    def _data_default(self):
        return N.zeros(self._dims, dtype=N.uint8)

    def _data_changed(self, value):
        bw = (len(value.shape) == 2)
        if not bw and self.cmap is not None:
            # Selecting a colormap coerces the image to monochrome
            # Use standard NTSC conversion formula
            value = N.array(
                0.2989 * value[..., 0] 
                + 0.5870 * value[..., 1]
                + 0.1140 * value[..., 2])
        value = N.rot90(value, self.rotate)
        self.data_store['image'] = self.data = value
        self._display_data()

    def _display_data(self):
        if self._dims != self.data.shape:
            # Redraw the axes if the image is a different size
            self.plot.delplot('camera_image')
            self._dims = self.data.shape
            renderers = self.plot.img_plot('image', name='camera_image')
            self._image = renderers[0]
            bw = (len(self._dims) == 2)
            if bw:
                color_range = DataRange1D()
                if self.data.dtype == N.uint16:
                    color_range.set_bounds(0, 65535)
                else:
                    color_range.set_bounds(0, 255)
                self._image.color_range = color_range
                self._image.color_mapper = gray(color_range) \
                                     if self.cmap is None \
                                     else self.cmap(color_range)
            #self._fig.tight_layout()
    
    #    # Do the heads-up display
    #    text = ''
    #    for key in sorted(self._hud.keys()):
    #        text += self._hud[key] + '\n\n'
    #    self._hud_text.set_text(text)
    #
    #    self._ax.set_aspect('equal')
    #    self.draw()

    def _cmap_changed(self, value):
        # Has no effect on RGB data?
        color_range = self._image.color_range
        color_map = (value(color_range) if value is not None
            else gray(color_range))
        self._image.color_mapper = color_map

    def hud(self, key, text):
        if text is None:
            self._hud.pop(key, None)
        else:
            self._hud[key] = text

    #def overlay(self, key, list_of_patches):
    #    if not list_of_patches:
    #        old_list = self._overlays.pop(key, [])
    #        for patch in old_list:
    #            patch.remove()
    #        return
    #
    #    # Draw the overlays
    #    self._overlays[key] = list_of_patches
    #    for patch in list_of_patches:
    #        self._ax.add_patch(patch)
