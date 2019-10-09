from PyQt5.QtWidgets import QWidget, QTextEdit, QSizePolicy,QVBoxLayout, \
    QTableView, QHBoxLayout, QCheckBox
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal


import dataset_model


class TableWidget(QWidget):
    sub_window_closed = pyqtSignal(str)
    checkboxes_clicked = pyqtSignal(object)

    def __init__(self, ds, name, parent):
        super().__init__(parent)
        self._window_state = TableWidgetState(name, ds.column_names())
        self._description_cb = QCheckBox("Show description")
        self._description_cb.setChecked(True)
        self._description = QTextEdit()
        self._description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._table_cb = QCheckBox("Show table")
        self._table_cb.setChecked(True)
        self._data_table = QTableView()
        self._data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._data_table.setAlternatingRowColors(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._data_layout = QVBoxLayout()
        self._data_layout.addWidget(self._description_cb)
        self._data_layout.addWidget(self._description, stretch=3)
        self._data_layout.addWidget(self._table_cb)
        self._data_layout.addWidget(self._data_table, stretch=7)

        self._window_layout = QHBoxLayout()
        self._plot_layout = QVBoxLayout()
        self._window_layout.addLayout(self._data_layout)
        self._window_layout.addLayout(self._plot_layout)
        self.setLayout(self._window_layout)

        self._description_cb.toggled.connect(self.checkbox_clicked)
        self._table_cb.clicked.connect(self.checkbox_clicked)
        self.initialize_with_dataset(ds)

    def initialize_with_dataset(self, ds):
        self._description.setText(ds.description())
        model = dataset_model.DatasetModel(data=ds)
        self._data_table.setModel(model)
        self.setWindowTitle(ds.name)
        self._description_cb.setChecked(True)
        self._table_cb.setChecked(True)

    def update_with_ds(self, ds):
        self._description.setText(ds.description())
        model = dataset_model.DatasetModel(data=ds)
        self._data_table.setModel(model)
        self.setWindowTitle(ds.name)
        self._description_cb.setChecked(True)
        self._table_cb.setChecked(True)
        self.window_state.column_names = ds.df.columns

    def update_with_state(self, state):
        self.window_state.description_visible = state.description_visible
        self.window_state.table_visible = state.table_visible
        self.show_description(state.description_visible)
        self.show_table(state.table_visible)

    def show_description(self, flag):
        self._description.setVisible(flag)
        self._description_cb.setChecked(flag)
        self._window_state._description_visible = flag

    def show_table(self, flag):
        self._data_table.setVisible(flag)
        self._table_cb.setChecked(flag)
        self._window_state._table_visible = flag

    def checkbox_clicked(self):
        self.show_table(self._table_cb.isChecked())
        self.show_description(self._description_cb.isChecked())
        self.window_state.table_visible = self._table_cb.isChecked()
        self.window_state.description_visible = self._description_cb.isChecked()
        self.checkboxes_clicked.emit(self.window_state)

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.sub_window_closed.emit(self.window_state.dataset_name)

    def get_selection(self):
        return self._data_table.selectedIndexes()

    @property
    def data_table(self):
        return self._data_table

    @property
    def window_state(self):
        return self._window_state


class TableWidgetState:
    def __init__(self, name, columns):
        self._description_visible = True
        self._table_visible = True
        self._dataset_name = name
        self._column_names = columns

    @property
    def description_visible(self):
        return self._description_visible

    @description_visible.setter
    def description_visible(self, value):
        self._description_visible = value

    @property
    def table_visible(self):
        return self._table_visible

    @table_visible.setter
    def table_visible(self, value):
        self._table_visible = value



    @property
    def dataset_name(self):
        return self._dataset_name

    @property
    def column_names(self):
        return self._column_names

    @column_names.setter
    def column_names(self, v):
        self._column_names = v








