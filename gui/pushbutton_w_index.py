from PyQt5.QtWidgets import QPushButton


class PushButtonWIndex(QPushButton):
    def __init__(self, name, index=-1):
        super().__init__(text=name)
        self.index = index
