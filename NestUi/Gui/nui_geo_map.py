import os
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import Qt, Signal
from folium import Element
from jinja2 import Template
from ..Utils.nest_map import *

class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        # Check if the message is our marker click signal.
        if msg.startswith("markerClicked:"):
            buoy_id = msg.split("markerClicked:")[1]
            print(f"✅ Received Buoy ID from JS: {buoy_id}")
            # Call the parent's handler for marker clicks.
            self.parent().on_marker_click(buoy_id)
        else:
            # Otherwise, print normally.
            print(f"JavaScript Console [{level}]: {msg}")

class NestGeoMapWidget(QWidget):
    markerClicked = Signal(str)
    """PySide6 Widget for displaying a Folium map in QWebEngineView without using WebChannel."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Create QWebEngineView with custom page
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.web_page = WebEnginePage(self)
        self.web_view.setPage(self.web_page)

        # Write the HTML map to disk and load it as a file URL
        map_html = get_html_map()  # This writes "clickable_map.html" to disk.
        self.web_view.setHtml(map_html)
        layout.addWidget(self.web_view)

    def on_marker_click(self, buoy_id):
        print(f"✅ Buoy Marker Clicked: {buoy_id}")
        self.markerClicked.emit(buoy_id)

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap

# Replace these imports with your actual modules:
# from .nui_geo_map import NestGeoMapWidget

class BuoyLegendWidget(QWidget):
    """
    A simple horizontal legend with color-coded or icon-based items.
    Overlays the map at the bottom.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Example styling: semi-transparent light background, a thin border
        self.setStyleSheet("""
            background-color: black;
            border: 1px solid #ccc;
        """)

        # We’ll create a horizontal layout in code (below) to place items side by side
        self._init_ui()

    def _init_ui(self):
        """
        Build out the layout with your legend items (color squares, icons, etc.).
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        # Example: color-coded circles
        layout.addWidget(self._create_legend_item_color("red", "Low Battery (< 20%)"))
        layout.addWidget(self._create_legend_item_color("yellow", "Medium Battery (20–50%)"))
        layout.addWidget(self._create_legend_item_color("green", "High Battery (> 50%)"))


    def _create_legend_item_color(self, color, text):
        """
        Creates a small color-coded circle plus a text label in a row.
        """
        container = QWidget()
        row_layout = QHBoxLayout(container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        icon_label = QLabel()
        icon_label.setFixedSize(18, 18)
        icon_label.setStyleSheet(
            f"background-color: {color}; "
            "border-radius: 8px; "  # circle shape
            "border: 1px solid black;"
        )

        text_label = QLabel(text)

        row_layout.addWidget(icon_label)
        row_layout.addWidget(text_label)
        return container
    
class BuoyLegendWidget(QWidget):
    """
    A horizontal legend bar with a black background.
    It has a "Legend:" label and multiple sub-items
    for different battery states (color-coded or icons).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Black background, thin gray border
        self.setStyleSheet("""
            background-color: black;
            border: 1px solid #ccc;
        """)

        # Build the UI
        self._init_ui()

    def _init_ui(self):
        """
        Build the legend layout:
          - "Legend:" label
          - 3 sub-hboxes for Low/Medium/High battery
        """
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(15)

        # A "Legend:" label, styled white/bold
        legend_label = QLabel("Legend:")
        legend_label.setStyleSheet("color: white; font-weight: bold;")
        main_layout.addWidget(legend_label)

        # Add each legend item as a small HBox
        main_layout.addWidget(self._create_legend_item_color("red", "Low Battery (< 20%)"))
        main_layout.addWidget(self._create_legend_item_color("yellow", "Medium Battery (20–50%)"))
        main_layout.addWidget(self._create_legend_item_color("green", "High Battery (> 50%)"))

        # Stretch at the end to push items to the left
        main_layout.addStretch(1)

    def _create_legend_item_color(self, color, text):
        """
        Creates a small horizontal container with:
          - A colored circle
          - A descriptive label
        """
        container = QWidget()
        row_layout = QHBoxLayout(container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        icon_label = QLabel()
        icon_label.setFixedSize(18, 18)
        icon_label.setStyleSheet(
            f"background-color: {color}; "
            "border-radius: 9px; "  # circle shape
            "border: 1px solid black;"
        )

        text_label = QLabel(text)
        text_label.setStyleSheet("color: white;")  # White text on black background

        row_layout.addWidget(icon_label)
        row_layout.addWidget(text_label)
        return container


class NestGeoMapLegendOverlayWidget(QWidget):
    """
    Composite widget that:
      - Contains a NestGeoMapWidget (the QWebEngine map)
      - Overlays a BuoyLegendWidget at the bottom
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1) The QWebEngine-based map widget
        self.map_view = NestGeoMapWidget(self)
        self.map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 2) The overlay legend panel
        self.legend_panel = BuoyLegendWidget(self)
        self.legend_panel.setFixedHeight(60)  # Adjust as needed

        # We do not use a standard layout here, because we want the legend
        # to overlay the map. Instead, we’ll position them in resizeEvent.

    def resizeEvent(self, event):
        """
        Manually size and position the map to fill the entire widget,
        and place the legend at the bottom, spanning the same width.
        """
        super().resizeEvent(event)
        w = self.width()
        h = self.height()

        # The map fills all available space
        self.map_view.setGeometry(0, 0, w, h)

        # The legend overlays the bottom
        legend_height = self.legend_panel.height()
        self.legend_panel.setGeometry(0, h - legend_height, w, legend_height)

def add_external_js(map_object, js_file_path):
    """
    Reads an external JavaScript file, renders it as a Jinja2 template with the
    map instance variable, and injects the resulting script into the map's header.
    """
    if os.path.exists(js_file_path):
        with open(js_file_path, "r", encoding="utf-8") as f:
            js_raw = f.read()
        template = Template(js_raw)
        rendered_js = template.render(map_instance=map_object.get_name())
        script_element = Element(f"<script>{rendered_js}</script>")
        map_object.get_root().header.add_child(script_element)
        print(f"✅ Injected external JavaScript: {js_file_path}")
    else:
        print(f"❌ ERROR: JavaScript file not found at {js_file_path}")
    return map_object

def get_html_map():
    """Generates an HTML map using Folium and injects external JavaScript for marker events."""
    folium_map = setup_map()

    # Inject external JavaScript; note that the JS file should use our custom URL scheme.
    js_path = "NestUi/Utils/js/mapInteractions.js"  # Adjust the path as needed.
    folium_map = add_external_js(folium_map, js_path)

    markers = get_buoys_from_db()
    for marker in markers:
        marker.add_to(folium_map)

    # Generate HTML string from the map.
    map_html = folium_map._repr_html_()

    # Define the file path and create directory if it doesn't exist.
    file_name = "NestUi/Gui/map_dep/clickable_map.html"
    directory = os.path.dirname(file_name)
    os.makedirs(directory, exist_ok=True)

    # Write the map HTML to the file.
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(map_html)
    print(f"✅ Clickable map saved to {os.path.abspath(file_name)}")

    return map_html