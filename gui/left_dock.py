from PyQt5.QtWidgets import QWidget, QDockWidget, QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal

import pandas as pd

from gui.left_dock_analysis import LeftDockAnalysisTab
from gui.left_dock_data import LeftDockDataTab
from gui.left_dock_ml import LeftDockMLTab

from dataset import Dataset
from gui.table_widget import TableWidget


class LeftDock(QDockWidget):
    mask_created_from_xplot = pyqtSignal(str)
    dataset_opened = pyqtSignal(Dataset, TableWidget)
    dataset_appended = pyqtSignal()
    dataset_closed = pyqtSignal()
    df_changed = pyqtSignal(pd.DataFrame)
    table_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dock Window")
        self.setWindowTitle("Dock Window")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        # Create the tabs
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabShape(QTabWidget.Triangular)
        self._data_tab = LeftDockDataTab()
        self._analysis_tab = LeftDockAnalysisTab()
        self._ml_tab = LeftDockMLTab()

        # Add tabs to tab widget

        self._tab_widget.addTab(self._data_tab, self._data_tab.windowTitle())
        self._tab_widget.addTab(self._analysis_tab, self._analysis_tab.windowTitle())
        self._tab_widget.addTab(self._ml_tab, self._ml_tab.windowTitle())

        #self._tab_widget.setTabPosition(QTabWidget.West)

        # Set tab widget as the widget of dock widget
        self.setWidget(self._tab_widget)
        # Keep others disabled till Calculate Info is clicked
        self.disable_tabs()

        self._data_tab.close_dataset.connect(self._analysis_tab.close_dataset)
        self._analysis_tab.info_calculated.connect(self.enable_tabs)
        self._analysis_tab.mask_created_from_xplot.connect(self.mask_created_from_xplot.emit)

        self.dataset_opened.connect(self._data_tab.dataset_opened.emit)
        self.dataset_opened.connect(self._analysis_tab.dataset_opened.emit)
        self.dataset_opened.connect(self._ml_tab.dataset_opened.emit)
        self.dataset_opened.connect(self.enable_analysis_tab)

        self.dataset_appended.connect(self._analysis_tab.dataset_appended.emit)
        self.dataset_appended.connect(self._data_tab.dataset_appended.emit)
        self.dataset_appended.connect(self._ml_tab.dataset_appended.emit)

        # signals from children
        self._data_tab.close_dataset.connect(self.dataset_closed.emit)
        self._data_tab.close_dataset.connect(self.disable_tabs)
        self._data_tab.df_changed.connect(self.df_changed.emit)
        self._data_tab.table_changed.connect(self.table_changed.emit)

    def data_load_button_connect_to(self, func):
            self._data_tab.data_load_button_connect_to(func)

    def enable_analysis_tab(self):
        self._tab_widget.setTabEnabled(1, True)

    def disable_tabs(self):
        for i in range(1, self._tab_widget.count()):
            self._tab_widget.setTabEnabled(i, False)

    def enable_tabs(self):
        for i in range(2, self._tab_widget.count()):
            self._tab_widget.setTabEnabled(i, True)

    def connect_request_selection_signal_to(self, func):
        self._data_editing_tab.request_table_selection.connect(func)

    def dataset_load_method(self):
        return self._data_tab.dataset_load_method()

    def dataset_name(self):
        return self._data_tab.dataset_name()

    def update_analysis_tab_with_window_state(self, state):
        return self._analysis_tab.update_analysis_tab_with_window_state(state)

    @property
    def data_tab(self):
        return self._data_tab

    @property
    def analysis_tab(self):
        return self._analysis_tab

    @property
    def ml_tab(self):
        return self._ml_tab
