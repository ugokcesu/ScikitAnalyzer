
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5 import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class PlotWindow(QWidget):
        length = 6

        def __init__(self, parent=None, height=3, width=6):

                super().__init__(parent)
                # self.setWindowTitle("Plotting Window")
                # self.setFixedSize(self.length, height)
                self.setFixedSize(width * self.physicalDpiX(), height * self.physicalDpiY())
                self.figure = plt.figure()
                self.canvas = FigureCanvas(self.figure)

                # scroll_area = QScrollArea()
                # scroll_area.setWidget(self.canvas)
                self.layout = QGridLayout()
                # self.layout.addWidget(scroll_area, 1, 0)
                self.layout.addWidget(self.canvas, 0, 0, 1, 3)
                self.setLayout(self.layout)

                FigureCanvas.setSizePolicy(self,
                                           Qt.QSizePolicy.Expanding,
                                           Qt.QSizePolicy.Expanding)
                FigureCanvas.updateGeometry(self)


