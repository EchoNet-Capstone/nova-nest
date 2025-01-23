from PySide6.QtWidgets import QWidget, QHBoxLayout, QFrame, QScrollArea
from .nui_burd_status_main_widget import *
from .nui_geo_map import *

class NestMainWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout(self)
        
        burd_map = NestGeoMapWidget()
        burd_map.setStyleSheet("""
            QFrame {
                border: 2px solid black;
                background-color: white;
            }
        """)
        main_layout.addWidget(burd_map, 4)
        
        burd_status_area = QScrollArea()
        burd_status_area.setWidgetResizable(True)
        
        burd_status = NestBurdStatusMainWidget()
        
        burd_status_area.setWidget(burd_status)
        main_layout.addWidget(burd_status_area, 1)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(main_layout)