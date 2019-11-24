import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from PyQt5.QtWidgets import QTableView, QWidget, QVBoxLayout, QGridLayout, QScrollArea, QSizePolicy, QSplitter, QLabel,\
    QSpacerItem
from PyQt5.QtCore import Qt


from dataset_model import DatasetModel
from color_by_val_model import ColorByValModel
from uncertainty_table_model import UncertaintyTableModel
from gui.plot_window import PlotWindow


class MLPlotter:
    # each scaler will have different marker
    markers = ['.', 'd', 'x', 'v', '*', 's']
    # each estimator method will have different color
    colors = ['red', 'blue', 'green', 'yellow']

    @staticmethod
    def plot_grid_results_table(grid):
        df = pd.DataFrame(grid.cv_results_)

        # filter some columns
        df = df.loc[:, ~(df.columns.str.contains("time|split"))]
        model = DatasetModel(dataFrame=df)
        grid_results = QTableView()
        grid_results.setAlternatingRowColors(True)
        grid_results.setModel(model)
        grid_results.setWindowTitle("Grid Results")
        grid_results.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        return grid_results

    @staticmethod
    def value_added_table(val_added_df):
        val_added_series = val_added_df.mean()
        val_added_df = pd.DataFrame({'Features':val_added_series.index, 'Value Added':val_added_series.values})
        val_added_df.sort_values(inplace=True, by='Value Added')
        model = ColorByValModel(dataFrame=val_added_df)
        table = QTableView()
        table.setModel(model)
        table.setWindowTitle("Value Added Table")
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return table

    @staticmethod
    def plot_df_results_table(df, base, secondary):
        # filter some columns
        df = df.loc[:, ~(df.columns.str.contains("time|split"))]
        model = UncertaintyTableModel(base, secondary, dataFrame=df)
        grid_results = QTableView()
        grid_results.setAlternatingRowColors(True)
        grid_results.setModel(model)
        grid_results.setWindowTitle("Grid Results")
        grid_results.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return grid_results

    @classmethod
    def plot_feat_unc_table(cls, df, scaler, params, base, secondary):
        df = df[['mean_test_score', 'mean_train_score', 'columns']].\
            sort_values(by='mean_test_score').reset_index(drop=True)
        table = cls.plot_df_results_table(df, base, secondary)
        table.horizontalHeader().setStretchLastSection(True)
        window = QWidget()
        layout = QVBoxLayout()
        lb = QLabel("All runs made with scaler= {}, and parameters= {}".format(scaler, params))
        layout.addWidget(lb)
        layout.addWidget(table)
        layout.setAlignment(Qt.AlignTop)
        window.setLayout(layout)
        lb.setFixedHeight(lb.sizeHint().height())
        return window

    @classmethod
    def _extract_best_param_per_estimator(cls, df):
        # we cannot just get rank==1, we need best rank per estimator
        # since all are done in single gridsearch
        estimators = df['estimator'].unique()
        best_per_estimator = df.groupby('estimator_cat')['rank_test_score'].min()

        # best_params' keys will be the different estimators
        # and values will be the dicitonary of parameters that correspond to best run of that estimator
        best_params = {}
        for estimator in estimators:
            best = {}
            best_row = df[df['rank_test_score'] == best_per_estimator[estimator]].iloc[0]
            for col in best_row.index:
                if 'param_DummyEstimator__' in col and not np.isnan(best_row[col]):
                    best[col] = best_row[col]
                best['scaler'] = best_row['scaler']
            best_params[estimator] = best
        return best_params

    @classmethod
    def plot_grid_results_graph(cls, grid):
        df = pd.DataFrame(grid.cv_results_)
        # legible names for estimator and scaler
        df['estimator'] = df['param_DummyEstimator'].astype(str).apply(lambda x: x.split('(')[0])
        df['estimator_cat'] = pd.Categorical(df['estimator'])
        df['scaler'] = df['param_DummyScaler'].astype(str).apply(lambda x: x.split('(')[0])

        best_params = cls._extract_best_param_per_estimator(df)
        container_widget = QWidget()
        layout = QGridLayout()
        container_widget.setLayout(layout)
        counter = 0
        for estimator in best_params.keys():
            layout.addWidget(QLabel("Parameter Analysis for " + estimator), counter, 0)
            counter += 1
            plot_window = PlotWindow(height=3 * (len(best_params[estimator])-1))
            i = 0
            for col in best_params[estimator].keys():
                if col == 'scaler':
                    continue
                i += 1
                mask = cls._create_bool_mask(df, col, best_params[estimator])
                ax = plot_window.figure.add_subplot(len(best_params[estimator])-1, 1, i)
                ax.plot(df[mask][col], df[mask].mean_test_score, label=col.split('__')[1]+'_test', linestyle='-',
                        marker='.', color='red', linewidth=1)
                ax.plot(df[mask][col], df[mask].mean_train_score, label=col.split('__')[1]+'_train',  linestyle='--',
                        marker='.', color='blue', linewidth=1)
                ax.legend(loc='best')
                ax.set_xlabel(col)
                ax.set_ylabel('mean test score')
                plt.tight_layout(True, rect=(0.06, 0.06, 0.98, 0.98))
            layout.addWidget(plot_window, counter, 0)
            best_param_lb = QLabel("Best Params for " + estimator + ":\n" +
                                   str(best_params[estimator]).replace(',', '\n').strip('{|}'))
            layout.addWidget(best_param_lb, counter, 1)
            counter +=1
        layout.addItem(QSpacerItem(1, 1), counter, 0, 1, 2)
        layout.setRowStretch(counter, 10)
        layout.setAlignment(Qt.AlignTop | Qt.AlignTop)
        return container_widget

    @staticmethod
    def _create_bool_mask(df, col, best):
        mask = pd.Series([True for i in range(df.shape[0])])
        for key in best.keys():
            if col.split('__')[-1] == key.split('__')[-1]:
                continue
            mask = mask & (df[key] == best[key])
        mask = mask & (df['scaler'] == best['scaler'])
        return mask

    @classmethod
    def plot_grid_results_summary_graph(cls, grid):
        df = pd.DataFrame(grid.cv_results_)

        # legible names for estimator and scaler
        df['estimator'] = df['param_DummyEstimator'].astype(str).apply(lambda x: x.split('(')[0])
        df['scaler'] = df['param_DummyScaler'].astype(str).apply(lambda x: x.split('(')[0])
        df['estimator_cat'] = pd.Categorical(df['estimator'])

        # runs with same est parameters but different scalers will have same ngroup
        cols = df.columns.str.contains("param_DummyEstimator__|estimator")
        cols = list(df.columns[cols])
        df['est_w_param'] = df[cols].astype(str).groupby(cols).ngroup()

        # cmap so we can have different color for each estimator
        cmap = matplotlib.colors.ListedColormap(cls.colors[:len(df['estimator_cat'].cat.categories)])

        plot_window = PlotWindow(height=4, width=9)

        ax = plot_window.figure.add_subplot(1, 1, 1)

        lines = []
        labels = []
        for i, scaler in enumerate(df.scaler.unique()):
            esti = df[df['scaler'] == scaler]['estimator_cat']
            line = ax.scatter(df[df['scaler'] == scaler]['est_w_param'], df[df['scaler'] == scaler]['mean_test_score'],
                              label=scaler, marker=cls.markers[i], c=list(esti.cat.codes), cmap=cmap);
            lines.append(line)
            labels.append(scaler)

        # legend gymnastics in order to include marker and color patches in the legend
        for i in range(len(df['estimator_cat'].cat.categories)):
            p = mpatches.Patch(color=cls.colors[i], label=df['estimator_cat'].cat.categories[i])
            lines.append(p)
            labels.append(df['estimator_cat'].cat.categories[i])

        ax.set_xlabel('runs \n(each run has constant estimator+parameters)')
        ax.set_ylabel('mean testing score')
        minor_ticks = np.arange(0, df['est_w_param'].max())
        ax.set_xticks(minor_ticks, minor=True)
        ax.xaxis.grid(which='minor', alpha=0.5)


        ax.set_title('GridSearchCv Summary Plot')
        ax.legend(tuple(lines), tuple(labels), loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout(True, rect=(0.06, 0.06, 0.98, 0.98))
        container_widget = QWidget()
        layout = QVBoxLayout()
        container_widget.setLayout(layout)
        layout.addWidget(plot_window, 0)
        layout.addSpacerItem(QSpacerItem(1, 1))
        layout.setStretch(1, 10)
        return container_widget

    def plot_grid_results(self, grid, X_test, y_test):
        score = grid.score(X_test, y_test)
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_widget.setLayout(container_layout)
        super_container = QWidget()
        super_scroll = QScrollArea()
        super_layout = QGridLayout()
        super_layout.addWidget(super_scroll, 0, 0)
        super_container.setLayout(super_layout)

        table = self.plot_grid_results_table(grid)
        graph = self.plot_grid_results_graph(grid)
        table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        graph.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        container_layout.addWidget(table, stretch=5)
        container_layout.addWidget(QLabel("Testing Score of best estimator (w/ data that was excluded for grid search): {:.3f}".format(score)))
        container_layout.addWidget(graph, stretch=5)
        super_scroll.setWidget(container_widget)
        super_scroll.setWidgetResizable(True)
        return super_container







