
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QScrollArea

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class PlotWindow(QWidget):
        length = 6

        def __init__(self, parent=None, height=3):
                super().__init__(parent)
                #self.setWindowTitle("Plotting Window")
                #self.setFixedSize(self.length, height)
                self.setFixedSize(6*self.physicalDpiX(), 3 * self.physicalDpiY())
                self.figure = plt.figure()

                self.canvas = FigureCanvas(self.figure)

                #scroll_area = QScrollArea()
                #scroll_area.setWidget(self.canvas)
                self.layout = QGridLayout()
                #self.layout.addWidget(scroll_area, 1, 0)
                self.layout.addWidget(self.canvas, 0, 0)
                self.setLayout(self.layout)
