import numpy as N
from traits.api import Int
from traitsui.api import BasicEditorFactory
from chaco.api import DataRange1D
from traits.etsconfig.api import ETSConfig

if ETSConfig.toolkit == 'wx':
    import wx
    from traitsui.wx.editor import Editor

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

elif ETSConfig.toolkit == 'qt4':
    from pyface.qt import QtGui
    from traitsui.qt4.editor import Editor

    class _ColorMapControl_qt4(QtGui.QLabel):
        """Qt widget for showing a color map sample"""

        def __init__(self, parent, cmap, padding=10, width=128, height=10):
            self.width = width
            self.height = height
            QtGui.QLabel.__init__(self, parent)
            self.setFixedSize(self.width, self.height)
            self.set_cmap(cmap)

        def set_cmap(self, cmap):
            self.cmap = cmap
            if self.cmap is None:
                self.data = N.zeros((self.width, self.height), dtype=N.uint8)
                colortable = [QtGui.qRgb(0, 0, 0)] * 256
            else:
                self.data = N.require(
                    N.outer(N.ones(self.height),
                        N.linspace(0, 255, self.width, endpoint=True)),
                    dtype=N.uint8,
                    requirements=['C_CONTIGUOUS', 'ALIGNED'])
                mapper = self.cmap(DataRange1D(low=0, high=255))
                clrarray = mapper.map_screen(N.arange(0, 256))[:, :-1] * 255
                colortable = [QtGui.qRgb(*clrarray[i, :]) for i in range(256)]

            image = QtGui.QImage(self.data, self.width, self.height,
                QtGui.QImage.Format_Indexed8)
            image.setColorTable(colortable)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.setPixmap(pixmap)


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


class _ColorMapEditor_qt4(Editor):
    """Qt4 implementation of ColorMapEditor"""

    def init(self, parent):
        self.control = _ColorMapControl_qt4(parent.parentWidget(), self.value.cmap,
            width=self.factory.width, height=self.factory.height)
        self.set_tooltip()
        self.value.on_trait_change(self.update_editor, 'cmap', dispatch='ui')

    def update_editor(self):
        self.control.set_cmap(self.value.cmap)


class ColorMapEditor(BasicEditorFactory):
    """TraitsUI editor that shows a sample of a color map"""
    width = Int(128)
    height = Int(10)
    if ETSConfig.toolkit == 'wx':
        klass = _ColorMapEditor_wx
    elif ETSConfig.toolkit == 'qt4':
        klass = _ColorMapEditor_qt4
