from PyQt5 import QtCore, QtGui


class DatasetModel(QtGui.QStandardItemModel):
    def __init__(self, data=None, dataFrame=None, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        if dataFrame is None and data is not None:
            self._data = data.data_frame()
        elif data is None and dataFrame is not None:
            self._data = dataFrame
        else:
            return
        for index, row in enumerate(self._data.values.tolist()):
            data_row = []

            for x in row:
                if isinstance(x, float):
                    item = QtGui.QStandardItem()
                    item.setData(float(x), QtCore.Qt.EditRole)
                    # data_row.append(QtGui.QStandardItem("{0:.2f}".format(float(x))))
                    data_row.append(item)
                elif isinstance(x, bool):
                    item = QtGui.QStandardItem()
                    item.setData(bool(x), QtCore.Qt.EditRole)
                    data_row.append(item)
                elif isinstance(x, int):
                    item = QtGui.QStandardItem()
                    item.setData(int(x), QtCore.Qt.EditRole)
                    data_row.append(item)
                else:
                    data_row.append(QtGui.QStandardItem(str(x)))
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

    def flags(self, index):
        row = index.row()
        if self._data.index[row] == "categorical?":
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
