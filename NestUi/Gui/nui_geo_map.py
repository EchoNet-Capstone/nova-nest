import os
from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QGridLayout, QLabel
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtCore import Qt, Signal, QUrl
from folium import Element, Map
from jinja2 import Template
from ..Utils.nest_map import *  # Replace with your actual import

# --------------------------------------------------------------------
# Custom WebEnginePage to capture JS marker clicks
# --------------------------------------------------------------------
class WebEnginePage(QWebEnginePage):
    marker_clicked = Signal(str)
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        if msg.startswith("markerClicked:"):
            buoy_id = msg.split("markerClicked:")[1]
            print(f"✅ Received Buoy ID from JS: {buoy_id}")
            self.marker_clicked.emit(buoy_id)
        else:
            print(f"JavaScript Console [{level}]: {msg}")

# --------------------------------------------------------------------
# Main Map Widget
# --------------------------------------------------------------------
class NestGeoMapWidget(QWebEngineView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.web_page = WebEnginePage(self)

        self.setPage(self.web_page)
        self.load(QUrl.fromLocalFile(get_html_map()))
        self.page().settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

# --------------------------------------------------------------------
# Custom Legend Widget as a QFrame
# --------------------------------------------------------------------
class CustomBuoyLegendWidget(QFrame):
    """
    Desired Legend layout (single border, one horizontal line after header,
    one vertical line separating columns):

    +------------------------------------------------------------------+
    | LEGEND                                                           |
    |------------------------------------------------------------------|
    | [Blue Box] My Ship           | [Green Circle] Good               |
    | [Black Circle] Selected BuRD | [Yellow Circle] Battery Below 50% |
    |                              | [Red Circle] Battery Below 20%    |
    +------------------------------------------------------------------+

    The whole legend box now has its own white background and a single
    border. No extra borders around individual rows or cells.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set an outer border & white background
        # Increase the width so all text fits comfortably
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
        # Minimal spacing so we don’t see extra boxes around rows
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 2) Horizontal separator below header
        h_separator = QFrame()
        h_separator.setFrameShape(QFrame.HLine)
        # We make it a thin black line
        h_separator.setStyleSheet("""
            QFrame {
                background-color: black;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        h_separator.setFixedHeight(1)
        # Span all columns
        layout.addWidget(h_separator, 1, 0, 1, 1)

        # Helper function to create a thin vertical separator
        def vertical_separator():
            sep = QFrame()
            sep.setFrameShape(QFrame.VLine)
            sep.setStyleSheet("""
                QFrame {
                    background-color: black;
                    border: none;
                    margin: 0px;
                    padding: 0px;
                }
            """)
            sep.setFixedWidth(1)
            return sep
        
        layout.addWidget(vertical_separator(), 0, 1, 4, 1)

        # Row 1: Left: Legend Label; Right: [Green Circle] Good
        header_label = QLabel("Legend")
        header_label.setStyleSheet("border: none; padding-left: 6px; margin-right 6px; font-weight: bold; background: transparent;")
        layout.addWidget(header_label, 0, 0, alignment=Qt.AlignLeft)
        right_item_row0 = self._create_legend_item("green", "Good", shape="circle")
        layout.addWidget(right_item_row0, 0, 2, 2, 1, alignment=Qt.AlignLeft)

        # Row 2: Left: [Blue Box] My Ship; Right: [Yellow Circle] Battery Below 50%
        left_item_row2 = self._create_legend_item("blue", "My Ship", shape="square")
        right_item_row2 = self._create_legend_item("yellow", "Battery Below 50%", shape="circle")
        layout.addWidget(left_item_row2, 2, 0, alignment=Qt.AlignLeft)
        layout.addWidget(right_item_row2, 2, 2, alignment=Qt.AlignLeft)

        # Row 3: Left: [Black Circle] Selected BuRD; Right: [Red Circle] Battery Below 20%
        left_item_row3 = self._create_legend_item("black", "Selected BuRD", shape="circle")
        layout.addWidget(left_item_row3, 3, 0, alignment=Qt.AlignLeft)
        right_item_row3 = self._create_legend_item("red", "Battery Below 20%", shape="circle")
        layout.addWidget(right_item_row3, 3, 2, alignment=Qt.AlignLeft)

        # Row 4: Left is empty; 


    def _create_legend_item(self, color, text, shape="circle"):
        """
        Creates a horizontal container with:
          - A small colored shape (circle or square)
          - A text label
        """
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(6, 0, 0, 0)
        h_layout.setSpacing(0)

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        # No border around the shape
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
    """
    Displays the Folium map and overlays the legend at the bottom left.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.map_view = NestGeoMapWidget(self)

        self.legend_panel = CustomBuoyLegendWidget(self)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()
        self.map_view.setGeometry(0, 0, w, h)

        legend_width = self.legend_panel.width()
        legend_height = self.legend_panel.height()
        # Position the legend at the bottom-left corner
        self.legend_panel.setGeometry(0, h - legend_height, legend_width, legend_height)
        return super().resizeEvent(event)

# --------------------------------------------------------------------
# Helper Functions for Folium Map
# --------------------------------------------------------------------
def add_external_js(map_object:Map, js_file_path):
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
    folium_map = setup_map()
    js_path = "NestUi/Utils/js/mapInteractions.js"  # Adjust path if needed
    folium_map = add_external_js(folium_map, js_path)
    markers = get_buoys_from_db()
    for marker in markers:
        marker.add_to(folium_map)

    folium_map.get_root().height = "100%"

    file_name = os.getcwd() + "/NestUi/Gui/map_dep/clickable_map.html"
    directory = os.path.dirname(file_name)
    os.makedirs(directory, exist_ok=True)
    folium_map.save(file_name)

    print(f"✅ Clickable map saved to {os.path.abspath(file_name)}")
    return file_name
