from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

from gui.fit_predict_tab import FitPredictTab
from gui.table_widget import TableWidget
from dataset import Dataset


class LeftDockMLTab(QWidget):
    dataset_opened = pyqtSignal(Dataset, TableWidget)
    dataset_appended = pyqtSignal()
    request_plot_generation = pyqtSignal(QWidget, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("MLTab")
        self.setWindowTitle("Machine Learning")

        self._tab_widget = QTabWidget()
        # self._tab_widget.setTabPosition(QTabWidget.West)
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tab_widget)
        self.setLayout(self._layout)

        self._fit_predict_tab = FitPredictTab()

        self._tab_widget.addTab(self._fit_predict_tab, self._fit_predict_tab.windowTitle())

        # signals to children
        self.dataset_opened.connect(self._fit_predict_tab.dataset_opened)

        # incoming signals from children
        self._fit_predict_tab.request_plot_generation.connect(self.request_plot_generation.emit)

