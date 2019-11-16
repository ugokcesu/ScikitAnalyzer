from PyQt5.QtWidgets import QListWidget
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal


class ListWidget(QListWidget):
    mouse_up = pyqtSignal()

    def __init__(self):
        super().__init__()

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        super().mouseReleaseEvent(e)
        self.mouse_up.emit()
