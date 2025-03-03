from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QSizePolicy, QVBoxLayout
)
from .nui_burd_status_main_widget import NestBurdStatusMainWidget
from .nui_geo_map import NestGeoMapLegendOverlayWidget


class NestMainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1) Left side: the map + overlay legend
        self.burd_map_overlay = NestGeoMapLegendOverlayWidget(self)
        main_layout.addWidget(self.burd_map_overlay, 4)

        # 2) Right side: a scrollable status panel
        burd_status_area = QScrollArea()
        burd_status_area.setWidgetResizable(True)
        self.burd_status = NestBurdStatusMainWidget(self)
        burd_status_area.setWidget(self.burd_status)
        main_layout.addWidget(burd_status_area, 1)

        # If NestGeoMapWidget emits markerClicked, connect it
        self.burd_map_overlay.map_view.markerClicked.connect(self.burd_status.update_status)

        self.setLayout(main_layout)