import os
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QUrl
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

    """Custom QWebEnginePage to intercept JavaScript messages via URL changes."""
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() == "myapp":
            # Expecting a URL like: myapp://markerClicked?data=BUOY-123
            query = url.query()  # Should be "data=BUOY-123"
            if query.startswith("data="):
                buoy_id = query[5:]  # remove "data=" prefix
                # Decode any URL encoding:
                buoy_id = QUrl.fromPercentEncoding(buoy_id.encode("utf-8"))
                print(f"✅ Received Buoy ID from JS: {buoy_id}")
                # Call the parent's marker click handler
                self.parent().on_marker_click(buoy_id)
            return False  # Block navigation
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class NestGeoMapWidget(QWidget):
    """PySide6 Widget for displaying a Folium map in QWebEngineView without using WebChannel."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel("Marker clicks will appear here.")
        layout.addWidget(self.label)

        # Create QWebEngineView with custom page
        self.web_view = QWebEngineView()
        self.web_page = WebEnginePage(self)
        self.web_view.setPage(self.web_page)

        # Write the HTML map to disk and load it as a file URL
        map_html = get_html_map()  # This writes "clickable_map.html" to disk.
        self.web_view.setHtml(map_html)
        layout.addWidget(self.web_view)

    def on_marker_click(self, buoy_id):
        """Slot called when a marker is clicked in JavaScript."""
        print(f"✅ Buoy Marker Clicked: {buoy_id}")
        self.label.setText(f"Marker clicked: {buoy_id}")

def add_external_js(map_object, js_file_path):
    """
    Reads an external JavaScript file, renders it as a Jinja2 template with the
    map instance variable, and injects the resulting script into the map's header.
    """
    if os.path.exists(js_file_path):
        with open(js_file_path, "r", encoding="utf-8") as f:
            js_raw = f.read()
        template = Template(js_raw)
        print(map_object.get_name())
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

    # Write the map HTML to disk so that all resources load correctly.
    map_html = folium_map._repr_html_()
    file_name = "clickable_map.html"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(map_html)
    print(f"✅ Clickable map saved to {os.path.abspath(file_name)}")

    return map_html