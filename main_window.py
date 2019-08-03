import sys

from PyQt5.Qt import QApplication, QSize, QIcon, QMdiSubWindow, QWidget, QDockWidget, QTabWidget
from PyQt5.QtWidgets import QMainWindow, QMdiArea, QTableWidget
from PyQt5.QtCore import Qt

from gui.data_loader_tab import DataLoaderTab
import sklearn

import dataset
from gui.table_widget import TableWidget
from gui.left_dock import LeftDock

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.left_dock = LeftDock()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.left_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dataset_dictionary = {}

        self.left_dock.data_load_tab.load_button_connect_to(self.create_table_view)


        # MDI SETUP
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        self.table_sub_win_list = []
        self.mdi_area.tileSubWindows()

        self.mdi_area.subWindowActivated.connect(self.left_dock.data_analysis_tab.update_upon_window_activation)

    def create_table_view(self):
        method_name = self.left_dock.data_load_tab.dataset_load_method()
        dataset_name = self.left_dock.data_load_tab.dataset_name()
        method = getattr(sklearn.datasets, method_name, None)
        if callable(method):
            try:
                skds = method()
            except TypeError:
                return None
            self.dataset_dictionary[dataset_name] = dataset.Dataset(skds)
            self.table_sub_win_list.append(TableWidget(self.dataset_dictionary[dataset_name], dataset_name))
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
