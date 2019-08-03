from PyQt5.QtWidgets import QWidget, QDockWidget, QGridLayout, QLabel, QSpinBox, QComboBox, QPushButton
from PyQt5.QtCore import Qt

import sklearn.datasets


class DataLoaderTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._prefix = "load_"

        self.setObjectName("DataLoaderDock")
        self.setWindowTitle("Data Loading")

        self._dataset_list = QComboBox()
        self._dataset_list.addItems(self.list_datasets())
        self._load_btn = QPushButton("Load")

        self._layout = QGridLayout()
        self._layout.addWidget(self._dataset_list, 0, 0)
        self._layout.addWidget(self._load_btn, 0, 1)
        self._layout.setAlignment(Qt.AlignTop)
        self.setLayout(self._layout)

    def load_button_connect_to(self, func):
        self._load_btn.clicked.connect(func)

    def dataset_load_method(self):
        return self._prefix + self._dataset_list.currentText()

    def dataset_name(self):
        return self._dataset_list.currentText()

    def list_datasets(self):
        datasets = []
        for ds in sklearn.datasets.__all__:
            if ds.startswith(self._prefix):
                datasets.append(ds[len(self._prefix):])
        print(datasets)
        return datasets

