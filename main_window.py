import sys

from PyQt5.Qt import QApplication, QSize, QIcon, QMdiSubWindow, QWidget, QDockWidget, QTabWidget, QPushButton, QLayout
from PyQt5.QtWidgets import QMainWindow, QMdiArea, QTableWidget, QAction, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal

from gui.data_loader_tab import DataLoaderTab
import sklearn

from dataset import Dataset
from gui.table_widget import TableWidget
from gui.left_dock import LeftDock
from gui.mdi_subwindow import MdiSubWindow
from gui.range_slider import QRangeSlider
from gui.plot_window import PlotWindow
from gui.dynamic_combobox import DynamicComboBox

class MainWindow(QMainWindow):
    dataset_opened = pyqtSignal(Dataset, TableWidget)
    dataset_updated = pyqtSignal(Dataset, TableWidget)
    dataset_appended = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.left_dock = LeftDock()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.left_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dataset_dictionary = {}
        self._current_dataset_name = ""

        # MDI SETUP
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        self.table_sub_window = None
        self.mdi_area.subWindowActivated.connect(self.left_dock.data_analysis_tab.update_upon_window_activation)

        #CONNECTIONS

        # signals from dock, related to dataset updates
        self.left_dock.data_load_tab.load_button_connect_to(self.create_table_view)
        self.left_dock.mask_created_from_xplot.connect(self.append_table)

        # outgoing signals related to dataset updated
        self.dataset_opened.connect(self.left_dock.dataset_opened.emit)

        self.dataset_updated.connect(self.disable_window_widgets)
        self.dataset_updated.connect(self.left_dock.dataset_opened.emit)

        self.dataset_appended.connect(self.left_dock.dataset_appended.emit)

        self.left_dock.data_load_tab.close_dataset.connect(self.mdi_area.closeAllSubWindows)
        self.left_dock.data_load_tab.close_dataset.connect(self.remove_current_dataset)

        self.left_dock.data_analysis_tab.request_plot_generation.connect(self.generate_plot_mdi)
        self.left_dock.data_analysis_tab_multi.request_plot_generation.connect(self.generate_plot_mdi)
        self.left_dock.fit_predict_tab.request_plot_generation.connect(self.generate_plot_mdi)
        self.left_dock.data_analysis_tab.info_calculated.connect(self.set_categoricals)

        # Toolbars
        self.view_toolbar = self.addToolBar("View Toolbar")
        self.tile_action = QAction(QIcon("icons/tile.png"), "Tile Windows")
        self.tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        self.cascade_action = QAction(QIcon("icons/cascade"), "Cascade Windows")
        self.cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        self.open_table_action = QAction("Open Table Window")
        self.open_table_action.triggered.connect(self.re_open_table_window)
        self.close_all_action = QAction("Close All")
        self.close_all_action.triggered.connect(self.close_all)
        self.view_toolbar.addAction(self.tile_action)
        self.view_toolbar.addAction(self.cascade_action)
        self.view_toolbar.addAction(self.open_table_action)
        self.view_toolbar.addAction(self.close_all_action)

    def close_all(self):
        for window in self.mdi_area.subWindowList():
            window.close()

    def set_categoricals(self, cats):
        self.current_ds._categorical_columns = cats

    def update_categoricals(self, cat):
        if cat not in self.current_ds.column_names():
            return
        if cat not in self.current_ds.categorical_columns:
            self.current_ds.categorical_columns.append(cat)

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
                self._current_dataset_name = dataset_name
                self.dataset_dictionary[dataset_name] = ds
                self.current_ds = ds
                self.table_sub_window = MdiSubWindow(self.dataset_dictionary[dataset_name], dataset_name, self)
                self.table_sub_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.Tool)
                self.mdi_area.addSubWindow(self.table_sub_window)
                self.table_sub_window.show()
                self.table_sub_window.table_widget.checkboxes_clicked.connect(self.left_dock.data_analysis_tab.update_self_with_window_state)
                self.mdi_area.tileSubWindows()
                self.dataset_opened.emit(self.dataset_dictionary[dataset_name], self.table_sub_window.table_widget)
                self.left_dock.data_editing_tab.table_changed.connect(self.update_table)
                self.left_dock.data_editing_tab.df_changed.connect(self.update_df)
            else:
                return None
        else:
            return None

    def remove_dataset_from_dictionary(self, name):
        self.dataset_dictionary.pop(name)

    def remove_current_dataset(self):
        self.dataset_dictionary.pop(self._current_dataset_name)

    def list_opened_datasets(self):
        return self.dataset_dictionary.keys()

    def re_open_table_window(self):
        if self.table_sub_window is not None:
            self.table_sub_window.show()

    # new column was added (existing was not deleted/modified)
    # widgets in windows do not need to be disabled
    def append_table(self, name):
        self.table_sub_window.table_widget.update_with_ds(self.dataset_dictionary[self._current_dataset_name])
        self.update_categoricals(name)
        self.dataset_appended.emit()

    def update_table(self):
        self.table_sub_window.table_widget.update_with_ds(self.dataset_dictionary[self._current_dataset_name])
        self.dataset_updated.emit(self.dataset_dictionary[self._current_dataset_name], self.table_sub_window.table_widget)

    # This is needed when the operation is not inplace=True, and a new copy of ds needs to be sent to main window
    def update_df(self, df):
        self.dataset_dictionary[self._current_dataset_name].df = df
        self.update_table()

    # connected to dataset_updated
    def disable_window_widgets(self, ds, _):
        for sub in self.mdi_area.subWindowList():
            if sub.windowTitle() == "XPlot Window":
                for child in sub.findChildren(QWidget):
                    if isinstance(child, QRangeSlider) or isinstance(child, QPushButton) or \
                            isinstance(child, QCheckBox) or isinstance(child, DynamicComboBox):
                        child.setDisabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainWindow()
    form.setWindowTitle("Data Analyzer")
    app.setWindowIcon(QIcon("icons/scikit.png"))
    form.show()
    app.exec_()

