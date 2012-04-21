import numpy as N
from traits.api import (HasTraits, Array, Range, Instance, Enum)
from traitsui.api import View, Item
from chaco.api import (ArrayPlotData, Plot, TextBoxOverlay, DataRange1D,
    ColorMapper, gray, pink, jet)
from chaco.default_colormaps import fix
from chaco.api import Label as _Label
from enable.api import ComponentEditor
from AwesomeColorMaps import awesome, isoluminant

def bone(rng, **traits):
    """
    Generator function for the 'bone' colormap. (Instead of faulty one
    in Chaco.) Data from Matplotlib.
    """
    _bone_data = {
        'red': ((0., 0., 0.),(0.746032, 0.652778, 0.652778),(1.0, 1.0, 1.0)),
        'green': ((0., 0., 0.),(0.365079, 0.319444, 0.319444),
            (0.746032, 0.777778, 0.777778),(1.0, 1.0, 1.0)),
        'blue': ((0., 0., 0.),(0.365079, 0.444444, 0.444444),(1.0, 1.0, 1.0))}
    return ColorMapper.from_segment_map(_bone_data, range=rng, **traits)

class CameraImage(HasTraits):

    data = Array()
    data_store = Instance(ArrayPlotData)
    plot = Instance(Plot)
    hud_overlay = Instance(TextBoxOverlay)
    # TextBoxOverlay can't set text color or alignment?!
    
	# Number of steps of 90 degrees to rotate the image before
    # displaying it - must be between 0 and 3
    rotate = Range(0, 3)

    # Colormap to use for display; None means use the image's natural
    # colors (if RGB data) or grayscale (if monochrome). Setting @cmap
    # to a value coerces the image to monochrome.
    cmap = Enum(None, gray, bone, pink, jet, isoluminant, awesome)

    view = View(Item('plot', show_label=False, editor=ComponentEditor()))

    def __init__(self):
        self._dims = (200, 320)
        self.data_store = ArrayPlotData(image=self.data)
        self._hud = dict()
        self._overlays = dict()
        self.plot = Plot(self.data_store)
        # Draw the image
        renderers = self.plot.img_plot('image', name='camera_image',
            colormap=fix(gray, (0, 255)))
        self._image = renderers[0]
        self.plot.aspect_ratio = float(self._dims[1]) / self._dims[0]

        self.hud_overlay = TextBoxOverlay(text='', align='ll',
            border_color='transparent') # why doesn't border_visible=False work?
        self.plot.overlays.append(self.hud_overlay)

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

        if self._dims != self.data.shape:
            # Redraw the axes if the image is a different size
            self.plot.delplot('camera_image')
            self._dims = self.data.shape
            renderers = self.plot.img_plot('image', name='camera_image',
                colormap=self._get_cmap_function())
            # colormap is ignored if image is RGB or RGBA
            self._image = renderers[0]

        # Make sure the aspect ratio is correct, even after resize
        self.plot.aspect_ratio = float(self._dims[1]) / self._dims[0]

    def _get_cmap_function(self):
        return fix(
            gray if self.cmap is None else self.cmap,
            (0, 65535 if self.data.dtype == N.uint16 else 255))

    def _cmap_changed(self, value):
        # Has no effect on RGB data?
        cmap_func = self._get_cmap_function()
        self._image.color_mapper = cmap_func(self._image.value_range)

    def hud(self, key, text):
        if text is None:
            self._hud.pop(key, None)
        else:
            self._hud[key] = text

        # Do the heads-up display
        text = ''
        for key in sorted(self._hud.keys()):
            text += self._hud[key] + '\n\n'
        self.hud_overlay.text = text

