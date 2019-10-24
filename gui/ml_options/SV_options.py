from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QGridLayout, QGroupBox, QLineEdit, QToolTip
from PyQt5.QtCore import QPoint, QTimer
import pandas as pd

from scikit_logger import ScikitLogger


class SVOptions(QWidget):
    logger = ScikitLogger()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._gamma_lb = QLabel("Gamma")
        self._gamma_le = QLineEdit()
        self._gamma_le.setToolTip("float or list of comma delimited floats")
        self._c_lb = QLabel("C")
        self._c_le = QLineEdit()
        self._c_le.setToolTip("float or list of comma delimited floats")

        self._options_gb = QGroupBox("Options")
        self._options_layout = QGridLayout()
        self._options_layout.addWidget(self._gamma_lb, 0, 0)
        self._options_layout.addWidget(self._gamma_le, 1, 0)
        self._options_layout.addWidget(self._c_lb, 2, 0)
        self._options_layout.addWidget(self._c_le, 3, 0)
        self._options_gb.setLayout(self._options_layout)
        self._layout = QGridLayout()
        self._layout.addWidget(self._options_gb)
        self.setLayout(self._layout)

    def _validate_float_parameters(self, widget):
        text = widget.text()
        values = text.split(',')
        try:
            numbers = list(map(pd.to_numeric, values))
        except Exception:
            self.logger.exception("{} must be floats or floats separated by commas".format(widget.objectName()))
            return False
        return True

    def gather_parameters(self):
        for widget in [self._c_le, self._gamma_le]:
            if not self._validate_float_parameters(widget):
                return None
        gamma_values = self._gamma_le.text().split(',')
        try:
            gamma_list = list(map(float, gamma_values))
        except ValueError:
            self.logger.exception('Cannot convert input to float')
            SVOptions.point_to_error(self._gamma_le)
            return None
        c_values = self._c_le.text().split(',')
        try:
            c_list = list(map(float, c_values))
        except ValueError:
            self.logger.exception('Cannot convert input to float')
            SVOptions.point_to_error(self._c_le)
            return None
        return {'C': c_list, 'gamma': gamma_list}

    @property
    def name(self):
        return "SV"

    @staticmethod
    def point_to_error(widget):
        widget.setStyleSheet("background-color:pink;")
        QTimer.singleShot(400, lambda x=widget: x.setStyleSheet("background-color:white;"))
        QToolTip.showText(widget.mapToGlobal(QPoint(0, 0)), widget.toolTip())
