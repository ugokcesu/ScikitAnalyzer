from PyQt5.Qt import QMdiArea


class MdiArea(QMdiArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def tileSubWindows(self):
        min_size = self.parent().minimumSize()
        max_size = self.parent().maximumSize()
        self.parent().setFixedSize(self.parent().size())
        super(MdiArea, self).tileSubWindows()
        self.parent().setMinimumSize(min_size)
        self.parent().setMaximumSize(max_size)

