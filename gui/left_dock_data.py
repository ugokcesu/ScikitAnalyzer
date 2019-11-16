from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

import pandas as pd

from dataset import Dataset
from gui.table_widget import TableWidget
from gui.data_loader_tab import DataLoaderTab
from gui.data_editing_tab import DataEditingTab


class LeftDockDataTab(QWidget):
    close_dataset = pyqtSignal()
    dataset_opened = pyqtSignal(Dataset, TableWidget)
    dataset_appended = pyqtSignal()
    df_changed = pyqtSignal(pd.DataFrame)
    table_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("DataTab")
        self.setWindowTitle("Data Loading/Editing")

        self._tab_widget = QTabWidget()
        # self._tab_widget.setTabPosition(QTabWidget.West)
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tab_widget)
        self.setLayout(self._layout)

        self._data_load_tab = DataLoaderTab()
        self._data_editing_tab = DataEditingTab()

        self._tab_widget.addTab(self._data_load_tab, self._data_load_tab.windowTitle())
        self._tab_widget.addTab(self._data_editing_tab, self._data_editing_tab.windowTitle())

        self._tab_widget.setTabEnabled(1, False)

        # incoming signals from children

        self._data_load_tab.close_dataset.connect(self.close_dataset.emit)
        self._data_load_tab.close_dataset.connect(self.disable_editing)
        self._data_editing_tab.df_changed.connect(self.df_changed.emit)
        self._data_editing_tab.table_changed.connect(self.table_changed.emit)


        # outgoing to children
        self.dataset_opened.connect(self._data_editing_tab.dataset_opened)
        self.dataset_opened.connect(self._data_load_tab.dataset_opened)
        self.dataset_opened.connect(self.enable_editing)

    def data_load_button_connect_to(self, func):
            self._data_load_tab.data_load_button_connect_to(func)

    def dataset_load_method(self):
        return self._data_load_tab.dataset_load_method()

    def dataset_name(self):
        return self._data_load_tab.dataset_name()

    def enable_editing(self):
        self._tab_widget.setTabEnabled(1, True)

    def disable_editing(self):
        self._tab_widget.setTabEnabled(1, False)
