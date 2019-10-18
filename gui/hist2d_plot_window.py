from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from gui.plot_window import PlotWindow
from gui.range_slider import QRangeSlider


class Hist2dPlotWindow(PlotWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.slider = QRangeSlider()
#        self.slider.setSizePolicy(self, Qt.QSizePolicy.Minimum)
        self.layout.addWidget(self.slider, 1, 1)

        #self.slider.startValueChanged.connect(self.on_draw)
        #self.slider.endValueChanged.connect(self.on_draw)
        self.slider.startValueChanged.connect(self.on_draw)
        self.slider.endValueChanged.connect(self.on_draw)
        self.slider.setFixedWidth(300)


    def update_slider(self):
        axes = self.figure.axes
        try:
            start, end = axes[0].collections[0].get_clim()
            self.slider.setMin(0)
            self.slider.setMax(end*2)
            self.slider.setRange(0, end)
            self.slider.setRange(start, end)
        except Exception as e:
            pass

    def on_draw(self):
        axes_in_figure = self.figure.axes
        quadmesh = axes_in_figure[0].collections[0]
        quadmesh.set_clim(self.slider.start(), self.slider.end())
        self.canvas.draw()

