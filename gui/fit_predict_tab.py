from PyQt5.QtWidgets import QWidget, QCheckBox, QGridLayout, QLabel,  QGroupBox, QPushButton, \
    QListWidget, QAbstractItemView,  QDoubleSpinBox,  QTabWidget, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

import pandas as pd

from gui.dynamic_combobox import DynamicComboBox
from gui.ml_options.KNeighbors_options import KNeighborsOptions
from gui.ml_options.SV_options import SVOptions
from gui.gui_helper import GuiHelper
from gui.list_widget import ListWidget

from ml_choices import Scalers, MLClassification, MLRegression, MLWidgets, ml_2_widget_number, ml_2_widget_name
from ml_expert import MLExpert
from ml_plotter import MLPlotter


class FitPredictTab(QWidget):
    request_plot_generation = pyqtSignal(QWidget, str)
    grid_computed = pyqtSignal(object, pd.DataFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FitPredictDock")
        self.setWindowTitle("Grid Search")

        # this dict will store ml parameters
        # and restore them as needed (instead of generating duplicates
        self._param_widgets = {}
        self._ml_expert = None
        self._ml_plotter = MLPlotter()
        self._ds_columns = []
        self._ds = None
        self._grid = None


        # data selection
        self._data_feature_lb = QLabel("Select Features")
        self._data_feature_list = QListWidget()
        self._data_feature_list.setToolTip("At least 1 feature needed for running estimator")
        self._data_feature_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._data_target_lb = QLabel("Select Target")
        self._data_target_combo = DynamicComboBox()
        self._data_target_combo.setToolTip("One column must be selected as target for running estimator")
        self._data_target_combo.popup_clicked.connect(self.fill_target_combo)
        self._data_target_combo.currentTextChanged.connect(self.fill_estimator_list)
        self._data_layout = QGridLayout()

        self._data_layout.addWidget(self._data_feature_lb, 0, 0)
        self._data_layout.addWidget(self._data_feature_list, 1, 0)
        self._data_layout.addWidget(self._data_target_lb, 0, 1)
        self._data_layout.addWidget(self._data_target_combo, 1, 1)

        self._data_gb = QGroupBox("Data Selection")
        self._data_gb.setLayout(self._data_layout)
        self._data_layout.setAlignment(Qt.AlignTop)

        # scaling
        self._scaling_select_lb = QLabel("Select Scaler")
        self._scaling_select_list = QListWidget()
        self._scaling_select_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._scaling_select_list.addItem("None")
        self._scaling_select_list.addItems(Scalers.all_names())
        self._grid_layout = QGridLayout()
        self._grid_layout.addWidget(self._scaling_select_lb, 0, 0)
        self._grid_layout.addWidget(self._scaling_select_list, 1, 0)

        #estimator
        self._estimator_select_lb = QLabel("Select Estimator")
        self._estimator_select_list = ListWidget()
        self._estimator_select_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._estimator_select_list.setToolTip("An estimator must be selected to run")
        self._estimator_select_list.mouse_up.connect(self._populate_ml_parameters)

        self._grid_layout.addWidget(self._estimator_select_lb, 0, 1)
        self._grid_layout.addWidget(self._estimator_select_list, 1, 1)

        self._grid_gb = QGroupBox("Grid Search")
        self._grid_gb.setLayout(self._grid_layout)
        self._grid_layout.setAlignment(Qt.AlignTop)

        self._estimator_widgets = {}
        self._estimator_tabs = QTabWidget()

        self._estimator_widgets[MLWidgets.KNeighbors.name] = KNeighborsOptions()
        self._estimator_tabs.addTab(self._estimator_widgets[MLWidgets.KNeighbors.name],
                                    self._estimator_widgets[MLWidgets.KNeighbors.name].windowTitle())
        self._estimator_widgets[MLWidgets.SV.name] = SVOptions()
        self._estimator_tabs.addTab(self._estimator_widgets[MLWidgets.SV.name],
                                    self._estimator_widgets[MLWidgets.SV.name].windowTitle())
        self._grid_layout.addWidget(self._estimator_tabs, 2, 0, 1, 2)

        #p arameters
        self._param_split_lb = QLabel("Test/Train Split Ratio")
        self._param_split_sp = QDoubleSpinBox()
        #TODO: think about use of this, either remove or use
        self._param_split_sp.setRange(0, 1)
        self._param_split_sp.setValue(0)
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
        self._display_table_btn = QPushButton("Show results table")
        self._display_table_btn.clicked.connect(self._display_table)
        self._display_summary_plot_btn = QPushButton("Show summary plot")
        self._display_summary_plot_btn.clicked.connect(self._display_summary_plot)
        self._display_parameter_plots_btn = QPushButton("Show parameter plots")
        self._display_parameter_plots_btn.clicked.connect(self._display_parameter_plots)

        self.buttons_hbox = QHBoxLayout()
        self.buttons_hbox.addWidget(self._run_btn)
        self.buttons_hbox.addWidget(self._display_table_btn)
        self.buttons_hbox.addWidget(self._display_summary_plot_btn)
        self.buttons_hbox.addWidget(self._display_parameter_plots_btn)
        self._enable_display_buttons(False)
        # layout for the whole tab
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignTop)

        self._layout.addWidget(self._data_gb, 0, 0)
        self._layout.addWidget(self._grid_gb, 1, 0)
        self._layout.addLayout(self.buttons_hbox, 2, 0)
        
        self._layout.setAlignment(Qt.AlignTop)
        self.setLayout(self._layout)

    def _enable_display_buttons(self, a):
        for i in range(1, self.buttons_hbox.count()):
            widget = self.buttons_hbox.itemAt(i).widget()
            widget.setEnabled(a)

    def _display_summary_plot(self):
        if not self._grid:
            return
        graph = self._ml_plotter.plot_grid_results_summary_graph(self._grid)
        self.request_plot_generation.emit(graph, "summary plot")
        return

    def _display_parameter_plots(self):
        if not self._grid:
            return
        graph2 = self._ml_plotter.plot_grid_results_graph(self._grid)
        self.request_plot_generation.emit(graph2, "parameter plot")
        return

    def _display_table(self):
        if not self._grid:
            return
        tbl = self._ml_plotter.plot_grid_results_table(self._grid)
        self.request_plot_generation.emit(tbl, "grid results")
        return

    def _validate_features(self):
        feature_columns = []
        for item in self._data_feature_list.selectedItems():
            feature_columns.append(item.text())
        if not feature_columns:
            GuiHelper.point_to_error(self._data_feature_list)
            return None
        for col in feature_columns:
            if col not in self._ds_columns:
                raise KeyError('selected column ({}) name not in dataframe'.format(col))
        return feature_columns

    def _validate_target(self):
        target = self._data_target_combo.currentText()
        if target == '':
            GuiHelper.point_to_error(self._data_target_combo)
            return None
        if target not in self._ds_columns:
            raise KeyError('selected column ({}) name not in dataframe'.format(target))
        return target

    def _validate_scaler(self):
        scaler = []
        for item in self._scaling_select_list.selectedItems():
            scaler.append(item.text())
        if not scaler:
            scaler.append("None")
        return scaler

    def _validate_ml(self):
        ml = []
        for item in self._estimator_select_list.selectedItems():
            ml.append(item.text())

        if not ml:
            GuiHelper.point_to_error(self._estimator_select_list)
            return None
        return ml

    def _validate_parameters(self, ml):
        parameters = {}
        for algo_name in ml:
            widget_name = ml_2_widget_name(algo_name)
            param = self._estimator_widgets[widget_name].gather_parameters()
            if not param:
                # set to current widget to problematic one
                # so that the widgets validate function can show issue to user
                self._estimator_tabs.setCurrentWidget(self._estimator_widgets[widget_name])
                return None
            parameters[algo_name] = param
        return parameters

    def _run(self):
        # check columns
        feature_columns = self._validate_features()
        if not feature_columns:
            return
        target_column = self._validate_target()
        if not target_column:
            return
        ml = self._validate_ml()
        if not ml:
            return
        test_ratio = self._param_split_sp.value()

        scalers = self._validate_scaler()
        parameters = self._validate_parameters(ml)
        if parameters is None:
            return

        # do the run
        categorical = target_column in self._ds.categorical_columns
        grid, df = self._ml_expert.big_loop(feature_columns, target_column, test_ratio, scalers, parameters, categorical)

        # update self
        self._grid = grid
        self._enable_display_buttons(True)
        self.grid_computed.emit(grid, df)
        # generate results
        self._display_table()
        self._display_summary_plot()
        self._display_parameter_plots()

    def _populate_ml_parameters(self):
        selected_widget_nos = []
        for item in self._estimator_select_list.selectedItems():
            try:
                selected_widget_nos.append(ml_2_widget_number(item.text()))
            except KeyError:
                return

        for no in range(self._estimator_tabs.count()):
            if no in selected_widget_nos:
                self._estimator_tabs.setTabEnabled(no, True)
            else:
                self._estimator_tabs.setTabEnabled(no, False)

    def fill_estimator_list(self):
        self._estimator_select_list.clear()
        if self._data_target_combo.currentText() == '':
            self._estimator_select_list.addItem("Target must be selected")
        elif self._data_target_combo.currentText() in self._ds.categorical_columns:
            self._estimator_select_list.addItems(MLClassification.all_names())
        else:
            self._estimator_select_list.addItems(MLRegression.all_names())

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
        self._ml_expert = MLExpert(self._ds)
        self._ds_columns = self._ds.column_names()
        self._data_feature_list.clear()
        self._data_target_combo.clear()
        self._data_target_combo.addItem("")
        self._data_target_combo.setCurrentIndex(0)
        self._data_feature_list.addItems(self._ds.numerical_columns)

    def update_upon_closing_dataset(self):
        self.setDisabled(True)
        self._ds_columns = []
        self._grid = None
        self._enable_display_buttons(False)


