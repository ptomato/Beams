from envisage.api import Application

from MainWindow import MainWindow
from BackgroundSubtract import BackgroundSubtract
from BeamProfiler import BeamProfiler
from DeltaDetector import DeltaDetector
from MinMaxDisplay import MinMaxDisplay
from Rotator import Rotator


class Beams(Application):
    """The Beams application (plugin manager)"""

    # Application interface
    id = 'name.ptomato.beams'

    def __init__(self, **traits):
        mainwin = MainWindow()
        super(Beams, self).__init__(
            id='name.ptomato.beams',
            plugins=[mainwin, BackgroundSubtract(), Rotator(),
                DeltaDetector(screen=mainwin.screen),
                MinMaxDisplay(screen=mainwin.screen),
                BeamProfiler(screen=mainwin.screen)],
            **traits)

if __name__ == '__main__':
    theapp = Beams()
    theapp.run()
