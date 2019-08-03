from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QGridLayout, QTextEdit, QSizePolicy,QVBoxLayout,\
    QCheckBox, QTableView

import dataset
import gui.dataset_model


class TableWidget(QWidget):
    def __init__(self, ds, name):
        super().__init__()

        self._window_state = TableWidgetState(name)
        self._description = QTextEdit()
        self._description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._data_table = QTableView()
        self._data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._description, stretch=3)
        self._layout.addWidget(self._data_table, stretch=7)
        self.setLayout(self._layout)

        self.initialize_with_dataset(ds)

    def initialize_with_dataset(self, ds):
        self._description.setText(ds.description())
        model = gui.dataset_model.DatasetModel(ds)
        self._data_table.setModel(model)

    def update_with_state(self, state):
        self.window_state.description_visible = state.description_visible
        self.window_state.table_visible = state.table_visible
        self.show_description(state.description_visible)
        self.show_table(state.table_visible)

    def show_description(self, flag):
        self._description.setVisible(flag)
        self._window_state._description_visible = flag

    def show_table(self, flag):
        self._data_table.setVisible(flag)
        self._window_state._table_visible = flag

    @property
    def window_state(self):
        return self._window_state


class TableWidgetState():
    def __init__(self, name):
        self._description_visible = True
        self._table_visible = True
        self._dataset_name = name

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








