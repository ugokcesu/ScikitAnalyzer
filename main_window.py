import sys

from PyQt5.Qt import QApplication, QSize, QIcon, QMdiSubWindow, QWidget, QDockWidget, QTabWidget
from PyQt5.QtWidgets import QMainWindow, QMdiArea, QTableWidget, QAction
from PyQt5.QtCore import Qt, pyqtSignal

from gui.data_loader_tab import DataLoaderTab
import sklearn

from dataset import Dataset
from gui.table_widget import TableWidget
from gui.left_dock import LeftDock
from gui.mdi_subwindow import MdiSubWindow
from gui.plot_window import PlotWindow

class MainWindow(QMainWindow):
    dataset_opened = pyqtSignal(Dataset)

    def __init__(self):
        super().__init__()

        self.left_dock = LeftDock()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.left_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dataset_dictionary = {}

        # MDI SETUP
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        self.table_sub_window = None
        self.mdi_area.subWindowActivated.connect(self.left_dock.data_analysis_tab.update_upon_window_activation)

        self.left_dock.data_load_tab.load_button_connect_to(self.create_table_view)
        self.dataset_opened.connect(self.left_dock.data_load_tab.dataset_opened)
        self.dataset_opened.connect(self.left_dock.data_analysis_tab.dataset_opened)
        self.left_dock.data_load_tab.close_dataset.connect(self.mdi_area.closeAllSubWindows)
        self.left_dock.data_analysis_tab.request_plot_generation.connect(self.generate_plot_mdi)

        # Toolbars
        self.view_toolbar = self.addToolBar("View Toolbar")
        self.tile_action = QAction(QIcon("icons/tile.png"), "Tile Windows")
        self.tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        self.cascade_action = QAction(QIcon("icons/cascade"), "Cascade Windows")
        self.cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        self.open_table_action = QAction("Open Table Window")
        self.open_table_action.triggered.connect(self.re_open_table_window)
        self.view_toolbar.addAction(self.tile_action)
        self.view_toolbar.addAction(self.cascade_action)
        self.view_toolbar.addAction(self.open_table_action)

    def generate_plot_mdi(self, window, title):
        if title == "Info Stats":
            for sub in self.mdi_area.subWindowList():
                if sub.windowTitle() == title:
                    sub.close()
        self.mdi_area.addSubWindow(window)
        window.setWindowTitle(title)
        window.show()
        self.mdi_area.tileSubWindows()

    def create_table_view(self):
        method_name = self.left_dock.data_load_tab.dataset_load_method()
        dataset_name = self.left_dock.data_load_tab.dataset_name()
        method = getattr(sklearn.datasets, method_name, None)
        # TODO later decide if necessary to keep datasets in a dict
        if dataset_name in self.dataset_dictionary:
            return None
        if callable(method):
            try:
                skds = method()
            except TypeError:
                return None
            ds = Dataset.create_dataset(skds, dataset_name)
            if ds is not None:
                self.dataset_dictionary[dataset_name] = ds
                self.table_sub_window = MdiSubWindow(self.dataset_dictionary[dataset_name], dataset_name, self)
                self.table_sub_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.Tool)
                self.mdi_area.addSubWindow(self.table_sub_window)
                self.table_sub_window.show()
                self.mdi_area.tileSubWindows()
                self.dataset_opened.emit(self.dataset_dictionary[dataset_name])
            else:
                return None
        else:
            return None

    def remove_dataset_from_dictionary(self, name):
        self.dataset_dictionary.pop(name)

    def list_opened_datasets(self):
        return self.dataset_dictionary.keys()

    def re_open_table_window(self):
        if self.table_sub_window is not None:
            self.table_sub_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    form = MainWindow()
    form.setWindowTitle("Dataset Analyzer")
    app.setWindowIcon(QIcon("icons/scikit.png"))
    form.show()
    app.exec_()

