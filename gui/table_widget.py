from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QGridLayout, QTextEdit

import dataset


class TableWidget(QWidget):
    def __init__(self, ds):
        super().__init__()

        self._description = QTextEdit()
        self._data_table = QTableWidget()

        self._layout = QGridLayout()
        self._layout.addWidget(self._description, 0, 0)
        self._layout.addWidget(self._data_table, 1, 0)
        self.setLayout(self._layout)

        self.initialize_with_dataset(ds)

    def initialize_with_dataset(self, ds):
        self._description.setText(ds.description())





