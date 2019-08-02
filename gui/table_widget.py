from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QGridLayout, QTextEdit, QSizePolicy,QVBoxLayout,\
    QCheckBox, QTableView

import dataset
import gui.dataset_model

class TableWidget(QWidget):
    def __init__(self, ds):
        super().__init__()

        self._show_desc_cb = QCheckBox("Show Description")
        self._show_desc_cb.setChecked(True)
        self._show_desc_cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._description = QTextEdit()
        self._description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._data_table = QTableView()
        self._data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._show_desc_cb)
        self._layout.addWidget(self._description, stretch=3)
        self._layout.addWidget(self._data_table, stretch=7)
        self.setLayout(self._layout)

        self.initialize_with_dataset(ds)
        self._show_desc_cb.toggled.connect(self.update_description)

    def initialize_with_dataset(self, ds):
        self._description.setText(ds.description())
        model = gui.dataset_model.DatasetModel(ds)
        self._data_table.setModel(model)

    def update_description(self):
        if not self._show_desc_cb.isChecked():
            self._description.setVisible(False)
        else:
            self._description.setVisible(True)





