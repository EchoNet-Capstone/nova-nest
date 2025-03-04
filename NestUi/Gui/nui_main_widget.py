from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QSizePolicy, QVBoxLayout
)
from .nui_geo_map import NestGeoMapLegendOverlayWidget
from .nui_burd_status_main_widget import NestBurdStatusDockWidget

class NestMainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1) Left side: the map + overlay legend
        self.burd_map_overlay = NestGeoMapLegendOverlayWidget(self)
        main_layout.addWidget(self.burd_map_overlay)

        self.burd_status = NestBurdStatusDockWidget(self)
        self.burd_status.move(self.width() - self.burd_status.width(), 0)
        self.burd_status.resize(self.burd_status.width(), self.height())
        self.burd_status.hide()

        self.burd_map_overlay.map_view.web_page.marker_clicked.connect(self.burd_status.toggle_visible)
        self.burd_map_overlay.map_view.web_page.marker_clicked.connect(self.burd_status.update_status)

        self.setLayout(main_layout)
    
    def resizeEvent(self, event):
        self.burd_status.move(self.width() - self.burd_status.width(), 0)
        self.burd_status.resize(self.burd_status.width(), self.height())
        return super().resizeEvent(event)
    