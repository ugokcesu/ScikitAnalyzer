#import warnings

from PyQt5.QtWidgets import QWidget, QCheckBox, QGridLayout, QLabel, QComboBox, QGroupBox, QPushButton, QVBoxLayout,\
    QListWidget, QAbstractItemView, QSpinBox, QDoubleSpinBox, QToolTip
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.Qt import QSizePolicy

from gui.table_widget import TableWidgetState, TableWidget
from gui.dynamic_combobox import DynamicComboBox
from gui.ml_options.KNeighbors_options import KNeighborsOptions
from gui.ml_options.SV_options import SVOptions
from gui.gui_helper import GuiHelper
from plot_generator import PlotGenerator

from ml_choices import Scalers, MLClassification, MLRegression, MLWidgets, ml_2_widgets
from ml_expert import MLExpert
from ml_plotter import MLPlotter


class FitPredictTab(QWidget):
    request_plot_generation = pyqtSignal(QWidget, str)
    info_calculated = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FitPredictDock")
        self.setWindowTitle("Grid Search")

        # this dict will store ml parameters
        # and restore them as needed (instead of generating duplicates
        self._param_widgets = {}
        self._plot_generator = None
        self._ml_expert = None
        self._ml_plotter = MLPlotter()
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
        self._data_feature_list.setToolTip("At least 1 feature needed for running estimator")
        self._data_feature_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._data_target_lb = QLabel("Select Target")
        self._data_target_combo = DynamicComboBox()
        self._data_target_combo.setToolTip("One column must be selected as target for running estimator")

        self._data_layout = QGridLayout()

        self._data_layout.addWidget(self._data_feature_lb, 0, 0)
        self._data_layout.addWidget(self._data_feature_list, 1, 0)
        self._data_layout.addWidget(self._data_target_lb, 0, 1)
        self._data_layout.addWidget(self._data_target_combo, 1, 1)
        self._data_target_combo.popup_clicked.connect(self.fill_target_combo)

        self._data_gb = QGroupBox("Data Selection")
        self._data_gb.setLayout(self._data_layout)
        self._data_layout.setAlignment(Qt.AlignTop)

        # scaling
        self._scaling_select_lb = QLabel("Select Scaler")
        self._scaling_select_combo = DynamicComboBox()
        self._scaling_select_combo.addItem("None")
        self._scaling_select_combo.addItems(Scalers.all_values())
        self._scaling_select_combo.setCurrentIndex(0)
        self._scaling_layout = QGridLayout()
        self._scaling_layout.addWidget(self._scaling_select_lb, 0, 0)
        self._scaling_layout.addWidget(self._scaling_select_combo, 0, 1)

        self._scaling_gb = QGroupBox("Data Scaling")
        self._scaling_gb.setLayout(self._scaling_layout)

        #predict
        self._predict_select_lb = QLabel("Select Estimator")
        self._predict_select_combo = DynamicComboBox()
        self._predict_select_combo.setToolTip("An estimator must be selected to run")
        self._predict_select_combo.popup_clicked.connect(self.fill_predict_combo)
        self._predict_select_combo.currentTextChanged.connect(self._populate_ml_parameters)

        self._predict_layout = QGridLayout()
        self._predict_layout.addWidget(self._predict_select_lb, 0, 0)
        self._predict_layout.addWidget(self._predict_select_combo, 0, 1)
        self._predict_layout.setAlignment(Qt.AlignTop)

        self._predict_gb = QGroupBox("Estimator")
        self._predict_gb.setLayout(self._predict_layout)

        #parameters
        self._param_split_lb = QLabel("Test/Train Split Ratio")
        self._param_split_sp = QDoubleSpinBox()
        self._param_split_sp.setRange(0, 0.99)
        self._param_split_sp.setValue(0.25)
        self._param_gscv_lb = QLabel("Enable GridSearchCV")
        self._param_gscv_cb = QCheckBox()
        self._param_gscv_cb.setChecked(False)
        self._param_layout = QGridLayout()
        self._param_layout.addWidget(self._param_split_lb, 0, 0)
        self._param_layout.addWidget(self._param_split_sp, 0, 1)
        self._param_layout.addWidget(self._param_gscv_lb, 1, 0)
        self._param_layout.addWidget(self._param_gscv_cb, 1, 1)
        self._param_last_row = 2
        self._param_gb = QGroupBox("Estimator Parameters")
        self._param_gb.setLayout(self._param_layout)

        self._run_btn = QPushButton("Run")
        self._run_btn.clicked.connect(self._run)
        # layout for the whole tab
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignTop)

        self._layout.addWidget(self._data_gb, 0, 0)
        self._layout.addWidget(self._scaling_gb, 1, 0)
        self._layout.addWidget(self._predict_gb, 2, 0)
        self._layout.addWidget(self._param_gb, 3, 0)
        self._layout.addWidget(self._run_btn, 4, 0)
        self._layout.setAlignment(Qt.AlignTop)
        self.setLayout(self._layout)

        # signal slot connections
    def _run(self):
        # check columns
        if not self._data_feature_list.selectedItems():
            GuiHelper.point_to_error(self._data_feature_list)
            return
        if self._data_target_combo.currentText() == '':
            GuiHelper.point_to_error(self._data_target_combo)
            return
        feature_columns = []
        for item in self._data_feature_list.selectedItems():
            feature_columns.append(item.text())
        target_column = self._data_target_combo.currentText()

        for selected_col in feature_columns + [target_column]:
            if selected_col not in self._ds_columns:
                raise KeyError

        scaler = self._scaling_select_combo.currentText()

        ml = self._predict_select_combo.currentText()

        if ml not in MLClassification.all_values() + MLRegression.all_values():
            GuiHelper.point_to_error(self._predict_select_combo)
            return

        test_ratio = self._param_split_sp.value()

        use_grid_search = self._param_gscv_cb.isChecked()

        if ml_2_widgets(ml) not in self._param_widgets.keys():
            return
        parameters = self._param_widgets[ml_2_widgets(ml)].gather_parameters()
        if parameters is None:
            return

        X_train, X_test, y_train, y_test = self._ml_expert.data_splitter(ml, test_ratio, feature_columns, target_column)
        pipeline = self._ml_expert.assemble_pipeline(scaler, ml)
        grid = self._ml_expert.fit_grid(ml, pipeline, parameters, X_train, y_train)
        window = self._ml_plotter.plot_grid_results(grid, X_test, y_test)
        self.request_plot_generation.emit(window, "GridSearch Results")

    def _populate_ml_parameters(self):
        selected_ml = self._predict_select_combo.currentText()
        item = self._param_layout.itemAtPosition(self._param_last_row, 0)
        if item is not None:
            self._param_layout.removeItem(item)
            item.widget().hide()

        if selected_ml == MLRegression.KNeighborsRegressor.name or selected_ml == MLClassification.KNeighborsClassifier.name:
            if MLWidgets.KNeighbors in self._param_widgets.keys():
                self._param_layout.addWidget(self._param_widgets[MLWidgets.KNeighbors], self._param_last_row, 0, 1, 2)
                self._param_widgets[MLWidgets.KNeighbors].show()

            else:
                self._param_widgets[MLWidgets.KNeighbors] = KNeighborsOptions()
                self._param_layout.addWidget(self._param_widgets[MLWidgets.KNeighbors], self._param_last_row, 0, 1, 2)
        elif selected_ml == MLRegression.SVR.name or selected_ml == MLClassification.SVC.name:
            if MLWidgets.SV in self._param_widgets.keys():
                self._param_layout.addWidget(self._param_widgets[MLWidgets.SV], self._param_last_row, 0, 1, 2)
                self._param_widgets[MLWidgets.SV].show()

            else:
                self._param_widgets[MLWidgets.SV] = SVOptions()
                self._param_layout.addWidget(self._param_widgets[MLWidgets.SV], self._param_last_row, 0, 1, 2)
        else:
            self._param_layout.addWidget(QLabel("Oops"), self._param_last_row, 0, 1, 2)

    def fill_predict_combo(self):
        self._predict_select_combo.clear()
        if self._data_target_combo.currentText() == '':
            self._predict_select_combo.addItem("Target must be selected")
        elif self._data_target_combo.currentText() in self._ds.categorical_columns:
            self._predict_select_combo.addItems(MLClassification.all_values())
        else:
            self._predict_select_combo.addItems(MLRegression.all_values())
        self._predict_select_combo.setCurrentIndex(0)

    def fill_target_combo(self):
        self._data_target_combo.clear()
        item_count = self._data_feature_list.count()
        for i in range(item_count):
            item = self._data_feature_list.item(i)
            if not item.isSelected():
                self._data_target_combo.addItem(item.text())

    def dataset_opened(self, ds=None, _=None):
        if ds:
            self._ds = ds
        if not self._ds:
            raise TypeError
        self.set_plot_generator(self._ds)
        self._ml_expert = MLExpert(self._ds)
        self._ds_name = self._ds.name
        self._ds_columns = self._ds.column_names()
        self._data_feature_list.clear()
        self._data_target_combo.clear()
        self._data_target_combo.addItem("")
        self._data_target_combo.setCurrentIndex(0)
        self._data_feature_list.addItems(self._ds_columns)

    def set_plot_generator(self, ds):
        self._plot_generator = PlotGenerator(ds)

    # connect to dataLoader tab's close_ds method
    def update_upon_closing_dataset(self):
        self.setDisabled(True)
        self._ds_columns = []
        self._categorical_columns = []

