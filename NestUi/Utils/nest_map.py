import geopandas as gpd
import requests
from shapely.geometry import Point

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

# def authenticate_er():
#     # Authenticate with EarthRanger
#     client = ERClient(
#         service_root="https://sandbox.pamdas.org/api/v1.0",
#         username="your_username",  # Replace with your username
#         password="your_password"   # Replace with your password
#     )
#     print("Authentication successful.")
#     return client

# def fetch_er_data(client):
#     # Fetch data from EarthRanger (e.g., recent events or assets with coordinates)
#     response = client.get("events", params={"limit": 100})  # Adjust parameters as needed
#     if response.status_code == 200:
#         events = response.json()
#         print(f"Fetched {len(events['results'])} events.")
#         return events['results']
#     else:
#         print(f"Failed to fetch data. Status code: {response.status_code}")
#         return []

# def process_er_data(events):
#     # Convert EarthRanger events into a GeoDataFrame
#     features = []
#     for event in events:
#         if 'geometry' in event and event['geometry']['type'] == 'Point':
#             coord = event['geometry']['coordinates']
#             features.append({
#                 'name': event['type']['name'],  # Example: Use event type as the name
#                 'geometry': gpd.points_from_xy([coord[0]], [coord[1]])[0]
#             })

#     gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
#     return gdf

def get_earthranger_data():
    """Fetch data from EarthRanger API and return as a GeoDataFrame."""
    # Replace with your EarthRanger API credentials and token
    BASE_URL = "https://ropeless-sandbox.pamdas.org/api/v1.0/activity/events"
    TOKEN = "duNL2uc2O4DNRBCQNu9swRO5OofEaxFa"  # Replace with your long-lived OAuth2 token

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accpet": "application/json",
        "Content-Disposition": "attachment; filename={}",
        "Content-Type": "application/json"
    }

    try:
        # Make the GET request to fetch events
        response = requests.get(BASE_URL, headers=headers)
        print("Status Code:", response.status_code)

        # Handle errors in response
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return gpd.GeoDataFrame()

        # Parse JSON data
        events = response.json()

        # Extract events with valid geometry
        features = []
        for event in events.get('results', []):  # Adjust based on API's pagination structure
            location = event.get("location")
            if location and "latitude" in location and "longitude" in location:
                features.append({
                    "event_type": event.get("event_type", "Unknown"),
                    "time": event.get("time"),
                    "priority": event.get("priority", None),
                    "geometry": Point(location["longitude"], location["latitude"])
                })

        # Convert to GeoDataFrame
        if features:
            gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
            return gdf
        else:
            print("No valid geometries found in the data.")
            return gpd.GeoDataFrame()

    except Exception as e:
        print("Error fetching data:", str(e))
        return gpd.GeoDataFrame()