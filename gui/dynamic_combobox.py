from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import pyqtSignal


class DynamicComboBox(QComboBox):
        popup_clicked = pyqtSignal()

        def __init__(self, index=-1):
            super().__init__()
            self.index = index

        def showPopup(self):
            self.popup_clicked.emit()
            super(DynamicComboBox, self).showPopup()
