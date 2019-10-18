from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout, QWidget, QCheckBox

import pandas as pd
import matplotlib as mpl

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

    def __init__(self, ds, x_props, y_props, parent=None):
        super().__init__(parent)
        self.ds = ds
        self.x_props = x_props
        self.y_props = y_props
        self.alpha = 0.3
        self.axes = [[0 for i in range(len(x_props))] for j in range(len(y_props))]
        self.props = [[0 for i in range(len(x_props))] for j in range(len(y_props))]
        self.xplots = [[0 for i in range(len(x_props))] for j in range(len(y_props))]
        self.windows = [[0 for i in range(len(x_props))] for j in range(len(y_props))]
        self.mask = pd.Series([True for x in range(self.ds.samples())])
        # color by selection
        self.color_by_lb = QLabel("Color By:")
        self.color_by = DynamicComboBox()
        self.color_by.setObjectName("ColorBy")
        self.color_by.popup_clicked.connect(self.fill_combo)
        self.color_by.currentTextChanged.connect(self.color_plots)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.color_by_lb, 1, 0, Qt.AlignLeft)
        self.layout.addWidget(self.color_by, 1, 1, Qt.AlignLeft)

        # selection for filtering
        self.row_counter = 2
        self.add_filter_btn = QPushButton("Add Filter")
        self.add_filter_btn.clicked.connect(self.filter_added)
        self.layout.addWidget(self.add_filter_btn, self.row_counter, 0, Qt.AlignLeft)
        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.color_plots)
        self.auto_apply_cb = QCheckBox("Auto-apply Filter")
        self.auto_apply_cb.setChecked(False)
        self.auto_apply_cb.toggled.connect(self.auto_apply_toggled)
        self.layout.addWidget(self.apply_filter_btn, self.row_counter, 1, Qt.AlignLeft)
        self.layout.addWidget(self.auto_apply_cb, self.row_counter, 2, Qt.AlignLeft)

        # add all comboboxes to this list:
        self.filters_list = []
        self.masks = {} # stores {filter_index:mask_array}

    def auto_apply_toggled(self):
        if self.auto_apply_cb.isChecked():
            self.apply_filter_btn.setDisabled(True)
            self.mask_updated.connect(self.color_plots)
        else:
            self.apply_filter_btn.setDisabled(False)
            self.mask_updated.disconnect()

    def filter_added(self):
        filtering_combo = DynamicComboBox(index=self.row_counter)
        filtering_combo.popup_clicked.connect(self.fill_combo)
        filtering_combo.currentTextChanged.connect(self.filter_selected)
        self.filters_list.append(filtering_combo)
        self.layout.addWidget(filtering_combo, self.row_counter, 0)
        self.layout.addWidget(self.add_filter_btn, self.row_counter + 1, 0)
        self.layout.addWidget(self.apply_filter_btn, self.row_counter + 1, 1)
        self.layout.addWidget(self.auto_apply_cb, self.row_counter + 1, 2)
        self.row_counter += 1

    def filter_selected(self):
        combo = self.sender()
        if combo.currentText() not in self.ds.column_names():
            return
        col = combo.currentText()
        min_filter, max_filter = self.ds.df[col].min(), self.ds.df[col].max()
        filter_slider = QRangeSlider(index=combo.index)
        filter_slider.setMin(min_filter)
        filter_slider.setMax(max_filter)
        filter_slider.setRange(min_filter, max_filter)
        self.layout.addWidget(filter_slider, combo.index, 1)
        filter_slider.startValueChanged.connect(self.filter_slider_edited)
        filter_slider.endValueChanged.connect(self.filter_slider_edited)
        delete_btn = PushButtonWIndex("Delete", combo.index)
        delete_btn.clicked.connect(self.delete_filter)
        self.layout.addWidget(delete_btn, combo.index, 2)

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
        # self.color_plots()

    def find_combo(self, index):
        for child in self.children():
            if isinstance(child, DynamicComboBox) and child.index==index:
                return child

    def delete_filter(self):
        if not isinstance(self.sender(), PushButtonWIndex):
            raise TypeError
        row = self.sender().index
        item1 = self.layout.itemAtPosition(row, 0).widget().hide()
        item2 = self.layout.itemAtPosition(row, 1).widget().hide()
        item3 = self.layout.itemAtPosition(row, 2).widget().hide()
        self.masks.pop(row, -1)

    def fill_combo(self):
        widget = self.sender()
        widget.clear()
        widget.addItem("")
        #widget.setCurrentIndex(0)
        widget.addItems(self.ds.column_names())

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
                    ax.scatter(x, y, c=self.ds.df[self.mask][color_by], marker='.',
                               alpha=self.alpha)
                    color_scale = ColorMapWindow(height=0.7)
                    ax = color_scale.figure.add_axes([0.05, 0.80, 0.9, 0.15])
                    norm = mpl.colors.Normalize(vmin=color_data.min(), vmax=color_data.max())
                    cb1 = mpl.colorbar.ColorbarBase(ax, cmap=color_map,
                                                    norm=norm,
                                                    orientation='horizontal')
                    cb1.set_label("Color scale")
                    self.layout.addWidget(color_scale, 1, 2)
                self.windows[j][i].canvas.draw()

'''
    def update_slider(self):
        axes = self.figure.axes
        try:
            start, end = axes[0].collections[0].get_clim()
            self.slider.setMin(0)
            self.slider.setMax(end*2)
            self.slider.setRange(0, end)
            self.slider.setRange(start, end)
        except Exception as e:
            pass
'''