from PyQt5.QtWidgets import QWidget, QDockWidget, QTabWidget
from PyQt5.QtCore import Qt

from gui.data_loader_tab import DataLoaderTab
from gui.data_analysis_tab import DataAnalysisTab


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
        # Add tabs to tab widget
        self._tab_widget.addTab(self._data_load_tab, self._data_load_tab.windowTitle())
        self._tab_widget.addTab(self._data_analysis_tab, self._data_analysis_tab.windowTitle())
        # Set tab widget as the widget of dock widget
        self.setWidget(self._tab_widget)

        self._data_load_tab.close_dataset.connect(self._data_analysis_tab.update_upon_closing_dataset)

    @property
    def data_load_tab(self):
        return self._data_load_tab

    @property
    def data_analysis_tab(self):
        return self._data_analysis_tab