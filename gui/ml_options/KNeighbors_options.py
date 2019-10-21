from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QGridLayout, QGroupBox, QLineEdit

import pandas as pd

from scikit_logger import ScikitLogger


class KNeighborsOptions(QWidget):
    logger = ScikitLogger()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._n_neighbors_lb = QLabel("Number of Neighbors")
        self._n_neighbors_le = QLineEdit()

        self._options_gb = QGroupBox("Options")
        self._options_layout = QGridLayout()
        self._options_layout.addWidget(self._n_neighbors_lb, 0, 0)
        self._options_layout.addWidget(self._n_neighbors_le, 1, 0)
        self._options_gb.setLayout(self._options_layout)
        self._layout = QGridLayout()
        self._layout.addWidget(self._options_gb)
        self.setLayout(self._layout)

    def _validate_parameters(self):
        text = self._n_neighbors_le.text()
        values = text.split(',')
        try:
            numbers = list(map(pd.to_numeric, values))
        except Exception:
            self.logger.exception("n_neighbors must be integer or integers separated by commas")
            return False
        return True

    def gather_parameters(self):
        if not self._validate_parameters():
            return None

        values = self._n_neighbors_le.text().split(',')
        ints_list = []
        for item in values:
            ints_list.append(int(item))
            if ints_list[-1] != item:
                self.logger.error('n_neighbors must be integer(s)')
                return None
        return {'n_neighbors': ints_list}

    @property
    def name(self):
        return "KNeighbors"
