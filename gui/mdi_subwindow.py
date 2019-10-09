from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from gui.table_widget import TableWidget


class MdiSubWindow(QMdiSubWindow):
    def __init__(self, ds, name, parent = None):
        super().__init__()
        self.table_widget = TableWidget(ds, name, parent)
        self.setWidget(self.table_widget)


    # we want to be able to show it again if user closes it
    # setting QA_Quitonclose doesn't help because the tables come up empty
    def closeEvent(self, closeEvent: QtGui.QCloseEvent):
        self.hide()

