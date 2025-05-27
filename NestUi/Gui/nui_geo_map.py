import os
from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QGridLayout, QLabel, QSizePolicy, QVBoxLayout
)
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import Qt, Signal, Slot
from pyqtlet2 import L, MapWidget
from ..Utils.nest_map import get_buoys_from_db

# --------------------------------------------------------------------
# Main Map Widget
# --------------------------------------------------------------------
class NestGeoMapWidget(MapWidget):
    marker_clicked = Signal(str)  # Signal to emit when a marker is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.init_ui()
        self.show()

    def init_ui(self):
        # Set up the map with OpenStreetMap tiles
        self.map = L.map(self)
        self.map.setView([44.5, -68.5], 7)

        # Use localhost:5000 as the tile server
        L.tileLayer('http://localhost:9000/styles/klokantech-basic/{z}/{x}/{y}.png').addTo(self.map)

        # Create marker icons in JavaScript
        self.create_marker_icons()
        
        # Add buoy markers
        self.add_buoy_markers()

    def add_vector_grid_layer(self):
        vector_grid_js = """
        var script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet.vectorgrid/dist/Leaflet.VectorGrid.bundled.js';
        script.onload = function() {
            var vectorTileOptions = {
                interactive: true,
                maxNativeZoom: 14,
                maxZoom: 20
            };
            
            var vectorGrid = L.vectorGrid.protobuf(
                'http://localhost:9000/data/{z}/{x}/{y}.pbf',
                vectorTileOptions
            );
            
            vectorGrid.addTo(map);  // map is globally defined by pyqtlet2
        };
        document.head.appendChild(script);
        """
        self.map.runJavaScript(vector_grid_js, 0)

    def create_marker_icons(self):
        # Create marker icons in JavaScript runtime
        icon_js = """
        var greenIcon = L.icon({
            iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="green" stroke="black" stroke-width="1"/></svg>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        var yellowIcon = L.icon({
            iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="yellow" stroke="black" stroke-width="1"/></svg>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        var redIcon = L.icon({
            iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="red" stroke="black" stroke-width="1"/></svg>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        var blueIcon = L.icon({
            iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" fill="blue" stroke="black" stroke-width="1"/></svg>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        var blackIcon = L.icon({
            iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="black" stroke="black" stroke-width="1"/></svg>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        """
        self.map.runJavaScript(icon_js, 0)

    def add_buoy_markers(self):
        markers = get_buoys_from_db()
        for marker in markers:
            marker.addTo(self.map)
            # Set the appropriate icon based on the marker's color
            if hasattr(marker, 'options') and 'color' in marker.options:
                color = marker.options['color']
                self.map.runJavaScript(f'{marker.jsName}.setIcon({color}Icon);', 0)
            
            # Add popup with buoy information
            if hasattr(marker, 'options') and 'title' in marker.options:
                popup_content = marker.options['title']
                self.map.runJavaScript(f'{marker.jsName}.bindPopup(`{popup_content}`);', 0)

            # Connect the click signal
            if hasattr(marker, 'options') and 'buoy_id' in marker.options:
                buoy_id = marker.options['buoy_id']
                marker.click.connect(lambda event=marker.click, bid=buoy_id: self.marker_clicked.emit(buoy_id))

# --------------------------------------------------------------------
# Custom Legend Widget as a QFrame
# --------------------------------------------------------------------
class CustomBuoyLegendWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #efefef;
                border: 1px solid black;
                margin: 0px;
                padding: 0px;
            }
        """)
        self._init_ui()
        self.setFixedSize(self.sizeHint())

    def _init_ui(self):
        layout = QGridLayout(self)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_label = QLabel("Legend")
        header_label.setStyleSheet("border: none; padding-left: 6px; margin-right 6px; font-weight: bold; background: transparent;")
        layout.addWidget(header_label, 0, 0, alignment=Qt.AlignLeft)

        # Horizontal separator
        h_separator = QFrame()
        h_separator.setFrameShape(QFrame.HLine)
        h_separator.setStyleSheet("background-color: black; border: none; margin: 0px; padding: 0px;")
        h_separator.setFixedHeight(1)
        layout.addWidget(h_separator, 1, 0, 1, 3)

        # Vertical separator
        v_separator = QFrame()
        v_separator.setFrameShape(QFrame.VLine)
        v_separator.setStyleSheet("background-color: black; border: none; margin: 0px; padding: 0px;")
        v_separator.setFixedWidth(1)
        layout.addWidget(v_separator, 0, 1, 4, 1)

        # Legend items
        layout.addWidget(self._create_legend_item("green", "Good", shape="circle"), 0, 2, 2, 1, alignment=Qt.AlignLeft)
        layout.addWidget(self._create_legend_item("blue", "My Ship", shape="square"), 2, 0, alignment=Qt.AlignLeft)
        layout.addWidget(self._create_legend_item("yellow", "Battery Below 50%", shape="circle"), 2, 2, alignment=Qt.AlignLeft)
        layout.addWidget(self._create_legend_item("black", "Selected BuRD", shape="circle"), 3, 0, alignment=Qt.AlignLeft)
        layout.addWidget(self._create_legend_item("red", "Battery Below 20%", shape="circle"), 3, 2, alignment=Qt.AlignLeft)

    def _create_legend_item(self, color, text, shape="circle"):
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(6, 0, 0, 0)
        h_layout.setSpacing(0)

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        if shape == "circle":
            icon_label.setStyleSheet(f"background-color: {color}; border: 1px solid black; border-radius: 10px;")
        else:
            icon_label.setStyleSheet(f"background-color: {color}; border: 1px solid black;")

        text_label = QLabel(text)
        text_label.setStyleSheet("margin-right: 6px; color: black; background: transparent;")

        h_layout.addWidget(icon_label)
        h_layout.addWidget(text_label)
        return container

# --------------------------------------------------------------------
# Composite Widget Combining Map and Legend
# --------------------------------------------------------------------
class NestGeoMapLegendOverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create a layout for this widget
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        
        # Create and add the map view
        self.map_view = NestGeoMapWidget(self)
        self.layout().addWidget(self.map_view)
        
        # Create the legend panel
        self.legend_panel = CustomBuoyLegendWidget(self)
        self.legend_panel.setFixedSize(self.legend_panel.sizeHint())
        
        # Ensure the map view takes up all available space
        self.map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        # Position the legend at the bottom left of the map with no margin
        legend_width = self.legend_panel.width()
        legend_height = self.legend_panel.height()
        self.legend_panel.move(0, self.height() - legend_height)
        return super().resizeEvent(event)
