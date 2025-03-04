from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QSizePolicy, QVBoxLayout
)
from .nui_geo_map import NestGeoMapLegendOverlayWidget


class NestMainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1) Left side: the map + overlay legend
        self.burd_map_overlay = NestGeoMapLegendOverlayWidget(self)
        main_layout.addWidget(self.burd_map_overlay)

        self.setLayout(main_layout)