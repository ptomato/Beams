import numpy as N
from traits.api import Int
from traitsui.api import BasicEditorFactory
from traitsui.wx.editor import Editor
from chaco.api import DataRange1D
import wx


class _ColorMapControl_wx(wx.Window):
    """WX control for showing a color map sample"""

    def __init__(self, parent, cmap, padding=10, width=128, height=10):
        self.cmap = cmap
        self.width = width
        self.height = height
        super(_ColorMapControl_wx, self).__init__(parent,
            size=wx.Size(self.width + padding, self.height + padding))
        wx.EVT_PAINT(self, self._on_paint)

    def _on_paint(self, event=None):
        if self.cmap is None:
            # Just show a black bar
            data = N.zeros((self.width, self.height, 3), dtype=N.uint8)
        else:
            mapper = self.cmap(DataRange1D(low=0, high=self.width - 1))
            # run a range through the color mapper, discard the alpha channel,
            # and multiply so that it's 0-255
            clrarray = mapper.map_screen(N.arange(0, self.width))[:, :-1] * 255
            # Replicate the array to the required height
            data = N.require(N.tile(clrarray, (self.height, 1)),
                dtype=N.uint8,
                requirements=['C_CONTIGUOUS', 'ALIGNED'])

        # Create a bitmap from the array and paint it
        wdc = wx.PaintDC(self)
        wdx, wdy = self.GetClientSizeTuple()
        bitmap = wx.BitmapFromBuffer(self.width, self.height, data)
        wdc.DrawBitmap(bitmap, (wdx - self.width) / 2, (wdy - self.height) / 2)


class _ColorMapEditor_wx(Editor):
    """WX implementation of ColorMapEditor"""

    # Note: init(), not __init__()
    def init(self, parent):
        self.control = _ColorMapControl_wx(parent, self.value.cmap,
            width=self.factory.width, height=self.factory.height)
        self.set_tooltip()
        # WHY ON EARTH is it impossible to just edit the MainWindow.cmap trait
        # which delegates to the MainWindow.screen.cmap trait? Why do we have
        # to edit MainWindow.screen and connect the update listener ourselves?
        # Try as I might, I could not get this editor to reflect changes made
        # from the other editor of MainWindow.cmap.
        self.value.on_trait_change(self.update_editor, 'cmap', dispatch='ui')

    def update_editor(self):
        # Called in response to the edited trait changing (well, that's how it's
        # SUPPOSED to work)
        self.control.cmap = self.value.cmap
        self.control.Refresh()


class ColorMapEditor(BasicEditorFactory):
    """TraitsUI editor that shows a sample of a color map"""
    width = Int(128)
    height = Int(10)
    klass = _ColorMapEditor_wx
