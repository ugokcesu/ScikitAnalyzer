from PyQt5.QtWidgets import QWidget, QCheckBox, QGridLayout, QLabel, QComboBox, QGroupBox, QPushButton, QVBoxLayout,\
    QListWidget, QAbstractItemView, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QSizePolicy

from gui.table_widget import TableWidgetState, TableWidget
from gui.dynamic_combobox import DynamicComboBox
from gui.ml_options.KNeighbors_options import KNeighborsOptions

from plot_generator import PlotGenerator

from ml_choices import Scalers, MLClassification, MLRegression, MLWidgets

class FitPredictTab(QWidget):
    request_plot_generation = pyqtSignal(QWidget, str)
    info_calculated = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FitPredictDock")
        self.setWindowTitle("Machine Learning")

        # this dict will store ml parameters
        # and restore them as needed (instead of generating duplicates
        self._param_widgets = {}

        self._ds_name = ""
        self._ds_columns = []
        self._ds = None
        self._current_table_widget = None
        self._current_dataset = None
        self._categorical_df = None
        self._categorical_columns = []
        self._plot_generator = None

        # data selection
        self._data_feature_lb = QLabel("Select Features")
        self._data_feature_list = QListWidget()
        self._data_feature_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._data_target_lb = QLabel("Select Target")
        self._data_target_combo = DynamicComboBox()

        self._data_layout = QGridLayout()
        self._data_layout.addWidget(self._data_feature_lb, 0, 0)
        self._data_layout.addWidget(self._data_feature_list, 1, 0)
        self._data_layout.addWidget(self._data_target_lb, 0, 1)
        self._data_layout.addWidget(self._data_target_combo, 1, 1)
        self._data_target_combo.popup_clicked.connect(self.fill_target_combo)

        self._data_gb = QGroupBox("Data Selection")
        self._data_gb.setLayout(self._data_layout)

        # scaling
        self._scaling_select_lb = QLabel("Select Scaler")
        self._scaling_select_combo = DynamicComboBox()
        self._scaling_select_combo.addItem("None")
        self._scaling_select_combo.setCurrentIndex(0)
        self._scaling_select_combo.addItems(Scalers.all_values())

        self._scaling_layout = QGridLayout()
        self._scaling_layout.addWidget(self._scaling_select_lb, 0, 0)
        self._scaling_layout.addWidget(self._scaling_select_combo, 0, 1)

        self._scaling_gb = QGroupBox("Data Scaling")
        self._scaling_gb.setLayout(self._scaling_layout)

        #predict
        self._predict_select_lb = QLabel("Select Algorithm")
        self._predict_select_combo = DynamicComboBox()
        self._predict_select_combo.popup_clicked.connect(self.fill_predict_combo)
        self._predict_select_combo.currentTextChanged.connect(self._populate_ml_parameters)

        self._predict_layout = QGridLayout()
        self._predict_layout.addWidget(self._predict_select_lb, 0, 0)
        self._predict_layout.addWidget(self._predict_select_combo, 0, 1)
        self._predict_layout.setAlignment(Qt.AlignTop)

        self._predict_gb = QGroupBox("ML Algorithm")
        self._predict_gb.setLayout(self._predict_layout)

        #parameters
        self._param_gscv_lb = QLabel("Enable GridSearchCV")
        self._param_gscv_cb = QCheckBox()
        self._param_gscv_cb.setChecked(False)
        self._param_layout = QGridLayout()
        self._param_layout.addWidget(self._param_gscv_lb, 0, 0)
        self._param_layout.addWidget(self._param_gscv_cb, 0, 1)

        self._param_gb = QGroupBox("ML Parameters")
        self._param_gb.setLayout(self._param_layout)





        # layout for the whole tab
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignTop)

        self._layout.addWidget(self._data_gb, 0, 0)
        self._layout.addWidget(self._scaling_gb, 1, 0)
        self._layout.addWidget(self._predict_gb, 2, 0)
        self._layout.addWidget(self._param_gb, 3, 0)
        self.setLayout(self._layout)

        # signal slot connections

    def _populate_ml_parameters(self):
        selected_ml = self._predict_select_combo.currentText()
        item = self._param_layout.itemAtPosition(1, 0)
        if item is not None:
            self._param_layout.removeItem(item)
            item.widget().hide()

        if selected_ml == MLRegression.KNeighborsRegressor.name or selected_ml == MLClassification.KNeighborsClassifier.name:
            if MLWidgets.KNeighbors in self._param_widgets.keys():
                self._param_layout.addWidget(self._param_widgets[MLWidgets.KNeighbors], 1, 0, 1, 2)
                self._param_widgets[MLWidgets.KNeighbors].show()

            else:
                self._param_widgets[MLWidgets.KNeighbors] = KNeighborsOptions()
                self._param_layout.addWidget(self._param_widgets[MLWidgets.KNeighbors], 1, 0, 1, 2)
        else:
            self._param_layout.addWidget(QLabel("Oops"), 1, 0, 1, 2)


    def fill_predict_combo(self):
        self._predict_select_combo.clear()
        if self._data_target_combo.currentText()=='':
            self._predict_select_combo.addItem("Target must be selected")
        elif self._data_target_combo.currentText() in self._ds.categorical_columns:
            self._predict_select_combo.addItems(MLClassification.all_values())
        else:
            self._predict_select_combo.addItems(MLRegression.all_values())

    def fill_target_combo(self):
        self._data_target_combo.clear()
        item_count = self._data_feature_list.count()
        for i in range(item_count):
            item = self._data_feature_list.item(i)
            if not item.isSelected():
                self._data_target_combo.addItem(item.text())

    def dataset_opened(self, ds, _):
        self.set_plot_generator(ds)
        self._ds_name = ds.name
        self._ds = ds
        self._ds_columns = ds.column_names()
        self._data_feature_list.clear()
        self._data_target_combo.clear()
        self._data_target_combo.addItem("")
        self._data_target_combo.setCurrentIndex(0)
        self._data_feature_list.addItems(self._ds_columns)

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
        self.info_calculated.emit(self._categorical_columns)

    def table_edited(self, sender):
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
        self._ds.categorical_columns = self._categorical_columns
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