from PyQt5.QtWidgets import QWidget, QDockWidget, QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal

from gui.data_loader_tab import DataLoaderTab
from gui.data_analysis_tab import DataAnalysisTab
from gui.data_analysis_tab_multi import DataAnalysisTabMulti
from gui.data_editing_tab import DataEditingTab
from gui.fit_predict_tab import FitPredictTab

from dataset import Dataset
from gui.table_widget import TableWidget


class LeftDock(QDockWidget):
    mask_created_from_xplot = pyqtSignal(str)
    dataset_opened = pyqtSignal(Dataset, TableWidget)
    dataset_appended = pyqtSignal()
    dataset_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dock Window")
        self.setWindowTitle("Dock Window")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self._tab_widget = QTabWidget()
        # Create the tabs
        self._data_load_tab = DataLoaderTab()
        self._data_analysis_tab = DataAnalysisTab()
        self._data_analysis_tab_multi = DataAnalysisTabMulti()
        self._data_editing_tab = DataEditingTab()
        self._fit_predict_tab = FitPredictTab()

        # Add tabs to tab widget
        self._tab_widget.addTab(self._data_load_tab, self._data_load_tab.windowTitle())
        self._tab_widget.addTab(self._data_analysis_tab, self._data_analysis_tab.windowTitle())
        self._tab_widget.addTab(self._data_analysis_tab_multi, self._data_analysis_tab_multi.windowTitle())
        self._tab_widget.addTab(self._fit_predict_tab, self._fit_predict_tab.windowTitle())
        self._tab_widget.addTab(self._data_editing_tab, self._data_editing_tab.windowTitle())

        # Set tab widget as the widget of dock widget
        self.setWidget(self._tab_widget)
        # Keep others disabled till Calculate Info is clicked
        self.disable_tabs()

        self._data_load_tab.close_dataset.connect(self._data_analysis_tab.update_upon_closing_dataset)
        self._data_analysis_tab.info_calculated.connect(self.enable_tabs)
        self._data_analysis_tab_multi.mask_created_from_xplot.connect(self.mask_created_from_xplot.emit)

        self.dataset_opened.connect(self.data_load_tab.dataset_opened)
        self.dataset_opened.connect(self.data_analysis_tab.dataset_opened)
        self.dataset_opened.connect(self.data_analysis_tab_multi.dataset_opened)
        self.dataset_opened.connect(self.data_editing_tab.dataset_opened)
        self.dataset_opened.connect(self.fit_predict_tab.dataset_opened)
        self.dataset_opened.connect(self.enable_analysis_tab)

        self.dataset_appended.connect(self.data_analysis_tab.dataset_opened)
        self.dataset_appended.connect(self.data_analysis_tab_multi.dataset_opened)
        self.dataset_appended.connect(self.data_editing_tab.dataset_opened)
        self.dataset_appended.connect(self.fit_predict_tab.dataset_opened)

        self.data_load_tab.close_dataset.connect(self.dataset_closed.emit)
        self.data_load_tab.close_dataset.connect(self.disable_tabs)

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


    @property
    def data_load_tab(self):
        return self._data_load_tab

    @property
    def data_analysis_tab(self):
        return self._data_analysis_tab

    @property
    def data_editing_tab(self):
        return self._data_editing_tab

    @property
    def data_analysis_tab_multi(self):
        return self._data_analysis_tab_multi

    @property
    def fit_predict_tab(self):
        return self._fit_predict_tab
