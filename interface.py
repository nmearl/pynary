__author__ = 'nmearl'

import sys
import numpy as np
from PySide.QtCore import *
from PySide.QtGui import *
import pyqtgraph as pg
import time

import utilfuncs


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Create menu actions
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        # Create menus and status bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        # self.statusBar()

        # Set window geometry
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Pynary')
        self.show()

        self.content_widget = ContentWidget()
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.content_widget)
        self.setCentralWidget(_widget)


class ContentWidget(QWidget):
    def __init__(self):
        super(ContentWidget, self).__init__()
        self.__controls()
        self.__layout()

    def __controls(self):
        # Construct UI elements
        self.task_label = QLabel('Ready', self)
        self.kid_label = QLabel("Enter KID", self)
        self.kid_input = QLineEdit('005897826', self)

        self.pdc_bool = QCheckBox("Use PDC", self)
        self.pdc_bool.setChecked(True)

        self.detrend_bool = QCheckBox("Detrend", self)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0.0)

        self.progress_bar.hide()

        self.retrieve_data = RetrieveData(self.kid_input.text())
        self.retrieve_data.update_progress.connect(lambda p: self.progress_bar.setValue(p))
        self.retrieve_data.data.connect(self.show_plot)

        self.mask_file_button = QPushButton('Open', self)
        self.mask_file_button.clicked.connect(self.get_mask_file)

        self.mask_file = ''
        self.mask_label = QLabel("No mask file selected", self)

        self.plot_button = QPushButton('Plot', self)
        self.plot_button.clicked.connect(self.get_data)

    def __layout(self):
        # Place elements in layout
        col1 = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(self.kid_label)
        row1.addWidget(self.kid_input)
        col1.addLayout(row1)
        col1.addWidget(self.pdc_bool)

        group_box = QGroupBox("Detrending Options")
        grp_col = QVBoxLayout()
        grp_col.addWidget(self.detrend_bool)

        grp_row = QHBoxLayout()
        grp_row.addWidget(self.mask_label)
        grp_row.addWidget(self.mask_file_button)
        grp_col.addLayout(grp_row)
        group_box.setLayout(grp_col)
        col1.addWidget(group_box)

        row2 = QHBoxLayout()
        row2.addWidget(self.plot_button)
        col1.addLayout(row2)
        col1.addStretch(1)

        row3 = QHBoxLayout()
        row3.addWidget(self.task_label)
        row3.addWidget(self.progress_bar)
        col1.addLayout(row3)

        self.setLayout(col1)

    def get_mask_file(self):
        self.mask_file, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.mask_label.setText('...'+self.mask_file[-20:])

    def get_data(self):
        self.task_label.setText('Getting data...')
        self.retrieve_data.use_pdc = self.pdc_bool.isChecked()
        self.retrieve_data.mask_file = self.mask_file
        self.retrieve_data.start()

    def show_plot(self, data):
        self.task_label.setText('Plotting data...')
        x, y, e = data
        self.plotview = Plotter(self.kid_input.text())
        self.plotview.create_plot(x, y)
        self.task_label.setText('Done')
        self.progress_bar.setValue(0.0)



class Plotter(QWidget):
    def __init__(self, kid):
        super(Plotter, self).__init__()
        self.kid = kid
        self.win = pg.GraphicsWindow()
        self.win.resize(1000, 600)
        self.win.setWindowTitle("Plot of KID {0}".format(self.kid))

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

    def create_plot(self, x, y):
        p = self.win.addPlot(title="KID {0}".format(self.kid))
        p.showGrid(x=True, y=True)
        p.plot(x, y, pen=(255, 255, 255, 200))
        lr = pg.LinearRegionItem([0, 10])
        lr.setZValue(-10)
        p.addItem(lr)

        # lr.sigRegionChanged.connect(lambda x: p9.setXRange(*lr.getRegion(), padding=0))
        # p9.sigXRangeChanged.connect(lambda x: lr.setRegion(p9.getViewBox().viewRange()[0]))

        # Update plot
        # p.setXRange(*lr.getRegion(), padding=0)


class RetrieveData(QThread):
    update_progress = Signal(float)
    data = Signal(list)
    use_pdc = False
    mask_file = ''

    def __init__(self, kid):
        QThread.__init__(self)
        self.kid = kid

    def run(self):
        self.update_progress.emit(0.0)
        d = utilfuncs.DataGetter(self.kid, self.use_pdc, self.update_progress)
        self.data.emit([d.time, d.flux, d.ferr])


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    sys.exit(main())