from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QSpacerItem
from PySide6.QtCore import Qt

from .StatusWidgets import *

class NestBurdStatusDockWidget(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buoy_id = -1
        self.init_ui()

    def init_ui(self):
        self.burd_status_layout = QGridLayout(self)
        self.burd_status_layout.addWidget(QLabel("BuRD Status"), 0, 0, 1, 1)
        self.status_label = QLabel("Status: Waiting...")
        self.burd_status_layout.addWidget(self.status_label, 1, 0, 4, 1)
        self.setLayout(self.burd_status_layout)
        self.setFixedWidth(300)
        self.setAutoFillBackground(True)

    def update_status(self, buoy_id):
        if(self.isVisible()):
            # Update the status label with the clicked marker's buoy ID.
            self.status_label.setText(f"Marker clicked: {buoy_id}")
            print(f"✅ Burd status updated with marker: {buoy_id}")
            self.buoy_id = buoy_id
    
    def toggle_visible(self, buoy_id):
        if self.buoy_id == buoy_id or self.buoy_id == -1:
            visible = self.isVisible()
            if visible:
                self.setVisible(False)
                self.buoy_id = -1
            else:
                self.setVisible(True)