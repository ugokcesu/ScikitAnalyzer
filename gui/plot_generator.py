import numpy as np
from PyQt5.QtWidgets import QListWidgetItem

from dataset import Dataset
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
                for name in unique_names:
                    hist1.hist(self.df.loc[self.df[color_by]==name, feature_name], alpha=0.5, bins=np_bins, label=name)
                    plt.xlabel(feature_name)
                    hist1.legend()

        # plot_window.layout.addWidget(plot_window)
        return plot_window
