import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from PyQt5.QtWidgets import QTableView, QWidget, QVBoxLayout, QGridLayout, QScrollArea, QSizePolicy, QSplitter, QLabel
from PyQt5.QtCore import Qt


from dataset_model import DatasetModel
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
        df.to_csv("df.csv")
        grid_results = QTableView()
        grid_results.setAlternatingRowColors(True)
        grid_results.setModel(model)
        grid_results.setWindowTitle("Grid Results")
        grid_results.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        return grid_results

    @staticmethod
    def plot_grid_results_graph(grid):
        df = pd.DataFrame(grid.cv_results_)
        params = df.columns[df.columns.str.contains('param_')]
        best = grid.best_params_
        plot_window = PlotWindow(height=3 * len(params))
        for i, col in enumerate(params):
            mask = MLPlotter.create_bool_mask(df, col, best)
            ax = plot_window.figure.add_subplot(len(params), 1, i+1)
            ax.plot(df[mask][col], df[mask].mean_test_score, label=col.split('__')[1]+'_test', linestyle='-', marker='.',color='red', linewidth=1)
            ax.plot(df[mask][col], df[mask].mean_train_score, label=col.split('__')[1]+'_train',  linestyle='--',marker='.', color='blue', linewidth=1)
            ax.legend(loc='best')
        return plot_window

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

        plot_window = PlotWindow(height=6)
        ax = plot_window.figure.add_subplot(1, 1, 1)

        lines = []
        labels = []
        for i, scaler in enumerate(df.scaler.unique()):
            esti = df[df['scaler'] == scaler]['estimator_cat']
            line = ax.scatter(df[df['scaler'] == scaler]['est_w_param'], df[df['scaler'] == scaler]['mean_test_score'],
                              label=scaler, marker=cls.markers[i], c=list(esti.cat.codes), cmap=cmap);
            lines.append(line)
            labels.append(scaler)

        # legend gymnastics
        for i in range(len(df['estimator_cat'].cat.categories)):
            p = mpatches.Patch(color=cls.colors[i], label=df['estimator_cat'].cat.categories[i])
            lines.append(p)
            labels.append(df['estimator_cat'].cat.categories[i])

        ax.set_xlabel('run number (each run has constant estimator+parameters)')
        ax.set_ylabel('mean testing score')
        ax.set_title('GridSearchCv Summary Plot')
        ax.legend(tuple(lines), tuple(labels), loc='upper right', bbox_to_anchor=(1.5, 0.5))

        return plot_window

    @staticmethod
    def create_bool_mask(df, col, best):
        mask = pd.Series([True for i in range(df.shape[0])])
        for key in best.keys():
            if col.split('__')[-1] == key.split('__')[-1]:
                continue
            mask = mask & (df['param_'+key] == best[key])
        return mask

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







