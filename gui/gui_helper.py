from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QToolTip

class GuiHelper:
    @staticmethod
    def point_to_error(widget):
        original_style = widget.styleSheet()
        widget.setStyleSheet("background-color:pink;")
        QTimer.singleShot(400, lambda x=widget: x.setStyleSheet(original_style))
        QToolTip.showText(widget.mapToGlobal(QPoint(0, 0)), widget.toolTip())
