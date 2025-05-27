from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QSpacerItem, QPushButton, QCheckBox, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from .StatusWidgets import *
from NestUi.Utils import nest_db

class NestBurdStatusDockWidget(QScrollArea):
    marker_released = Signal(int)  # Signal to notify marker removal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buoy_id = -1
        self.init_ui()

    def init_ui(self):
        self.burd_status_layout = QGridLayout()
        self.setLayout(self.burd_status_layout)
        self.setFixedWidth(300)
        self.setAutoFillBackground(True)

        self.burd_status_layout.addWidget(QLabel("BuRD Status"), 0, 0, 1, 2)

        self.id_label = QLabel("ID: -")
        self.burd_status_layout.addWidget(self.id_label, 1, 0, 1, 2)

        self.located_checkbox = QCheckBox("Located")
        self.burd_status_layout.addWidget(self.located_checkbox, 2, 0)
        self.opened_checkbox = QCheckBox("Opened?")
        self.burd_status_layout.addWidget(self.opened_checkbox, 2, 1)

        self.battery_label = QLabel("Battery: -- %")
        self.burd_status_layout.addWidget(self.battery_label, 3, 0, 1, 2)

        # Buttons (now disconnected)
        self.locate_button = QPushButton("Locate")
        self.update_button = QPushButton("Update")
        self.release_button = QPushButton("Release")
        # Only leave Locate as a no-op
        # self.locate_button.clicked.connect(self.on_locate)
        # self.update_button.clicked.connect(self.on_update)
        # self.release_button.clicked.connect(self.on_release)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.locate_button)
        button_layout.addWidget(self.update_button)
        self.burd_status_layout.addLayout(button_layout, 4, 0, 1, 2)
        self.burd_status_layout.addWidget(self.release_button, 5, 0, 1, 2)

        self.clear_status()

    def clear_status(self):
        self.id_label.setText("ID: -")
        self.located_checkbox.setChecked(False)
        self.opened_checkbox.setChecked(False)
        self.battery_label.setText("Battery: -- %")
        self.setVisible(False)

    def update_status(self, buoy_id):
        if self.isVisible():
            self.buoy_id = int(buoy_id)
            self.id_label.setText(f"ID: {self.buoy_id}")
            # Query the database for this buoy
            buoy = nest_db.get_buoy_by_id(self.buoy_id)
            if buoy:
                # Only battery is available in schema
                self.located_checkbox.setChecked(False)
                self.located_checkbox.setEnabled(False)
                self.opened_checkbox.setChecked(False)
                self.opened_checkbox.setEnabled(False)
                self.battery_label.setText(f"Battery: {getattr(buoy, 'battery', '--')} %")
            else:
                self.clear_status()
    
    def toggle_visible(self, buoy_id):
        if self.buoy_id == int(buoy_id) or self.buoy_id == -1:
            visible = self.isVisible()
            if visible:
                self.setVisible(False)
                self.buoy_id = -1
            else:
                self.setVisible(True)
                self.update_status(buoy_id)

    def on_locate(self):
        # Implement locate logic (e.g., highlight marker on map)
        pass

    def on_update(self):
        if self.buoy_id != -1:
            self.update_status(self.buoy_id)

    def on_release(self):
        if self.buoy_id != -1:
            nest_db.delete_buoy(self.buoy_id)
            self.marker_released.emit(self.buoy_id)
            self.clear_status()