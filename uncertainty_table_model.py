from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt


class UncertaintyTableModel(QtGui.QStandardItemModel):
    def __init__(self, base, secondary, data=None, dataFrame=None, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        if dataFrame is None and data is not None:
            self._data = data.df
        elif data is None and dataFrame is not None:
            self._data = dataFrame
        else:
            return
        self._base = base
        self._secondary = secondary
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
        self.assign_colors()
        return

    def assign_colors(self):
        max_row = self._data['mean_test_score'].idxmax()
        min_row = self._data['mean_test_score'].idxmin()
        if self._base:
            base_row = self._data[self._data['columns'].apply(lambda x: x == self._base)].index[0]
            base = self.takeRow(base_row)
            for item in base:
                item.setBackground(Qt.blue)
            self.insertRow(base_row, base)
        min_idx = self.takeRow(min_row)
        for item in min_idx:
            item.setBackground(Qt.red)
        self.insertRow(min_row, min_idx)
        max_idx = self.takeRow(max_row)
        for item in max_idx:
            item.setBackground(Qt.green)
        self.insertRow(max_row, max_idx)


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
