from PyQt5.QtWidgets import QWidget, QGridLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ColorMapWindow(QWidget):
        length = 6
        def __init__(self, parent=None, height=0.5):
                super().__init__(parent)
                #self.setWindowTitle("Plotting Window")
                #self.setFixedSize(self.length, height)
                self.setFixedSize(2*self.physicalDpiX(), height * self.physicalDpiY())
                self.figure = plt.figure()

                self.canvas = FigureCanvas(self.figure)

                #scroll_area = QScrollArea()
                #scroll_area.setWidget(self.canvas)
                self.layout = QGridLayout()
                #self.layout.addWidget(scroll_area, 1, 0)
                self.layout.addWidget(self.canvas, 0, 0)
                self.setLayout(self.layout)