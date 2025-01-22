from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from ..Utils.nest_map import *
# Save the map HTML to an in-memory string
import io

class GeoMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the layout
        layout = QVBoxLayout()

        # Create a QWebEngineView for displaying interactive maps
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Set the layout
        self.setLayout(layout)

        # Render the map
        self.display_map()

    def display_map(self):
        """
        Generates a folium map using the provided get_map_path_function and displays it in the QWebEngineView.
        """
        # Call the function to get the gdf map
        gdf = get_map()
        
        html_file = io.BytesIO()
        gdf.save(html_file, close_file=False)
        html_file.seek(0)

        # Load the HTML map into the QWebEngineView
        self.web_view.setHtml(html_file.getvalue().decode())    