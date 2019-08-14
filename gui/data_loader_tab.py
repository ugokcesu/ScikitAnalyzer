from PyQt5.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPushButton,\
    QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

import sklearn.datasets


class DataLoaderTab(QWidget):
    close_dataset = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._prefix = "load_"

        self.setObjectName("DataLoaderDock")
        self.setWindowTitle("Data Loading")

        self._is_a_ds_loaded = False

        # New Dataset loading/closing widgets
        self._dataset_list = QComboBox()
        self._dataset_list.addItems(self.list_datasets())
        self._load_btn = QPushButton("Load")
        self._close_btn = QPushButton("Close")
        # New Dataset loading layout
        self._loading_layout = QHBoxLayout()
        self._loading_layout.addWidget(self._dataset_list, 0)
        self._loading_layout.addWidget(self._load_btn, 1)
        self._loading_layout.addWidget(self._close_btn, 2)
        self._loading_layout.setAlignment(Qt.AlignTop)
        #New Dataset loading groupbox
        self._load_gb = QGroupBox()
        self._load_gb.setTitle("Load New Dataset")
        self._load_gb.setLayout(self._loading_layout)

        # Layout for entire tab
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._load_gb, 0)

        self._layout.setAlignment(Qt.AlignTop)
        self.setLayout(self._layout)

        self._close_btn.clicked.connect(self.close_ds)

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

    # slot to be connected to main_window's create_table_view method
    def dataset_opened(self, dataset_name):
        self._dataset_list.setDisabled(True)
        self._load_btn.setDisabled(True)
        self._close_btn.setDisabled(False)
        self._is_a_ds_loaded = True


    def close_ds(self):
        choice = QMessageBox.question(self, "Close Dataset?", "Closing dataset will delete all windows. Continue?", \
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.close_dataset.emit()
            self._close_btn.setDisabled(True)
            self._dataset_list.setDisabled(False)
            self._load_btn.setDisabled(False)
