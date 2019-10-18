from PyQt5.QtWidgets import QWidget, QCheckBox, QGridLayout, QLabel, QComboBox, QGroupBox, QPushButton, QVBoxLayout,\
    QListWidget, QAbstractItemView, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QSizePolicy



from gui.table_widget import TableWidgetState, TableWidget
from gui.plot_window import PlotWindow
from gui.dynamic_combobox import DynamicComboBox
from plot_generator import PlotGenerator


class DataAnalysisTabMulti(QWidget):
    request_plot_generation = pyqtSignal(QWidget, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DataAnalysisDockMulti")
        self.setWindowTitle("MultiVariate Analysis")

        self._ds_name = ""
        self._ds = None
        self._ds_columns = []
        self._current_table_widget = None
        self._current_dataset = None
        self._categorical_df = None
        self._categorical_columns = []
        self._plot_generator = None



        # correlation matrix
        self.correlation_btn = QPushButton("Calculate Correlation")
        self.sort_by_lb = QLabel("Sort By:")
        self.sort_by = DynamicComboBox()
        self.sort_by.popup_clicked.connect(self.fill_combobox)

        self._corr_layout = QGridLayout()
        self._corr_layout.addWidget(self.correlation_btn, 0, 0, 1, 2)
        self._corr_layout.addWidget(self.sort_by_lb, 1, 0)
        self._corr_layout.addWidget(self.sort_by, 1, 1)
        self._corr_gb = QGroupBox("Correlation")
        self._corr_gb.setLayout(self._corr_layout)
        self._corr_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # 2d histograms
        self._hist_X = QListWidget()
        self._hist_X.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._hist_Y = QListWidget()
        self._hist_Y.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._hist_btn = QPushButton("Create hist2d")
        self._hist_xplot_btn = QPushButton("Create cross plot")
        self._hist_x_lb = QLabel("X:")
        self._hist_y_lb = QLabel("Y:")
        self._hist_layout = QGridLayout()
        self._hist_layout.addWidget(self._hist_x_lb, 0, 0)
        self._hist_layout.addWidget(self._hist_y_lb, 0, 1)
        self._hist_layout.addWidget(self._hist_X, 1, 0)
        self._hist_layout.addWidget(self._hist_Y, 1, 1)
        self._hist_layout.addWidget(self._hist_btn, 2, 0)
        self._hist_layout.addWidget(self._hist_xplot_btn, 2, 1)

        self._hist_gb = QGroupBox("2D Histograms / XPlots")
        self._hist_gb.setLayout(self._hist_layout)
        self._hist_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # layout for the whole tab
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignTop)

        self._layout.addWidget(self._corr_gb, 0, 0)
        self._layout.addWidget(self._hist_gb, 1, 0)
        self.setLayout(self._layout)

        # signal slot connections
        self.correlation_btn.clicked.connect(self.correlation_matrix)
        self._hist_btn.clicked.connect(self.hist2d)
        self._hist_xplot_btn.clicked.connect(self.xplot)

    def dataset_opened(self, ds, _):
        self.set_plot_generator(ds)
        self._ds_name = ds.name
        self._ds = ds
        self._ds_columns = ds.column_names()
        self.sort_by.clear()
        self.sort_by.addItem("")
        self.sort_by.setCurrentIndex(0)
        self._hist_X.clear()
        self._hist_X.addItems(ds.column_names())
        self._hist_Y.clear()
        self._hist_Y.addItems(ds.column_names())

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
        self.sort_by.clear()
        self._hist_X.clear()
        self._hist_Y.clear()
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
        self.sort_by.clear()
        self.sort_by.addItem("")
        self.sort_by.setCurrentIndex(0)
        self._hist_data.addItems(self._ds_columns)
        self._hist_data.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self._hist_data.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.sort_by.addItems(self._ds_columns)
        self._hist_plot.setDisabled(False)

    def correlation_matrix(self):
        sort_key = self.sort_by.currentText()
        window = self._plot_generator.correlation_matrix(sort_key)
        self.request_plot_generation.emit(window, "Correlation Window")

    def hist2d(self):
        x_props = self._hist_X.selectedItems()
        y_props = self._hist_Y.selectedItems()
        window = self._plot_generator.generate_hist2d(x_props, y_props)
        self.request_plot_generation.emit(window, "Hist2d Window")

    def xplot(self):
        x_props = self._hist_X.selectedItems()
        y_props = self._hist_Y.selectedItems()
        window = self._plot_generator.generate_xplot(x_props, y_props)
        self.request_plot_generation.emit(window, "XPlot Window")

    def set_plot_generator(self, ds):
        self._plot_generator = PlotGenerator(ds)

    def fill_combobox(self):
        combobox = self.sender()
        combobox.clear()
        combobox.addItem("")
        combobox.setCurrentIndex(0)
        combobox.addItems(self._ds.column_names())

# plot_window = PlotWindow(self)
#         hist1 = plot_window.figure.add_subplot(111)
#         hist1.hist([2, 23, 4, 5, 6, 6, 6, 4, 3, 3, 2, 1])
#         self._plot_layout.addWidget(plot_window)