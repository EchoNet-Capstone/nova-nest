import folium
from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Signal
from ..Utils.nest_map import *
import io
import os

class MapBridge(QObject):
    mapClicked = Signal(float, float)  # Signal with latitude and longitude

class NestGeoMapWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create QWebEngineView
        self.web_view = QWebEngineView()

        # Set up the communication bridge
        self.channel = QWebChannel()
        self.bridge = MapBridge()
        self.channel.registerObject("qtChannel", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Load the map HTML
        map_html = self.get_html_map()
        self.web_view.setHtml(map_html)

        # Connect the mapClicked signal to a slot
        self.bridge.mapClicked.connect(self.on_map_click)

        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def on_map_click(self, lat, lng):
        print(f"Map clicked at: Latitude {lat}, Longitude {lng}")

    def get_html_map(self):
        # Fetch data from EarthRanger
        gdf = get_earthranger_data()

        # Create a folium map
        folium_map = folium.Map(location=[0, 0], zoom_start=2)

        # Add points to the map
        for _, row in gdf.iterrows():
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup=row.get('name', 'No Name')
            ).add_to(folium_map)

        # Save the map to an HTML string
        map_html = folium_map._repr_html_()

        # Save to file for debugging or further use
        file_name = "map.html"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(map_html)
        print(f"Map HTML saved to {os.path.abspath(file_name)}")

        return map_html