from copy import deepcopy
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QWidget, QCheckBox, QGridLayout, QLabel,  QGroupBox, QPushButton, \
    QListWidget, QAbstractItemView,  QDoubleSpinBox,  QTabWidget, QHBoxLayout, QRadioButton, QButtonGroup, QSpinBox,\
    QVBoxLayout
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtCore


from gui.dynamic_combobox import DynamicComboBox
from gui.ml_options.KNeighbors_options import KNeighborsOptions
from gui.ml_options.SV_options import SVOptions
from gui.gui_helper import GuiHelper
from gui.list_widget import ListWidget

from scikit_logger import ScikitLogger

from ml_choices import Scalers, MLClassification, MLRegression, MLWidgets, ml_2_widget_number, ml_2_widget_name
from ml_expert import MLExpert
from ml_plotter import MLPlotter


class FeatureAnalysisTab(QWidget):
    request_plot_generation = pyqtSignal(QWidget, str)
    logger = ScikitLogger()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FeatureAnalyseDock")
        self.setWindowTitle("Feature Analysis")

        # this dict will store ml parameters
        # and restore them as needed (instead of generating duplicates
        self._param_widgets = {}
        self._ml_expert = None
        self._ml_plotter = MLPlotter()
        self._ds_columns = []
        self._ds = None
        self._grid = None
        self._df = None

        # data selection
        self._data_info_lb = QLabel("")
        self._data_feature_lb = QLabel("Select Base Features")
        self._data_feature_list = QListWidget()
        self._data_feature_list.setToolTip("These features will be included in all runs")
        self._data_feature_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._data_feature_list.itemSelectionChanged.connect(self.feature_updated)
        self._data_feature2_lb = QLabel("Select Secondary")
        self._data_feature2_list = QListWidget()
        self._data_feature2_list.setToolTip("These features will be added to base features\n"
                                            " by combining them using a full factorial approach\n")
        self._data_feature2_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._data_feature2_list.itemSelectionChanged.connect(self.feature_updated)

        # sync scollbar of feature lists
        self._data_feature_list.verticalScrollBar().valueChanged.connect(
            self._data_feature2_list.verticalScrollBar().setValue)
        self._data_feature2_list.verticalScrollBar().valueChanged.connect(
            self._data_feature_list.verticalScrollBar().setValue)

        self._data_target_lb = QLabel("Select Target")
        self._data_target_combo = DynamicComboBox()
        self._data_target_combo.setToolTip("One column must be selected as target for running estimator")
        self._data_target_combo.popup_clicked.connect(self.fill_target_combo)
        self._data_target_combo.currentTextChanged.connect(self.fill_estimator_list)
        self._data_layout = QGridLayout()

        self._data_layout.addWidget(self._data_info_lb, 0, 0, 1, 2)
        self._data_layout.addWidget(self._data_feature_lb, 1, 0)
        self._data_layout.addWidget(self._data_feature_list, 2, 0)
        self._data_layout.addWidget(self._data_feature2_lb, 1, 1)
        self._data_layout.addWidget(self._data_feature2_list, 2, 1)
        self._data_layout.addWidget(self._data_target_lb, 1, 2)
        self._data_layout.addWidget(self._data_target_combo, 2, 2)
        self._data_layout.setRowStretch(2, 10)

        self._data_gb = QGroupBox("Data Selection")
        self._data_gb.setLayout(self._data_layout)
        self._data_layout.setAlignment(Qt.AlignTop)

        # model selection choice
        self._choice_grid_rb = QRadioButton("Select grid results")
        self._choice_run_no_rb = QRadioButton("Enter grid result run #")
        self._choice_manual_rb = QRadioButton("Manual entry")
        self._button_group = QButtonGroup()
        self._button_group.addButton(self._choice_grid_rb, 0)
        self._button_group.addButton(self._choice_run_no_rb, 1)
        self._button_group.addButton(self._choice_manual_rb, 2)
        self._button_group.buttonClicked[int].connect(self._handle_radio_click)
        self._choice_grid_combo = DynamicComboBox()
        self._choice_run_no_sb = QSpinBox()
        self._choice_layout = QGridLayout()
        self._choice_layout.addWidget(self._choice_grid_rb, 0, 0)
        self._choice_layout.addWidget(self._choice_grid_combo, 0, 1)
        self._choice_layout.addWidget(self._choice_run_no_rb, 1, 0)
        self._choice_layout.addWidget(self._choice_run_no_sb, 1, 1)
        self._choice_layout.addWidget(self._choice_manual_rb, 2, 0)
        self._choice_box = QGroupBox("Initialize Model Using")
        self._choice_box.setLayout(self._choice_layout)

        # scaling
        self._scaling_select_lb = QLabel("Select Scaler")
        self._scaling_select_list = QListWidget()
        self._scaling_select_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._scaling_select_list.addItem("None")
        self._scaling_select_list.addItems(Scalers.all_names())
        self._grid_layout = QGridLayout()
        self._grid_layout.addWidget(self._scaling_select_lb, 0, 0)
        self._grid_layout.addWidget(self._scaling_select_list, 1, 0)

        #estimator
        self._estimator_select_lb = QLabel("Select Estimator")
        self._estimator_select_list = ListWidget()
        self._estimator_select_list.setSelectionMode(QAbstractItemView.SingleSelection)
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

        #parameters
        self._param_split_lb = QLabel("Test/Train Split Ratio")
        self._param_split_sp = QDoubleSpinBox()
        # TODO: think about use of this, either remove or use
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
        self._layout.addWidget(self._choice_box, 1, 0)
        self._layout.addWidget(self._grid_gb, 2, 0)
        self._layout.addLayout(self.buttons_hbox, 3, 0)

        self._layout.setRowStretch(0, 10)
        self._layout.setRowStretch(1, 1)
        self._layout.setRowStretch(2, 1)
        self._layout.setRowStretch(3, 1)
        self._layout.setAlignment(Qt.AlignTop)
        self.setLayout(self._layout)

        # initialize radio buttons
        self._grid_choices_set_enabled(False)
        self._choice_manual_rb.click()

    def feature_updated(self):
        if self.sender() is self._data_feature_list:
            list1 = self._data_feature_list
            list2 = self._data_feature2_list
        else:
            list1 = self._data_feature2_list
            list2 = self._data_feature_list
        selected = []
        for item in list1.selectedItems():
            selected.append(item.text())
        selected2 = []
        for item in list2.selectedItems():
            selected2.append(item.text())
            if item.text() in selected:
                item.setSelected(False)

        if self._data_target_combo.currentText() in selected + selected2:
            self._data_target_combo.clear()

        self.update_info_label()

    def update_info_label(self):
        nb = len(self._data_feature2_list.selectedItems())
        if nb == 0:
            self._data_info_lb.setText("No secondary features selected")
        else:
            self._data_info_lb.setText("{} secondary features selected = {} runs".format(nb, 2**nb - 1))

    def _handle_radio_click(self, btn_id):
        if btn_id == 0:
            self._choice_grid_combo.setEnabled(True)
            self._choice_run_no_sb.setEnabled(False)
            self._grid_gb.setEnabled(False)
        if btn_id == 1:
            self._choice_grid_combo.setEnabled(False)
            self._choice_run_no_sb.setEnabled(True)
            self._grid_gb.setEnabled(False)
        elif btn_id == 2:
            self._choice_grid_combo.setEnabled(False)
            self._choice_run_no_sb.setEnabled(False)
            self._grid_gb.setEnabled(True)

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
        # allow to be None
        # if not feature_columns:
        #    GuiHelper.point_to_error(self._data_feature_list)
        #    return None
        for col in feature_columns:
            if col not in self._ds_columns:
                raise KeyError('selected column ({}) name not in dataframe'.format(col))
        return feature_columns

    def _validate_features2(self):
        feature_columns = []
        for item in self._data_feature2_list.selectedItems():
            feature_columns.append(item.text())
        if not feature_columns:
        #    GuiHelper.point_to_error(self._data_feature2_list)
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
            # this part is different than fit_predict
            # we need to have only 1 value for each param
            # so, take first
            for key, val in param.items():
                if isinstance(val, list):
                    param[key] = [val[0]]

            parameters[algo_name] = param
        return parameters

    def _run(self):
        # check columns
        # note: it is ok for base feature to be empty
        # intended use is for feature2 to NOT be empty so you can uncertainty analysis
        base_columns = self._validate_features()
        secondary_columns = self._validate_features2()
        if not secondary_columns and not base_columns:
            return
        target_column = self._validate_target()
        if not target_column:
            return
        test_ratio = self._param_split_sp.value()

        if self._button_group.checkedId() == 2:
            ml = self._validate_ml()
            if not ml:
                return
            scalers = self._validate_scaler()
            parameters = self._validate_parameters(ml)
            if parameters is None:
                return

        if self._button_group.checkedId() == -1:
            raise ValueError("Initialize Model Using cannot be unselected")
        run = -1
        if self._button_group.checkedId() == 0:
            run = self._choice_grid_combo.currentData()
            row = self._validate_run_no(run)
            if row is None:
                return

        if self._button_group.checkedId() == 1:
            run = self._choice_run_no_sb.value()
            row = self._validate_run_no(run)
            if row is None:
                return

        # combine secondary features
        feature_run_list = []
        if secondary_columns:
            secondary_combinations = self.full_factorial_combination(secondary_columns, [[]])

        if base_columns and secondary_columns:
            feature_run_list.append(deepcopy(base_columns))
            for item in secondary_combinations:
                feature_run_list.append(deepcopy(base_columns))
                feature_run_list[-1].extend(item)
        elif secondary_columns:
            feature_run_list = secondary_combinations
        elif base_columns:
            feature_run_list = [base_columns]

        #do the run
        categorical = target_column in self._ds.categorical_columns
        if self._button_group.checkedId() == 0 or self._button_group.checkedId() == 1:
            scalers, parameters = self._get_parameters_from_run(row)

        df = self._ml_expert.feature_uncertainty_loop(feature_run_list, target_column, test_ratio, scalers, parameters, categorical)

        # update self
        self._feat_unc_df = df
        # generate results
        window = self._ml_plotter.plot_feat_unc_table(self._feat_unc_df, scalers[0], parameters, base_columns, secondary_columns)
        self.request_plot_generation.emit(window, "Feature Uncertainty Analysis Table")

    def _validate_run_no(self, run_no):
        if self._df is None:
            return None
        try:
            run = self._df.iloc[run_no]
        except KeyError as e:
            self.logger.error(e)
            return None
        return run

    def full_factorial_combination(self, columns, result=[[]]):
        temp_result = []
        if len(columns) == 0:
            return result[1:]

        for j in range(len(result)):
            temp_result.append(deepcopy(result[j]))
            temp_result[-1].append(columns[0])

        result.extend(temp_result)
        return self.full_factorial_combination(columns[1:], result)

    def _get_parameters_from_run(self, row):
        params = {}
        ml = str(row['param_DummyEstimator']).split("(")[0]

        scaler = [str(row['param_DummyScaler']).split("(")[0]]
        for name in row.index:
            if ('param_DummyEstimator__' in name) and (not np.isnan(row[name])):
                params[name.replace('param_DummyEstimator__', '')] = [row[name]]
        parameters = {}
        parameters[ml] = params
        return scaler, parameters

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
        not_in_1 = []
        for i in range(item_count):
            item = self._data_feature_list.item(i)
            if not item.isSelected():
                not_in_1.append(item.text())
        item_count = self._data_feature2_list.count()
        for i in range(item_count):
            item = self._data_feature2_list.item(i)
            if not item.isSelected() and (item.text() in not_in_1):
                self._data_target_combo.addItem(item.text())

    def dataset_opened(self, ds=None, _=None):
        if ds:
            self._ds = ds
        if not self._ds:
            raise TypeError
        self._ml_expert = MLExpert(self._ds)
        self._ds_columns = self._ds.column_names()
        self._data_feature_list.clear()
        self._data_feature2_list.clear()
        self._data_target_combo.clear()

        self._data_target_combo.addItem("")
        self._data_target_combo.setCurrentIndex(0)
        self._data_feature_list.addItems(self._ds_columns)
        self._data_feature2_list.addItems(self._ds_columns)

    def update_upon_closing_dataset(self):
        self.setDisabled(True)
        self._ds_columns = []

    # slot, signal comes from fit_predict -> left_dock_ml -> feature_analysis
    def update_grid(self, grid, df):
        self._grid = grid
        self._df = df
        self._grid_choices_set_enabled(True)
        self._choice_run_no_sb.setRange(0, len(grid.cv_results_['mean_test_score'])-1)

        #TODO: maybe do these in ml_expert and store in dataset?
        df = pd.DataFrame(grid.cv_results_)
        # legible names for estimator and scaler
        df['estimator'] = df['param_DummyEstimator'].astype(str).apply(lambda x: x.split('(')[0])
        df['best_rank_per_estimator'] = df.groupby('estimator')['rank_test_score'].transform(min)
        df_bests = df[df.best_rank_per_estimator == df.rank_test_score]
        estimators = df['estimator'].unique()
        self._choice_grid_combo.clear()
        for estimator in estimators:
            best_row = df_bests[df_bests.estimator == estimator].index[0]
            text = "Best {}, row={}, score={:.2f}".format(
                estimator, str(best_row), df.iloc[best_row]['mean_test_score'])
            self._choice_grid_combo.addItem(text, best_row)

    def _grid_choices_set_enabled(self, a):
        self._choice_grid_rb.setEnabled(a)
        self._choice_run_no_rb.setEnabled(a)

