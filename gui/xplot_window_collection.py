from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout, QWidget, QCheckBox, QLineEdit

import pandas as pd
import matplotlib as mpl
import numpy as np

from gui.plot_window import PlotWindow
from gui.dynamic_combobox import DynamicComboBox
from gui.range_slider import QRangeSlider
from color_by_val_model import color_map
from gui.color_map_window import ColorMapWindow
from gui.pushbutton_w_index import PushButtonWIndex
from dataset import Dataset


class XPlotWindowCollection(QWidget):
    request_columns = pyqtSignal(str)
    request_data = pyqtSignal(str)
    mask_updated = pyqtSignal()
    mask_created_from_xplot = pyqtSignal(str)

    def __init__(self, ds, x_props, y_props, alpha=1, parent=None):
        super().__init__(parent)
        self.ds = ds
        self.x_props = x_props
        self.y_props = y_props
        self.alpha = alpha
        self.axes = [[None for i in range(len(x_props))] for j in range(len(y_props))]
        self.props = [[None for i in range(len(x_props))] for j in range(len(y_props))]
        self.xplots = [[None for i in range(len(x_props))] for j in range(len(y_props))]
        self.windows = [[None for i in range(len(x_props))] for j in range(len(y_props))]
        self.mask = pd.Series([True for x in range(self.ds.samples())])
        # color by selection
        self.color_by_lb = QLabel("Color By:")
        self.color_by = DynamicComboBox()
        self.color_by.setObjectName("ColorBy")
        self.fill_combo(self.color_by)
        self.color_by.currentTextChanged.connect(self.color_plots)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.color_by_lb, 1, 0, Qt.AlignLeft)
        self.layout.addWidget(self.color_by, 1, 1, Qt.AlignLeft)

        # selection for filtering
        self.filter_layout = QGridLayout()
        self.filter_layout.setColumnStretch(1, 1)
        self.layout.addLayout(self.filter_layout, 2, 0, 1, 5)
        self.row_counter = 0

        self.add_filter_btn = QPushButton("Add Filter")
        self.add_filter_btn.clicked.connect(self.filter_added)
        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.color_plots)
        self.auto_apply_cb = QCheckBox("Auto-apply Filter")
        self.auto_apply_cb.setChecked(False)
        self.auto_apply_cb.toggled.connect(self.auto_apply_toggled)
        self.save_mask_btn = QPushButton("Save mask as column")
        self.save_mask_btn.clicked.connect(self.save_mask)
        self.mask_col_name_le = QLineEdit("mask")
        self.layout.addWidget(self.add_filter_btn, 3, 0, Qt.AlignLeft)
        self.layout.addWidget(self.apply_filter_btn, 3, 1, Qt.AlignLeft)
        self.layout.addWidget(self.auto_apply_cb, 3, 2, Qt.AlignLeft)
        self.layout.addWidget(self.mask_col_name_le, 3, 3, Qt.AlignLeft)
        self.layout.addWidget(self.save_mask_btn, 3, 4)
        self.layout.setColumnStretch(4, 1)
        #self.layout.setColumnStretch(3, 1)

        # add all comboboxes to this list:
        self.filters_list = []
        self.masks = {} # stores {filter_index:mask_array}

    def save_mask(self):
        name = self.mask_col_name_le.text()
        if name in self.ds.column_names():
            return
        self.ds.df[name] = self.mask.astype(int)
        self.mask_created_from_xplot.emit(name)

    def auto_apply_toggled(self):
        if self.auto_apply_cb.isChecked():
            self.apply_filter_btn.setDisabled(True)
            self.mask_updated.connect(self.color_plots)
        else:
            self.apply_filter_btn.setDisabled(False)
            self.mask_updated.disconnect()

    def filter_added(self):
        filtering_combo = DynamicComboBox(index=self.row_counter)
        self.fill_combo(filtering_combo)
        filtering_combo.currentTextChanged.connect(self.filter_selected)
        filter_slider = QRangeSlider(index=self.row_counter)
        filter_slider.hide()
        filter_slider.setMinimumWidth(150)
        delete_btn = PushButtonWIndex("Delete", self.row_counter)
        delete_btn.clicked.connect(self.delete_filter)
        delete_btn.hide()
        self.filters_list.append(filtering_combo)

        self.filter_layout.addWidget(filtering_combo, self.row_counter, 0, Qt.AlignLeft)
        self.filter_layout.addWidget(filter_slider, self.row_counter, 1)
        self.filter_layout.addWidget(delete_btn, self.row_counter, 2)

        self.row_counter += 1

    def filter_selected(self):
        combo = self.sender()
        if combo.currentText() not in self.ds.column_names():
            return
        col = combo.currentText()
        index = combo.index
        slider = self.filter_layout.itemAtPosition(index, 1).widget()
        delete_btn = self.filter_layout.itemAtPosition(index, 2).widget()
        delete_btn.show()
        min_filter, max_filter = self.ds.df[col].min(), self.ds.df[col].max()
        min_filter, max_filter = min(min_filter, max_filter), max(min_filter, max_filter)
        slider.setMin(min_filter)
        slider.setMax(max_filter)
        slider.setRange(min_filter, max_filter)
        slider.show()

        slider.startValueChanged.connect(self.filter_slider_edited)
        slider.endValueChanged.connect(self.filter_slider_edited)

    def filter_slider_edited(self):
        slider = self.sender()
        if not isinstance(slider, QRangeSlider):
            return TypeError
        index = slider.index
        min, max = slider.getRange()
        combo = self.find_combo(index)
        col = combo.currentText()
        if col:
            self.masks[slider.index] = (self.ds.df[col] <= max) & (self.ds.df[col] >= min)
            self.update_mask()

    def update_mask(self):
        self.mask = pd.Series([True for i in range(self.ds.samples())])
        for mask in self.masks.values():
            self.mask = self.mask & mask
        self.mask_updated.emit()

    def find_combo(self, index):
        for child in self.children():
            if isinstance(child, DynamicComboBox) and child.index==index:
                return child

    def delete_filter(self):
        if not isinstance(self.sender(), PushButtonWIndex):
            raise TypeError
        row = self.sender().index
        self.filter_layout.itemAtPosition(row, 0).widget().hide()
        self.filter_layout.itemAtPosition(row, 1).widget().hide()
        self.filter_layout.itemAtPosition(row, 2).widget().hide()
        self.masks.pop(row, -1)
        self.color_plots()

    def fill_combo(self, combo):
        if isinstance(combo, DynamicComboBox):
            combo.clear()
            combo.addItem("")
            combo.addItems(self.ds.numerical_columns)

    def on_draw(self):
        axes_in_figure = self.figure.axes
        quadmesh = axes_in_figure[0].collections[0]
        quadmesh.set_clim(self.slider.start(), self.slider.end())
        self.canvas.draw()

    def request_data_for_plot_color(self):
        self.request_data.emit(self.color_by.currentText())

    def color_plots(self):
        for i, out_prop in enumerate(self.x_props):
            for j, in_prop in enumerate(self.y_props):
                if self.windows[j][i] is None:
                    continue

                axes = self.windows[j][i].figure.axes
                ax = axes[0]
                scatter = ax.collections[0]
                scatter.remove()
                x = self.ds.df[self.mask][out_prop.data(0)]
                y = self.ds.df[self.mask][in_prop.data(0)]

                color_by = self.color_by.currentText()
                if color_by not in self.ds.column_names():
                    ax.scatter(x, y, marker='.', c='blue',
                               alpha=self.alpha)
                else:

                    color_data = self.ds.df[color_by]
                    p2, p98 = np.percentile(color_data, [2, 98])
                    ax.scatter(x, y, c=self.ds.df[self.mask][color_by], marker='.',
                               alpha=self.alpha, vmin=p2, vmax=p98, cmap=color_map)
                    color_scale = ColorMapWindow(height=0.8)
                    ax = color_scale.figure.add_axes([0.05, 0.85, 0.9, 0.15])
                    norm = mpl.colors.Normalize(vmin=p2, vmax=p98)
                    cb1 = mpl.colorbar.ColorbarBase(ax, cmap=color_map,
                                                    norm=norm,
                                                    orientation='horizontal')
                    cb1.set_label(color_by)
                    self.layout.addWidget(color_scale, 1, 2)
                self.windows[j][i].canvas.draw()
