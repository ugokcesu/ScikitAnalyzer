from PyQt5.QtWidgets import QWidget, QCheckBox, QGridLayout, QLabel, QSpinBox, QGroupBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt

from gui.table_widget import TableWidgetState


class DataAnalysisTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DataAnalysisDock")
        self.setWindowTitle("Data Analysis")

        self._current_table_widget = None

        # viewing options widgets and layout
        self._current_ds_lb = QLabel("Current Dataset:")
        self._view_description_cb = QCheckBox("Show description")
        self._view_table_cb = QCheckBox("Show Table")

        self._view_layout = QVBoxLayout()
        self._view_layout.addWidget(self._current_ds_lb)
        self._view_layout.addWidget(self._view_description_cb)
        self._view_layout.addWidget(self._view_table_cb)
        # viewing options group
        self._view_gb = QGroupBox()
        self._view_gb.setTitle("View Options")
        self._view_gb.setLayout(self._view_layout)

        # layout for the whole tab
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.addWidget(self._view_gb, 0, 0)

        self.setLayout(self._layout)

        # signal slot connections
        self._view_table_cb.clicked.connect(self.update_table_widget)
        self._view_description_cb.clicked.connect(self.update_table_widget)

    #when checkboxes are clicked, send updates to the TableView
    def update_table_widget(self):
        if self._current_table_widget is not None:
            state = TableWidgetState("dummy")
            state.table_visible = self._view_table_cb.isChecked()
            state.description_visible = self._view_description_cb.isChecked()
            self._current_table_widget.update_with_state(state)

    def update_upon_window_activation(self):
        sender = self.sender()
        try:
            self._current_table_widget = sender.activeSubWindow().widget()
        except AttributeError:
            return
        self.update_self_with_window_state(self._current_table_widget.window_state)

    # when a new mdi window is selected, set the view checkboxes
    def update_self_with_window_state(self, state):
        self._view_table_cb.setChecked(state.table_visible)
        self._view_description_cb.setChecked(state.description_visible)
        self._current_ds_lb.setText("Current Dataset: {}".format(state.dataset_name))




