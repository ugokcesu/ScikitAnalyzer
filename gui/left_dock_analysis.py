from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QTabBar
from PyQt5.QtCore import pyqtSignal

from gui.data_analysis_tab import DataAnalysisTab
from gui.data_analysis_tab_multi import DataAnalysisTabMulti
from gui.table_widget import TableWidget
from dataset import Dataset


class LeftDockAnalysisTab(QWidget):
    close_dataset = pyqtSignal()
    info_calculated = pyqtSignal(list)
    mask_created_from_xplot = pyqtSignal(str)
    dataset_opened = pyqtSignal(Dataset, TableWidget)
    dataset_appended = pyqtSignal()
    update_upon_window_activation = pyqtSignal()
    request_plot_generation = pyqtSignal(QWidget, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("DataTab")
        self.setWindowTitle("Data Analysis")

        self._tab_widget = QTabWidget()
        # self._tab_widget.setTabPosition(QTabWidget .West)
        self._tab_widget.tabBar().setStyleSheet("QTabWidget.tab-bar {left: 0; }")
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tab_widget)
        self.setLayout(self._layout)

        self._data_analysis_tab = DataAnalysisTab()
        self._data_analysis_tab_multi = DataAnalysisTabMulti()

        self._tab_widget.addTab(self._data_analysis_tab, self._data_analysis_tab.windowTitle())
        self._tab_widget.addTab(self._data_analysis_tab_multi, self._data_analysis_tab_multi.windowTitle())
        self._tab_widget.tabBar().setTabEnabled(1, False)

        self.close_dataset.connect(self._data_analysis_tab.update_upon_closing_dataset)
        self.close_dataset.connect(self._data_analysis_tab_multi.update_upon_closing_dataset)
        self.update_upon_window_activation.connect(self._data_analysis_tab.update_upon_window_activation)

        # incoming signals from children
        self._data_analysis_tab.info_calculated.connect(self.info_calculated.emit)
        self._data_analysis_tab.request_plot_generation.connect(self.request_plot_generation.emit)

        self._data_analysis_tab_multi.request_plot_generation.connect(self.request_plot_generation.emit)
        self._data_analysis_tab_multi.mask_created_from_xplot.connect(self.mask_created_from_xplot.emit)

        # outgoing signals to children
        self.dataset_opened.connect(self._data_analysis_tab.dataset_opened)
        self.dataset_opened.connect(self._data_analysis_tab_multi.dataset_opened)
        self.info_calculated.connect(self.enable_multi_tab)

    def enable_multi_tab(self):
        self._tab_widget.tabBar().setTabEnabled(1, True)

    def update_analysis_tab_with_window_state(self, state):
        return self._data_analysis_tab.update_self_with_window_state(state)
