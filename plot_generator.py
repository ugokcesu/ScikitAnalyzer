import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QTableView, QWidget, QGridLayout, QScrollArea, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import QObject

import matplotlib.pyplot as plt
import matplotlib as mpl

from sklearn.preprocessing import MinMaxScaler

from dataset import Dataset
from color_by_val_model import color_map, ColorByValModel
from dataset_model import DatasetModel
from gui.plot_window import PlotWindow
from gui.color_map_window import ColorMapWindow
from gui.hist2d_plot_window import Hist2dPlotWindow
from gui.xplot_window_collection import XPlotWindowCollection


class PlotGenerator(QObject):
    columns_sent = pyqtSignal(str, object)
    data_sent = pyqtSignal(np.ndarray, float, float) # rgb array, min, max
    mask_created_from_xplot = pyqtSignal(str)

    def __init__(self, ds: Dataset):
        super().__init__()
        self.df = ds.df
        self.ds = ds

    def generate_histogram(self, data: list, color_by=""):
        container_widget = QWidget()
        container_layout = QGridLayout()
        container_widget.setLayout(container_layout)
        super_container = QWidget()
        super_scroll = QScrollArea()

        super_layout = QGridLayout()
        super_layout.addWidget(super_scroll, 0, 0)
        super_container.setLayout(super_layout)

        if not hasattr(self.df, color_by):
            for index, item in enumerate(data):
                plot_window = PlotWindow(height=3)
                feature_name = item.data(0)
                hist1 = plot_window.figure.add_subplot(len(data), 1, index+1)
                try:
                    np_bins = np.histogram_bin_edges(self.df[feature_name], bins='auto')
                except TypeError:
                    continue
                hist1.hist(self.df[feature_name], alpha=0.5, bins=np_bins, label=feature_name)
                hist1.set_position([0.1, 0.2, 0.85, 0.75])
                plt.xlabel(feature_name)
                hist1.legend()
                container_layout.addWidget(plot_window, index, 0)
        else:
            unique_names = self.df[color_by].unique()
            for index, item in enumerate(data):
                plot_window = PlotWindow(height=3)
                feature_name = item.data(0)
                hist1 = plot_window.figure.add_subplot(len(data), 1, index + 1)
                np_bins = np.histogram_bin_edges(self.df[feature_name], bins='auto')
                all_data = []
                for name in unique_names:
                    all_data.append(self.df.loc[self.df[color_by] == name, feature_name])
                hist_data = hist1.hist(all_data, stacked=True, bins=np_bins, label=unique_names)
                hist1.set_position([0.1, 0.2, 0.85, 0.75])
                plt.xlabel(feature_name)
                hist1.legend()
                dispersion = self.dispersion(hist_data)
                dispersion_label = "Dispersion % :\n"
                for i, name in enumerate(unique_names):
                    dispersion_label += "{} : {:.2f}%\n".format(name, dispersion[i]*100)
                label = QLabel(dispersion_label)
                container_layout.addWidget(plot_window, index, 0)
                container_layout.addWidget(label, index, 1)
            # for the current feature, work out hist dispersion

        # plot_window.layout.addWidget(plot_window)
        super_scroll.setWidget(container_widget)
        return super_container

    def generate_hist2d(self, x_props, y_props):
        container_widget = QWidget()
        container_layout = QGridLayout()
        container_widget.setLayout(container_layout)
        super_container = QWidget()
        super_scroll = QScrollArea()

        super_layout = QGridLayout()
        super_layout.addWidget(super_scroll, 0, 0)
        super_container.setLayout(super_layout)

        for i, out_prop in enumerate(x_props):
            for j, in_prop in enumerate(y_props):
                plot_window = Hist2dPlotWindow() # PlotWindow()
                ax = plot_window.figure.add_subplot(1, 1, 1)
                h2d = ax.hist2d(self.df[out_prop.data(0)], self.df[in_prop.data(0)])
                ax.set_xlabel(out_prop.data(0))
                ax.set_ylabel(in_prop.data(0))
                plot_window.figure.subplots_adjust(bottom=0.18)
                plot_window.figure.colorbar(h2d[3], ax=ax)
                container_layout.addWidget(plot_window, j, i)
                # this should somehow be automatic
                plot_window.update_slider()
        super_scroll.setWidget(container_widget)
        super_scroll.setWidgetResizable(True)
        return super_container

    # like other plots, generate_xplot, generates the window containing plots
    # unlike other plots, it passes the dataset to the window so later the window updates/redraws its own plots
    # is that ok?
    def generate_xplot(self, x_props, y_props, alpha=1):
        container_widget = QWidget()
        container_layout = QGridLayout()
        container_widget.setLayout(container_layout)
        super_container = QWidget()
        super_scroll = QScrollArea()

        super_layout = QGridLayout()
        super_layout.addWidget(super_scroll, 0, 0)
        super_container.setLayout(super_layout)

        xplot_window_collection = XPlotWindowCollection(self.ds, x_props, y_props)
        xplot_window_collection.mask_created_from_xplot.connect(self.mask_created_from_xplot.emit)
        x_props_str = [x.data(0) for x in x_props]
        y_props_str = [y.data(0) for y in y_props]
        plotted_so_far = []
        for i, out_prop in enumerate(x_props_str):
            for j, in_prop in enumerate(y_props_str):
                if (in_prop, out_prop) in plotted_so_far or out_prop == in_prop:
                    continue
                plot_window = PlotWindow()
                xplot_window_collection.windows[j][i] = plot_window
                ax = plot_window.figure.add_subplot(1, 1, 1)
                xplot_window_collection.axes[j][i] = ax
                xplot_window_collection.props[j][i] = out_prop, in_prop
                xplot = ax.scatter(self.df[out_prop], self.df[in_prop], alpha=alpha, marker='.', c='blue')
                xplot_window_collection.xplots[j][i] = xplot
                ax.set_xlabel(out_prop)
                ax.set_ylabel(in_prop)
                plot_window.figure.subplots_adjust(bottom=0.2)
                container_layout.addWidget(plot_window, j, i)
                plotted_so_far.append((out_prop, in_prop))
        super_scroll.setWidget(container_widget)
        super_scroll.setWidgetResizable(True)
        xplot_window_collection.layout.addWidget(super_container, 0, 0, 1, 5)
        return xplot_window_collection

    def send_data(self, col):
        if col not in self.ds.column_names():
            return
        data = self.df[col]
        scaled = MinMaxScaler(feature_range=(0, 1)).fit_transform(data.values.reshape(-1, 1))
        rgb = color_map(scaled)
        self.data_sent.emit(rgb.reshape(-1, 4), data.min(), data.max())

    @staticmethod
    def dispersion(hist_data):
        cum_data = hist_data[0]
        # compute bin_data which stores nb samples in each bin for each category
        bin_data = []
        for index, array in enumerate(cum_data):
            bin_data.append(np.copy(array))
            if index == 0:
                continue
            for i, item in enumerate(array):
                bin_data[index][i] = (cum_data[index][i] - cum_data[index - 1][i])

        # dispersion will be ratio of bin_data of a category to all categories added for each bin (between 0-1)
        dispersion = [None] * len(cum_data)
        # dispersion = bin_data / added so we need "added" array
        added = [0] * len(bin_data[0])
        for array in bin_data:
            added += array
        added[added == 0] = 1   # to avoid divide by zero for empty bins

        for index, _ in enumerate(bin_data):
            dispersion[index] = (bin_data[index] / added)

        # if in a bin we have 1% categoryA and 99% categoryB samples, that means dispersion is very low
        # so for both categories we would set it to 1%. i.e: if dispersion > 0.5, take complement
        for i, array in enumerate(dispersion):
            for j, item in enumerate(array):
                if item > 0.5:
                    dispersion[i][j] = 1 - item

        # each bin's dispersion will only affect the samples in that bin, so dispersion for each bin
        # needs to be weighed by nb samples in that bin
        weighed_dispersion = [None] * len(cum_data)
        for index, array in enumerate(dispersion):
            weighed_dispersion[index] = (sum(array * cum_data[-1]) / sum(cum_data[-1]))

        return weighed_dispersion

    def correlation_matrix(self, sort_key=None):
        container_widget = QWidget()
        container_layout = QGridLayout()
        container_widget.setLayout(container_layout)
        super_container = QWidget()
        super_scroll = QScrollArea()

        super_layout = QGridLayout()
        super_layout.addWidget(super_scroll, 0, 0)
        super_container.setLayout(super_layout)

        if sort_key:
            corr = self.df.corr().sort_values(by=sort_key, ascending=False)
        else:
            corr = self.df.corr()

        model = ColorByValModel(dataFrame=corr)
        corr_table = QTableView()
        corr_table.setAlternatingRowColors(True)
        corr_table.setModel(model)
        corr_table.setWindowTitle("Correlation Matrix")

        plot_window = ColorMapWindow(height=1)
        ax = plot_window.figure.add_axes([0.05, 0.80, 0.9, 0.15])
        norm = mpl.colors.Normalize(vmin=-1, vmax=1)
        cb1 = mpl.colorbar.ColorbarBase(ax, cmap=color_map,
                                        norm=norm,
                                        orientation='horizontal')
        cb1.set_label("Correlation color scale")

        container_layout.addWidget(corr_table)
        container_layout.addWidget(plot_window)
        super_scroll.setWidget(container_widget)
        super_scroll.setWidgetResizable(True)
        return super_container

    def info(self, convert=True, cat_limit=5):
        # if something was changed, run info() again
        # one use case is when a column is converted to int
        run_again = False
        index = ['dtype', 'min', 'mean', 'max', 'isAllInts?', '# of unique', '# of nan', '# of null', 'DataFrame Size',
                 'categorical?']
        info_df = pd.DataFrame(index=index, columns=self.df.columns)
        for col in self.df.columns:
            info_df.loc[index[0], col] = self.df[col].dtype
            try:
                info_df.loc[index[1], col] = self.df[col].min()
                info_df.loc[index[2], col] = self.df[col].mean()
                info_df.loc[index[3], col] = self.df[col].max()
            except TypeError:
                pass
            try:
                int_series = self.df[col]-self.df[col].astype(int)
                is_int_series = int_series.sum() == 0
                info_df.loc[index[4], col] = is_int_series
                if is_int_series and convert and np.issubdtype(self.df[col].dtype, np.float64):
                    self.df[col] = self.df[col].astype(int)
                    info_df.loc[index[0], col] = self.df[col].dtype
                    run_again = True
            except Exception as e:
                print(e)
            info_df.loc[index[5], col] = len(self.df[col].unique())
            info_df.loc[index[6], col] = self.df[col].isna().sum()
            info_df.loc[index[7], col] = self.df[col].isnull().sum()
            if info_df.loc[index[5], col] <= cat_limit:
                info_df.loc[index[9], col] = True
            else:
                info_df.loc[index[9], col] = False
        info_df.loc[index[8], info_df.columns[0]] = self.df.shape[0]

        info_df.fillna('', inplace=True)

        if run_again:
            self.info(convert=False, cat_limit=cat_limit)

        model = DatasetModel(dataFrame=info_df)
        info_table = QTableView()
        info_table.setAlternatingRowColors(True)
        info_table.setModel(model)
        info_table.setWindowTitle("Info Stats")
        return info_table, info_df.loc[index[9], :]

    def send_ds_columns(self, object_name):
        self.columns_sent.emit(object_name, self.ds.column_names())
