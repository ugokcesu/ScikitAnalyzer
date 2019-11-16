import sys
import pandas as pd

from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QGridLayout, QGroupBox, QLineEdit, QToolTip
from PyQt5.Qt import QApplication, QIcon

from scikit_logger import ScikitLogger
from gui.gui_helper import GuiHelper


class KNeighborsOptions(QWidget):
    logger = ScikitLogger()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KNeighbors")
        self._n_neighbors_lb = QLabel("Number of Neighbors")
        self._n_neighbors_le = QLineEdit()
        self._n_neighbors_le.setToolTip("single number or separated by commas")
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
            numbers = list(map(int, values))
        except Exception:
            self.logger.exception("n_neighbors must be integer or integers separated by commas")
            GuiHelper.point_to_error(self._n_neighbors_le)
            return False
        return True

    def gather_parameters(self):
        if not self._validate_parameters():
            return None
        values = self._n_neighbors_le.text().split(',')
        ints_list = []
        for item in values:
            ints_list.append(int(item))
            if ints_list[-1] != pd.to_numeric(item):
                self.logger.error('n_neighbors must be integer or integers separated by commas')
                GuiHelper.point_to_error(self._n_neighbors_le)
                return None
        return {'n_neighbors': ints_list}

    @property
    def name(self):
        return "KNeighbors"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = KNeighborsOptions()
    form.setWindowTitle("Testing")
    app.setWindowIcon(QIcon("icons/scikit.png"))
    form.show()
    app.exec_()

