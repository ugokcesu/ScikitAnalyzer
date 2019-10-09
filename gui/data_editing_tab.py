from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt

import pandas as pd

from dataset import Dataset

class DataEditingTab(QWidget):
    request_table_selection = pyqtSignal()
    df_changed = pyqtSignal(pd.DataFrame)
    table_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DataEditingDock")
        self.setWindowTitle("Data Editing")

        self._ds_name = ""
        self._ds_columns = []
        self._current_table_widget = None
        self._current_df = None
        self._categorical_df = None
        self._categorical_columns = []

        self.drop_btn = QPushButton("Drop Selected Columns")
        self.one_hot_btn = QPushButton("Create 1-Off for Selected Columns")

        self._layout = QVBoxLayout()
        self._layout.addWidget(self.drop_btn)
        self._layout.addWidget(self.one_hot_btn)
        self.setLayout(self._layout)
        self._layout.setAlignment(Qt.AlignTop)

        self.drop_btn.clicked.connect(self.drop_columns)
        self.one_hot_btn.clicked.connect(self.create_one_hot)

    # this should be in dataset class or in something like dataset_editor
    def create_one_hot(self):
        cols, axis = self.get_table_selection()
        column_names = self.current_df.columns[cols]
        df = pd.get_dummies(self.current_df, columns=column_names)
        print(self.current_df)
        # connects to when data is loaded, after QTableview is created in main window
        self.df_changed.emit(df)

    # this should be in dataset class or in something like dataset_editor
    def drop_columns(self):
        cols, axis = self.get_table_selection()
        column_names = self.current_df.columns[cols]
        self.current_df.drop(column_names, axis=axis, inplace=True)
        #connects to when data is loaded, after QTableview is created in main window
        self.table_changed.emit()

    def get_table_selection(self):
        selection = self.current_table_widget.data_table.selectionModel()
        columns = [x.column() for x in selection.selectedColumns()]
        return columns, 1


    @property
    def current_table_widget(self):
        return self._current_table_widget

    @current_table_widget.setter
    def current_table_widget(self, widget):
        self._current_table_widget = widget

    def dataset_opened(self, ds, table_widget):
        self.current_table_widget = table_widget
        self.current_df = ds.df


