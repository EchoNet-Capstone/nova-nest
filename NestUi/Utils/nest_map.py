import geopandas as gpd
import requests
import socket
from shapely.geometry import Point
from offline_folium import offline
import folium
from folium.plugins import MarkerCluster, BeautifyIcon
from ..Utils.nest_db import *


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

def get_buoys(lat=39.7749, lon=-120.4194, state=None, updated_since=None, page=1, page_size=25):
    """Fetch data from EarthRanger API and return as a GeoDataFrame."""
    if not is_connected():
        print("No internet connection. Please connect and try again.")
        return gpd.GeoDataFrame()

    BASE_URL = "https://buoy.pamdas.org/api/v1.0/gear/"
    TOKEN = "CVuqlvvFPsTkZ9nVlrk3o0kMY59MxC"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
    }

    # Construct query parameters
    params = {
        "lat": lat,
        "lon": lon,
        "page": page,
        "page_size": page_size,
    }
    if state:
        params["state"] = state
    if updated_since:
        params["updated_since"] = updated_since

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        print("Status Code:", response.status_code)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return gpd.GeoDataFrame()

        data = response.json()
        features = []

        for item in data.get('results', []):
            location = item.get("location")
            if location and isinstance(location, dict) and "latitude" in location and "longitude" in location:
                features.append({
                    "id": item.get("id"),
                    "subject": item.get("subject", "Unknown"),
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
      - ClickForLatLng plugin to copy coordifnates to the clipboard.
    
    The ClickForLatLng plugin is configured with a format string that outputs 
    the coordinates as a list (e.g., [lat, lng]) and with alert=True.
    """
    # Center map at a default location (e.g., [0, 0]). Adjust zoom as needed.
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    return m

def add_events_to_map(m, gdf):
    if gdf.empty:
        print("No buoys to add to the map.")
        return

    marker_cluster = MarkerCluster().add_to(m)  # Cluster markers to optimize rendering

    for _, row in gdf.iterrows():
        buoy_id = row.get("id", "Unknown")
        lat, lng = row.geometry.y, row.geometry.x

        popup_text = f"Buoy ID: {buoy_id}"

        # Create a marker with a beautified icon
        icon = BeautifyIcon(
            icon='info-sign', 
            border_color='#00ABDC', 
            text_color='#00ABDC', 
            background_color='white'
        )
        marker = folium.Marker(
            location=[lat, lng],
            popup=popup_text,
            icon=icon
        )

        marker.add_to(marker_cluster)

    return m

def get_buoys_from_db():
    # Retrieve buoy records from the database via Prisma.
    # list_buoys() is decorated to run synchronously.
    buoy_records = list_buoys()
    
    markers = []
    if not buoy_records:
        print("No buoys found in the database.")
        return markers

    for buoy in buoy_records:
        # Access attributes using dot notation
        lat = buoy.lat
        lon = buoy.long  # Assuming the attribute name is 'long'
        buoy_id = buoy.buoy_id
        battery = getattr(buoy, 'battery', "N/A")
        drop_time = getattr(buoy, 'drop_time', "Unknown")
        
        popup_text = (
            f"Buoy ID: {buoy_id}<br>"
            f"Battery: {battery}<br>"
            f"Drop Time: {drop_time}"
        )

        # Create a beautified icon for buoy markers
        icon = BeautifyIcon(
            icon='info-sign', 
            border_color='green', 
            text_color='green', 
            background_color='white'
        )

        marker = folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            tooltip="Click for details",
            icon=icon
        )
        markers.append(marker)

    return markers