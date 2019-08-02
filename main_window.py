import sys

from PyQt5.Qt import QApplication, QSize, QIcon, QMdiSubWindow, QWidget
from PyQt5.QtWidgets import QMainWindow, QMdiArea, QTableWidget
from PyQt5.QtCore import Qt

from gui.data_loader_dock import DataLoaderDock
import sklearn

import dataset
from gui.table_widget import TableWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data_loader_dock = DataLoaderDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.data_loader_dock)

        self.dataset_dictionary = {}

        self.data_loader_dock.load_button_connect_to(self.create_table_view)


        # MDI SETUP
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        self.table_sub_win_list = []
        self.mdi_area.tileSubWindows()

    def create_table_view(self):
        method_name = self.data_loader_dock.dataset_load_method()
        dataset_name = self.data_loader_dock.dataset_name()
        method = getattr(sklearn.datasets, method_name, None)
        if callable(method):
            skds = method()
            self.dataset_dictionary[dataset_name] = dataset.Dataset(skds)
            self.table_sub_win_list.append(TableWidget(self.dataset_dictionary[dataset_name]))
            self.mdi_area.addSubWindow(self.table_sub_win_list[-1]).show()

            self.mdi_area.tileSubWindows()
        else:
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)

    form = MainWindow()
    form.setWindowTitle("Dataset Analyzer")
    app.setWindowIcon(QIcon("icons/scikit.png"))
    form.show()
    app.exec_()
    ds = dataset.Dataset(sklearn.datasets.load_iris())
    print(ds._df)
