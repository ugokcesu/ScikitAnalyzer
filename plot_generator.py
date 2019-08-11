import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QTableView
from PyQt5.QtGui import QStandardItem

from dataset import Dataset
from dataset_model import DatasetModel
from gui.plot_window import PlotWindow

import matplotlib.pyplot as plt


class PlotGenerator:
    def __init__(self, ds: Dataset):
        self.df = ds.data_frame()

    def generate_histogram(self, data: list, color_by=""):
        plot_window = PlotWindow(height=3*len(data))
        if not hasattr(self.df, color_by):
            for index, item in enumerate(data):
                feature_name = item.data(0)
                hist1 = plot_window.figure.add_subplot(len(data), 1, index+1)
                np_bins = np.histogram_bin_edges(self.df[feature_name], bins='auto')
                hist1.hist(self.df[feature_name], alpha=0.5, bins=np_bins, label=feature_name)
                plt.xlabel(feature_name)
                hist1.legend()
        else:
            unique_names = self.df[color_by].unique()
            for index, item in enumerate(data):
                feature_name = item.data(0)
                hist1 = plot_window.figure.add_subplot(len(data), 1, index + 1)
                np_bins = np.histogram_bin_edges(self.df[feature_name], bins='auto')
                all_data = []
                for name in unique_names:
                    all_data.append(self.df.loc[self.df[color_by] == name, feature_name])
                nedir = hist1.hist(all_data, stacked=True, bins=np_bins, label=name)
                plt.xlabel(feature_name)
                hist1.legend()
                    #hist1.hist(self.df.loc[self.df[color_by] == name, feature_name], stacked=True, alpha=0.5, bins=np_bins, label=name)
                    #plt.xlabel(feature_name)
                    #hist1.legend()

        # plot_window.layout.addWidget(plot_window)
        return plot_window

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


