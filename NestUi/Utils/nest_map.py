import requests
import socket
from pyqtlet2 import L
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
    """Fetch data from EarthRanger API and return as a list of markers."""
    if not is_connected():
        print("No internet connection. Please connect and try again.")
        return []

    BASE_URL = "https://buoy.pamdas.org/api/v1.0/gear/"
    TOKEN = "CVuqlvvFPsTkZ9nVlrk3o0kMY59MxC"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
    }

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
            return []

        data = response.json()
        markers = []

        for item in data.get('results', []):
            location = item.get("location")
            if location and isinstance(location, dict) and "latitude" in location and "longitude" in location:
                marker = L.marker(
                    [location["latitude"], location["longitude"]],
                    {
                        'buoy_id': item.get("id"),
                        'title': item.get("subject", "Unknown"),
                        'color': 'green'  # Default color for EarthRanger buoys
                    }
                )
                markers.append(marker)

        return markers

    except Exception as e:
        print("Error fetching data:", str(e))
        return []

def get_buoys_from_db():
    """Retrieve buoy records from the database and return as PyQtlet2 markers."""
    buoy_records = list_buoys()
    markers = []
    
    if not buoy_records:
        print("No buoys found in the database.")
        return markers

    for buoy in buoy_records:
        lat = buoy.lat
        lon = buoy.long
        buoy_id = buoy.buoy_id
        battery = getattr(buoy, 'battery', "N/A")
        drop_time = getattr(buoy, 'drop_time', "Unknown")

        # Determine icon color based on battery level
        try:
            battery_level = float(battery)
        except (ValueError, TypeError):
            battery_level = None

        if battery_level is not None:
            if battery_level <= 20:
                color = 'red'
            elif battery_level <= 50:
                color = 'yellow'
            else:
                color = 'green'
        else:
            color = 'green'

        # Create marker with color information
        marker = L.marker(
            [lat, lon],
            {
                'buoy_id': buoy_id,
                'title': f"Buoy ID: {buoy_id}\nBattery: {battery}\nDrop Time: {drop_time}",
                'color': color
            }
        )
        markers.append(marker)

    return markers