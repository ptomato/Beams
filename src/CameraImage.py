import numpy as N
from traits.api import (HasTraits, Array, Range, Instance, Enum, DictStrStr,
    DictStrAny)
from traitsui.api import View, Item
from chaco.api import ArrayPlotData, Plot, gray, bone, pink, jet
from enable.api import ComponentEditor

class CameraImage(HasTraits):

    data = Array()
    plot = Instance(Plot)
    
	# Number of steps of 90 degrees to rotate the image before
    # displaying it - must be between 0 and 3
    rotate = Range(0, 3)

    # Colormap to use for display; None means use the image's natural
    # colors (if RGB data) or grayscale (if monochrome). Setting @cmap
    # to a value coerces the image to monochrome.
    cmap = Enum(None, gray, bone, pink, jet)  # isoluminant, awesome

    hud = DictStrStr()
    overlays = DictStrAny()

    view = View(Item('plot', show_label=False, editor=ComponentEditor()))

    def __init__(self):
        self.data_store = ArrayPlotData()
        self.data = N.zeros((320, 200), dtype=N.uint8)

    def _data_changed(self, value):
        bw = (len(value.shape) == 2)
        if not bw and self.cmap is not None:
            # Selecting a colormap coerces the image to monochrome
            # Use standard NTSC conversion formula
            value = N.array(
                0.2989 * value[..., 0] 
                + 0.5870 * value[..., 1]
                + 0.1140 * value[..., 2])
        self.data_store.set_data('image', value)

    def _plot_default(self):
        plot = Plot(self.data_store)
        # Draw the image
        plot.img_plot('image', colormap=self.cmap)
        #self._ax.set_aspect('equal')
        #self._fig.tight_layout()
        return plot

    #def _display_data(self):
    #    data = N.rot90(self._data, self._rotate)
    #
    #    if self._dims != data.shape:
    #        # Redraw the axes if the image is a different size
    #        self._fig.delaxes(self._ax)
    #        self._ax = self._fig.add_subplot(1, 1, 1)
    #        self._dims = data.shape
    #        self._image = self._ax.imshow(data)
    #        bw = (len(self._dims) == 2)
    #        if bw:
    #            if data.dtype == N.uint16:
    #                self._image.set_clim(0, 65535)
    #            else:
    #                self._image.set_clim(0, 255)
    #            self._image.set_cmap(matplotlib.cm.gray \
    #                                 if self._cmap is None \
    #                                 else self._cmap)
    #        self._fig.tight_layout()
    #
    #    else:
    #        # Do it the fast way
    #        self._image.set_data(data)
    #
    #    # Do the heads-up display
    #    text = ''
    #    for key in sorted(self._hud.keys()):
    #        text += self._hud[key] + '\n\n'
    #    self._hud_text.set_text(text)
    #
    #    self._ax.set_aspect('equal')
    #    self.draw()

    def _cmap_changed(self, value):
        # Has no effect on RGB data:
        self.plot.img_plot('image',
            colormap=(value if value is not None else gray))

    #def hud(self, key, text):
    #    if text is None:
    #        self._hud.pop(key, None)
    #    else:
    #        self._hud[key] = text

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
