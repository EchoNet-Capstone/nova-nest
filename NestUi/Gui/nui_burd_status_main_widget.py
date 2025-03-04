from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QDockWidget, QScrollArea
from PySide6.QtCore import Qt

from .StatusWidgets import *

class NestBurdStatusDockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buoy_id = -1
        self.init_ui()

    def init_ui(self):
        self.main_widget = QScrollArea(self)
        self.burd_status_layout = QGridLayout(self.main_widget)
        self.status_label = QLabel("Status: Waiting...")
        self.burd_status_layout.addWidget(self.status_label, 0, 0)
        self.setFixedWidth(300)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.setWidget(self.main_widget)
        self.setWindowTitle("Device Status")

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
                self.main_widget.setVisible(False)
                self.setVisible(False)
                self.buoy_id = -1
            else:
                self.main_widget.setVisible(True)
                self.setVisible(True)