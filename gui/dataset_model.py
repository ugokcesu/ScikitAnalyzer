from PyQt5 import QtCore, QtGui


class DatasetModel(QtGui.QStandardItemModel):
    def __init__(self, data, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self._data = data.data_frame()
        for row in self._data.values.tolist():
            data_row = []
            for x in row:
                try:
                    data_row.append(QtGui.QStandardItem("{0:.2f}".format(float(x))))
                except ValueError:
                    data_row.append(QtGui.QStandardItem(x))
            self.appendRow(data_row)
        return

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[x]
        return None
