
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QScrollArea

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class PlotWindow(QWidget):
        def __init__(self, parent=None, height=12):
                super().__init__(parent)
                self.setWindowTitle("Plotting Window")
                self.figure = plt.figure(figsize=(6, height))
                self.canvas = FigureCanvas(self.figure)
                scroll_area = QScrollArea()
                scroll_area.setWidget(self.canvas)
                self.layout = QGridLayout()
                self.layout.addWidget(scroll_area, 1, 0)
                self.setLayout(self.layout)
