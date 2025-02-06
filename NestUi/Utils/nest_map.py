import geopandas as gpd
import requests
import socket
from shapely.geometry import Point
import folium
from folium.plugins import MousePosition


########################################
# EarthRanger Data Functions
########################################

class EarthRangerClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = (username, password)

    def get_events(self, limit=100):
        endpoint = f"{self.base_url}/events"
        params = {"limit": limit}
        response = requests.get(endpoint, auth=self.auth, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch events. Status code: {response.status_code}")
            return {}

def is_connected():
    """Check if there is an active internet connection."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def get_earthranger_data():
    """Fetch data from EarthRanger API and return as a GeoDataFrame."""
    if not is_connected():
        print("No internet connection. Please connect and try again.")
        return gpd.GeoDataFrame()
    
    # Replace with your EarthRanger API credentials/token
    BASE_URL = "https://ropeless-sandbox.pamdas.org/api/v1.0/activity/events"
    TOKEN = "duNL2uc2O4DNRBCQNu9swRO5OofEaxFa"  # Replace with your OAuth2 token

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accpet": "application/json",
        "Content-Disposition": "attachment; filename={}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers)
        print("Status Code:", response.status_code)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return gpd.GeoDataFrame()
        
        events = response.json()
        features = []
        for event in events.get('results', []):
            location = event.get("location")
            if location and "latitude" in location and "longitude" in location:
                features.append({
                    "event_type": event.get("event_type", "Unknown"),
                    "time": event.get("time"),
                    "priority": event.get("priority", None),
                    "geometry": Point(location["longitude"], location["latitude"])
                })
        if features:
            gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
            return gdf
        else:
            print("No valid geometries found in the data.")
            return gpd.GeoDataFrame()
    except Exception as e:
        print("Error fetching data:", str(e))
        return gpd.GeoDataFrame()

########################################
# Map Setup and Plugin Integration
########################################

def setup_map():
    """
    Create and return a folium map with:
      - OpenStreetMap tile layer (with attribution)
      - MousePosition to display current coordinates
      - ClickForLatLng plugin to copy coordinates to the clipboard.
    
    The ClickForLatLng plugin is configured with a format string that outputs 
    the coordinates as a list (e.g., [lat, lng]) and with alert=True.
    """
    # Center map at a default location (e.g., [0, 0]). Adjust zoom as needed.
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    # Add OpenStreetMap layer (Default Street View)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)

    # Add CartoDB Positron (Light Street View)
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='CartoDB Positron'
    ).add_to(m)

    # Add Terrain layer (using OpenTopoMap as an alternative)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
        name='Terrain (OpenTopoMap)'
    ).add_to(m)

    # Add Satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite'
    ).add_to(m)

    # Add Hybrid layer (Satellite with labels)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Hybrid'
    ).add_to(m)

    # Add layer control to switch between layers
    folium.LayerControl().add_to(m)
    
    # Add MousePosition plugin
    MousePosition(
        position='bottomright',
        separator=', ',
        prefix='Coordinates:'
    ).add_to(m)
    
    # Add ClickForLatLng plugin. When the map is clicked, the coordinates are 
    m.add_child(
        folium.ClickForMarker()
    )
    
    return m

def add_events_to_map(m, gdf):
    """
    Add markers to the folium map for each event in the GeoDataFrame.
    Each marker's popup displays event type, time, and priority.
    """
    if gdf.empty:
        print("No events to add to the map.")
        return
    
    for row in gdf.iterrows():
        lat = row.geometry.y
        lng = row.geometry.x
        popup_text = (
            f"<strong>Event:</strong> {row.get('event_type', 'Unknown')}<br>"
            f"<strong>Time:</strong> {row.get('time', 'N/A')}<br>"
            f"<strong>Priority:</strong> {row.get('priority', 'N/A')}"
        )
        folium.Marker([lat, lng], popup=popup_text).add_to(m)