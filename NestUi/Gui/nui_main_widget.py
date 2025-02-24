from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy, QScrollArea
from .nui_burd_status_main_widget import *
from .nui_geo_map import *

class NestMainWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        
        burd_map = NestGeoMapWidget(self)
        burd_map.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(burd_map, 4)
        
        burd_status_area = QScrollArea()
        burd_status_area.setWidgetResizable(True)
        
        burd_status = NestBurdStatusMainWidget(self)
        
        burd_status_area.setWidget(burd_status)
        main_layout.addWidget(burd_status_area, 1)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        burd_map.markerClicked.connect(burd_status.update_status)
        
        self.setLayout(main_layout)