from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

import pandas as pd

from gui.fit_predict_tab import FitPredictTab
from gui.feature_analysis_tab import FeatureAnalysisTab
from gui.table_widget import TableWidget
from dataset import Dataset


class LeftDockMLTab(QWidget):
    dataset_opened = pyqtSignal(Dataset, TableWidget)
    dataset_appended = pyqtSignal()
    request_plot_generation = pyqtSignal(QWidget, str)
    grid_computed = pyqtSignal(object, pd.DataFrame)

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
        self._feature_analysis_tab = FeatureAnalysisTab()

        self._tab_widget.addTab(self._fit_predict_tab, self._fit_predict_tab.windowTitle())
        self._tab_widget.addTab(self._feature_analysis_tab, self._feature_analysis_tab.windowTitle())

        # signals to children
        self.dataset_opened.connect(self._fit_predict_tab.dataset_opened)
        self.dataset_opened.connect(self._feature_analysis_tab.dataset_opened)
        self.grid_computed.connect(self._feature_analysis_tab.update_grid)

        # incoming signals from children
        self._fit_predict_tab.request_plot_generation.connect(self.request_plot_generation.emit)
        self._fit_predict_tab.grid_computed.connect(self.grid_computed.emit)
        self._feature_analysis_tab.request_plot_generation.connect(self.request_plot_generation.emit)

