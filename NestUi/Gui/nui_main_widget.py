from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt
from ..Utils.nest_serialno_init import add_buoy_serial_protocol
from .nui_geo_map import NestGeoMapLegendOverlayWidget
from .nui_burd_status_main_widget import NestBurdStatusDockWidget
from NestUi.Utils import nest_db
from datetime import datetime
import geocoder

class NestMainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main map overlay (fills parent)
        self.burd_map_overlay = NestGeoMapLegendOverlayWidget(self)
        self.burd_map_overlay.setGeometry(0, 0, self.width(), self.height())

        self.burd_status = NestBurdStatusDockWidget(self)
        self.burd_status.move(self.width() - self.burd_status.width(), 0)
        self.burd_status.resize(self.burd_status.width(), self.height())
        self.burd_status.hide()

        self.burd_map_overlay.map_view.web_page.marker_clicked.connect(self.burd_status.toggle_visible)
        self.burd_map_overlay.map_view.web_page.marker_clicked.connect(self.burd_status.update_status)

        # --- Floating bottom center button bar ---
        self.button_bar_widget = QWidget(self)
        self.button_bar_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.button_bar_widget.setStyleSheet("background: rgba(0,0,0,0.85); border-radius: 12px;")

        button_bar = QHBoxLayout(self.button_bar_widget)
        button_bar.setContentsMargins(16, 8, 16, 8)
        button_bar.setSpacing(24)  # Add spacing between buttons

        button_style = (
            "QPushButton {"
            " background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #232526, stop:1 #414345);"
            " color: white;"
            " font-weight: bold;"
            " font-size: 18px;"
            " border-radius: 14px;"
            " padding: 10px 24px;"
            " min-width: 140px;"
            " min-height: 36px;"
            " letter-spacing: 1px;"
            " border: 2px solid #333;"
            " }"
            "QPushButton:hover {"
            " background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #414345, stop:1 #232526);"
            " color: #FFD700;"
            " border: 2px solid #FFD700;"
            " }"
        )

        # Remove LEGEND button
        self.add_burd_button = QPushButton("ADD BuRD")
        self.add_burd_button.setStyleSheet(button_style)
        self.remove_burd_button = QPushButton("Remove BuRD")
        self.remove_burd_button.setStyleSheet(button_style)
        self.update_map_button = QPushButton("Update Map")
        self.update_map_button.setStyleSheet(button_style)

        button_bar.addWidget(self.add_burd_button)
        button_bar.addWidget(self.remove_burd_button)
        button_bar.addWidget(self.update_map_button)
        button_bar.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Connect buttons to actions
        self.add_burd_button.clicked.connect(self.add_burd_to_db)
        self.remove_burd_button.clicked.connect(self.remove_burd_from_db)
        self.update_map_button.clicked.connect(self.refresh_map)

    def resizeEvent(self, event):
        # Resize map overlay to fill parent
        self.burd_map_overlay.setGeometry(0, 0, self.width(), self.height())
        # Position the button bar at the bottom right
        bar_width = 800
        bar_height = 80
        margin_bottom = 32
        margin_right = 32
        x = self.width() - bar_width - margin_right
        y = self.height() - bar_height - margin_bottom
        self.button_bar_widget.setGeometry(x, y, bar_width, bar_height)
        self.burd_status.move(self.width() - self.burd_status.width(), 0)
        self.burd_status.resize(self.burd_status.width(), self.height())
        return super().resizeEvent(event)

    def add_burd_to_db(self):
        # Get serial number from user
        serial_number, ok = QInputDialog.getText(
            self, 
            "Add BuRD", 
            "Enter Serial Number:",
            text=""
        )
        if not ok or not serial_number:
            return

        # Get device ID from user
        did, ok = QInputDialog.getText(
            self,
            "Add BuRD",
            "Enter Device ID:",
            text=""
        )
        if not ok or not did:
            return

        # Get network ID from user
        nid, ok = QInputDialog.getText(
            self,
            "Add BuRD",
            "Enter Network ID:",
            text=""
        )
        if not ok or not nid:
            return

        # Default serial port and baud rate
        serial_port = '/dev/ttys015'  # or COMx on Windows
        baud_rate = 9600

        try:
            if add_buoy_serial_protocol(serial_port, baud_rate, serial_number, did, nid):
                # Try to get geolocation first
                g = geocoder.ip('me')
                if g.ok and g.latlng:
                    lat, lon = g.latlng
                    self._add_burd_with_coords(lat, lon)
                else:
                    # Fallback: get map center from JS
                    def handle_center(center):
                        if not center:
                            QMessageBox.critical(self, "Error", "Could not get map center or geolocation.")
                            return
                        lat = center['lat']
                        lon = center['lng']
                        self._add_burd_with_coords(lat, lon)
                    js = "map.getCenter();"
                    self.burd_map_overlay.map_view.page().runJavaScript(js, handle_center)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add BuRD: {e}")

    def _add_burd_with_coords(self, lat, lon):
        battery, ok = QInputDialog.getInt(self, "Add BuRD", "Battery %:", 100, 0, 100)
        if not ok:
            return
        try:
            nest_db.create_buoy(lat, lon, battery, datetime.now())
            QMessageBox.information(self, "Success", "BuRD added to database!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add BuRD: {e}")

    def remove_burd_from_db(self):
        # Example: Prompt for Buoy ID to remove
        buoy_id, ok = QInputDialog.getInt(self, "Remove BuRD", "Buoy ID:", 1, 1)
        if not ok:
            return
        try:
            nest_db.delete_buoy(buoy_id)
            QMessageBox.information(self, "Success", f"BuRD {buoy_id} removed from database!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove BuRD: {e}")

    def refresh_map(self):
        # Remove and recreate the entire map widget
        self.burd_map_overlay.setParent(None)
        self.burd_map_overlay.deleteLater()
        self.burd_map_overlay = NestGeoMapLegendOverlayWidget(self)
        self.burd_map_overlay.setGeometry(0, 0, self.width(), self.height())
        self.burd_map_overlay.map_view.web_page.marker_clicked.connect(self.burd_status.toggle_visible)
        self.burd_map_overlay.map_view.web_page.marker_clicked.connect(self.burd_status.update_status)
        self.burd_map_overlay.raise_()
        self.button_bar_widget.raise_()
        self.burd_status.raise_()
    