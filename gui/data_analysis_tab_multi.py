from PyQt5.QtWidgets import QWidget, QCheckBox, QGridLayout, QLabel, QComboBox, QGroupBox, QPushButton, QVBoxLayout,\
    QListWidget, QAbstractItemView, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QSizePolicy

from gui.table_widget import TableWidgetState, TableWidget
from gui.plot_window import PlotWindow
from gui.dynamic_combobox import DynamicComboBox
from plot_generator import PlotGenerator


class DataAnalysisTab(QWidget):
    request_plot_generation = pyqtSignal(QWidget, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DataAnalysisDock")
        self.setWindowTitle("Univariate Analysis")

        self._ds_name = ""
        self._ds_columns = []
        self._current_table_widget = None
        self._current_dataset = None
        self._categorical_df = None
        self._categorical_columns = []
        self._plot_generator = None

        # viewing options widgets and layout
        self._current_ds_lb = QLabel("Current Dataset:")
        self._view_description_cb = QCheckBox("Show description")
        self._view_table_cb = QCheckBox("Show Table")

        self._view_layout = QVBoxLayout()
        self._view_layout.addWidget(self._current_ds_lb)
        self._view_layout.addWidget(self._view_description_cb)
        self._view_layout.addWidget(self._view_table_cb)
        # viewing options group
        self._view_gb = QGroupBox()
        self._view_gb.setTitle("View Options")
        self._view_gb.setLayout(self._view_layout)

        # info statistics
        self._info_calculate_btn = QPushButton("Calculate Info")
        self._info_convert_to_int_cb = QCheckBox("Convert to int if possible")
        self._info_convert_to_int_cb.setChecked(True)
        self._info_categorical_limit_lb = QLabel("Max unique values for categoricals")
        self._info_cat_limit_sb = QSpinBox()
        self._info_cat_limit_sb.setValue(5)
        self._info_cat_limit_sb.setRange(2, 10000)

        self._info_layout = QGridLayout()
        self._info_layout.addWidget(self._info_convert_to_int_cb, 0, 0)
        self._info_layout.addWidget(self._info_categorical_limit_lb, 1, 0)
        self._info_layout.addWidget(self._info_cat_limit_sb, 1, 1)
        self._info_layout.addWidget(self._info_calculate_btn, 2, 0)
        self._info_gb = QGroupBox("Info Statistics")
        self._info_gb.setLayout(self._info_layout)

        #histogram group
        self._hist_data_lb = QLabel("Use column:")
        self._hist_data = QListWidget()
        self._hist_data.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._hist_color_by_lb = QLabel("Color By:")
        self._hist_color_by = DynamicComboBox()
        self._hist_color_by.popup_clicked.connect(self.fill_color_by)
        self._hist_plot = QPushButton("Plot Histogram")

        self._hist_layout = QGridLayout()
        self._hist_layout.addWidget(self._hist_data_lb, 0, 0)
        self._hist_layout.addWidget(self._hist_data, 0, 1)
        self._hist_layout.addWidget(self._hist_color_by_lb, 1, 0)
        self._hist_layout.addWidget(self._hist_color_by, 1, 1)
        self._hist_layout.addWidget(self._hist_plot, 2, 0, 1, 2)
        self._hist_layout.setAlignment(Qt.AlignTop)
        self._hist_gb = QGroupBox("Histogram")
        self._hist_gb.setLayout(self._hist_layout)

        # layout for the whole tab
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.addWidget(self._view_gb, 0, 0)
        self._layout.addWidget(self._info_gb, 1, 0)
        self._layout.addWidget(self._hist_gb, 2, 0)
        self.setLayout(self._layout)

        # signal slot connections
        self._view_table_cb.clicked.connect(self.update_table_widget)
        self._view_description_cb.clicked.connect(self.update_table_widget)
        self._hist_plot.clicked.connect(self.plot_histogram)
        self._info_calculate_btn.clicked.connect(self.calculate_info)

        # keep histogram area grayed out until info stats are calculated

    def dataset_opened(self, ds, _):
        self.set_plot_generator(ds)
        self.disable_histogram()
        self._ds_name = ds.name
        self._ds_columns = ds.column_names()
        self._hist_data.clear()
        self._hist_color_by.clear()
        self._hist_color_by.addItem("")
        self._hist_color_by.setCurrentIndex(0)
        self._hist_data.addItems(self._ds_columns)

    def disable_histogram(self):
        self._hist_gb.setDisabled(True)

    def enable_histogram(self):
        self._hist_gb.setDisabled(False)

    # when checkboxes are clicked, send updates to the TableView
    # I am guessing this should emit a signal which main window should pick up
    def update_table_widget(self):
        if self._current_table_widget is not None:
            state = TableWidgetState("dummy", "dummy")
            state.table_visible = self._view_table_cb.isChecked()
            state.description_visible = self._view_description_cb.isChecked()
            try:
                self._current_table_widget.update_with_state(state)
            except RuntimeError:
                self._current_table_widget = None
                self._current_ds_lb.setText("")
                self._ds_name = ""
                self._ds_columns = ""
                self._hist_plot.setDisabled(True)

    def update_upon_window_activation(self):
        sender = self.sender()
        try:
            widget = sender.activeSubWindow().widget()
        except AttributeError:
            # all sub windows have been closed
            self.setDisabled(True)
            return
        if isinstance(widget, TableWidget):
            self._current_table_widget = widget
            self.setDisabled(False)
            self.update_self_with_window_state(self._current_table_widget.window_state)
            return
        else:
            # a plot window was clicked, don't update dock
            return

    # connect to dataLoader tab's close_ds method
    def update_upon_closing_dataset(self):
        self.setDisabled(True)
        self._hist_color_by.clear()
        self._hist_data.clear()
        self._ds_columns = []
        self._categorical_columns = []

    # when a new mdi window is selected, set the view checkboxes
    def update_self_with_window_state(self, state):
        self._view_table_cb.setChecked(state.table_visible)
        self._view_description_cb.setChecked(state.description_visible)
        self._current_ds_lb.setText("Current Dataset: {}".format(state.dataset_name))
        self._ds_name = state.dataset_name
        self._ds_columns = state.column_names
        self._hist_data.clear()
        self._hist_color_by.clear()
        self._hist_color_by.addItem("")
        self._hist_color_by.setCurrentIndex(0)
        self._hist_data.addItems(self._ds_columns)
        self._hist_data.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self._hist_data.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self._hist_color_by.addItems(self._ds_columns)
        self._hist_plot.setDisabled(False)

    def plot_histogram(self):
        window = self._plot_generator.generate_histogram(self._hist_data.selectedItems(), self._hist_color_by.currentText())
        self.request_plot_generation.emit(window, "Histogram Window")

    def calculate_info(self):
        conv = self._info_convert_to_int_cb.isChecked()
        cat = self._info_cat_limit_sb.value()
        window, self._categorical_df = self._plot_generator.info(convert=conv, cat_limit=cat)
        self.request_plot_generation.emit(window, "Info Stats")
        window.model().itemChanged.connect(self.table_edited)
        self._categorical_columns = []
        for index, col in enumerate(self._ds_columns):
            if self._categorical_df[index]:
                self._categorical_columns.append(col)
        self.enable_histogram()

    def table_edited(self, sender):
        print(" I changed, sender = {}, {} ={}".format(sender.row(), sender.column(), sender.data(Qt.EditRole)))
        val = sender.data(Qt.EditRole)
        col = self._ds_columns[sender.column()]
        if not val:
            try:
                self._categorical_columns.remove(col)
            except ValueError:
                # modified column was already not a part of categoricals
                pass
        if val:
            if col not in self._categorical_columns:
                self._categorical_columns.append(col)

    def set_plot_generator(self, ds):
        self._plot_generator = PlotGenerator(ds)

    def fill_color_by(self):
        self._hist_color_by.clear()
        self._hist_color_by.addItem("")
        self._hist_color_by.setCurrentIndex(0)
        self._hist_color_by.addItems(self._categorical_columns)
# plot_window = PlotWindow(self)
#         hist1 = plot_window.figure.add_subplot(111)
#         hist1.hist([2, 23, 4, 5, 6, 6, 6, 4, 3, 3, 2, 1])
#         self._plot_layout.addWidget(plot_window)