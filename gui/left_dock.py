from PyQt5.QtWidgets import QWidget, QDockWidget, QTabWidget
from PyQt5.QtCore import Qt

from gui.data_loader_tab import DataLoaderTab
from gui.data_analysis_tab import DataAnalysisTab
from gui.data_analysis_tab_multi import DataAnalysisTabMulti
from gui.data_editing_tab import DataEditingTab
from gui.fit_predict_tab import FitPredictTab

class LeftDock(QDockWidget):
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
        self._tab_widget.addTab(self._data_editing_tab, self._data_editing_tab.windowTitle())
        self._tab_widget.addTab(self._fit_predict_tab, self._fit_predict_tab.windowTitle())

        # Set tab widget as the widget of dock widget
        self.setWidget(self._tab_widget)
        # Keep others disabled till Calculate Info is clicked
        self.disable_tabs()

        self._data_load_tab.close_dataset.connect(self._data_analysis_tab.update_upon_closing_dataset)
        self._data_analysis_tab.info_calculated.connect(self.enable_tabs)

    def disable_tabs(self):
        for i in range(2, self._tab_widget.count()):
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
