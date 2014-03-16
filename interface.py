__author__ = 'nmearl'

import sys
from numpy import arange, sin, array
from PySide.QtCore import *
from PySide.QtGui import *

app = QApplication(sys.argv)

# from etsconfig.etsconfig import ETSConfig
# ETSConfig.toolkit = "qt4"
from enable.api import Window
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import RangeSelection, RangeSelectionOverlay, ZoomTool
from chaco.api import OverlayPlotContainer, create_line_plot, add_default_axes, \
                                 add_default_grids

import utilfuncs


class Viewer(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.base_ui()

    def base_ui(self):
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.kid = QLineEdit(self)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Pynary')
        self.show()

    def show_plot(self):
        self.plotview = Plotter(self)
        self.setCentralWidget(self.plotview.widget)
        x, y, e = utilfuncs.get_fits('005897826')
        self.plotview.update_data(x, y)

class Plotter():
    def __init__(self, parent):
        self.plotdata = ArrayPlotData(x=array([]),  y=array([]))
        self.window = self.create_plot(parent)
        self.widget = self.window.control

    def update_data(self, x, y):
        self.plotdata.set_data("x", x)
        self.plotdata.set_data("y", y)

    def create_plot(self, parent):
        value_mapper = None
        index_mapper = None
        plot = Plot(self.plotdata, padding=50, border_visible=True)
        plot.plot(("x", "y"), name="data plot", color="green")

        if value_mapper is None:
            index_mapper = plot.index_mapper
            value_mapper = plot.value_mapper
            add_default_grids(plot)
            add_default_axes(plot)
        else:
            plot.value_mapper = value_mapper
            value_mapper.range.add(plot.value)
            plot.index_mapper = index_mapper
            index_mapper.range.add(plot.index)

        selection_overlay = RangeSelectionOverlay(component = plot)
        plot.tools.append(RangeSelection(plot))
        zoom = ZoomTool(plot, tool_mode="box", always_on=False)
        plot.overlays.append(selection_overlay)
        plot.overlays.append(zoom)

        return Window(parent, -1, component=plot)

if __name__ == "__main__":
    plot = Viewer()
    plot.resize(600, 400)
    plot.show()
    sys.exit(app.exec_())