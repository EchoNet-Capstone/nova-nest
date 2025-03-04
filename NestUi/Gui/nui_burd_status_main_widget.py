from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QDockWidget
from PySide6.QtCore import Qt

from .StatusWidgets import *

class NestBurdStatusMainWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.burd_status_layout = QGridLayout(self)
        self.status_label = QLabel("Status: Waiting...")
        self.burd_status_layout.addWidget(self.status_label, 0, 0)
        self.setFixedWidth(300)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

    def update_status(self, buoy_id):
        if(self.isVisible()):
            # Update the status label with the clicked marker's buoy ID.
            self.status_label.setText(f"Marker clicked: {buoy_id}")
            print(f"✅ Burd status updated with marker: {buoy_id}")
    
    def toggle_visible(self):
        self.setVisible(not self.isVisible())