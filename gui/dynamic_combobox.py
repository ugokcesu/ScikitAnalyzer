from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import pyqtSignal


class DynamicComboBox(QComboBox):
        popup_clicked = pyqtSignal()

        def showPopup(self):
            self.popup_clicked.emit()
            super(DynamicComboBox, self).showPopup()
