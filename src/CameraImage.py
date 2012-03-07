import gtk, gobject
import numpy as N
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg \
    import FigureCanvasGTKAgg as FigureCanvas
import matplotlib.cm

class CameraImage(FigureCanvas):
    
    def __init__(self):
        self._fig = Figure()
        FigureCanvas.__init__(self, self._fig)
        self._data = N.zeros((200, 320), dtype=N.uint8)
        self._dims = self._data.shape
        self._cmap = None
        self._rotate = 0
        self._hud = dict()
        self._hud_text = self._fig.text(0.99, 0.99, '',
            color='white',
            verticalalignment='top', horizontalalignment='right')
        self._overlays = dict()
        
        # Draw the image
        self._ax = self._fig.add_subplot(1, 1, 1)
        self._image = self._ax.imshow(self._data, cmap=matplotlib.cm.gray)
        self._ax.set_aspect('equal')
        self._fig.tight_layout()
        self.draw()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        bw = (len(value.shape) == 2)
        if not bw and self._cmap is not None:
            # Selecting a colormap coerces the image to monochrome
            # Use standard NTSC conversion formula
            value = N.array(
                0.2989 * value[..., 0] 
                + 0.5870 * value[..., 1]
                + 0.1140 * value[..., 2])
        self._data = value
        self._display_data()

    def _display_data(self):
        data = N.rot90(self._data, self._rotate)
        
        if self._dims != data.shape:
            # Redraw the axes if the image is a different size
            self._fig.delaxes(self._ax)
            self._ax = self._fig.add_subplot(1, 1, 1)
            self._dims = data.shape
            self._image = self._ax.imshow(data)
            bw = (len(self._dims) == 2)
            if bw:
                if data.dtype == N.uint16:
                    self._image.set_clim(0, 65535)
                else:
                    self._image.set_clim(0, 255)
                self._image.set_cmap(matplotlib.cm.gray \
                                     if self._cmap is None \
                                     else self._cmap)
            self._fig.tight_layout()
        
        else:
            # Do it the fast way
            self._image.set_data(data)

        # Do the heads-up display
        text = ''
        for key in sorted(self._hud.keys()):
            text += self._hud[key] + '\n\n'
        self._hud_text.set_text(text)
        
        self._ax.set_aspect('equal')
        self.draw()
    
    @property
    def rotate(self):
        '''
        Number of steps of 90 degrees to rotate the image before
        displaying it - must be between 0 and 3
        '''
        return self._rotate
    
    @rotate.setter
    def rotate(self, value):
        if value < 0 or value > 3:
            raise ValueError('Rotate must be between 0 and 3')
        self._rotate = value

    @property
    def cmap(self):
        '''
        Colormap to use for display; None means use the image's natural
        colors (if RGB data) or grayscale (if monochrome). Setting @cmap
        to a value coerces the image to monochrome.
        '''
        return self._cmap
    
    @cmap.setter
    def cmap(self, value):
        self._cmap = value
        # Has no effect on RGB data:
        self._image.set_cmap(value if value is not None else matplotlib.cm.gray)
        self.data = self.data  # redisplay

    def hud(self, key, text):
        if text is None:
            self._hud.pop(key, None)
        else:
            self._hud[key] = text

    def overlay(self, key, list_of_patches):
        if not list_of_patches:
            old_list = self._overlays.pop(key, [])
            for patch in old_list:
                patch.remove()
            return

        # Draw the overlays
        self._overlays[key] = list_of_patches
        for patch in list_of_patches:
            self._ax.add_patch(patch)
