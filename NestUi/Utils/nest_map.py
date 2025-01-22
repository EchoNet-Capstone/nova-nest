import geopandas
import contextily as ctx
import matplotlib.pyplot as plt
import os
import zipfile
import geopandas as gpd
# Download the ZIP file
import requests

# find maps here
def get_map():
    # Load the Pacific Coast by Virginia dataset using geodatasets
    gdf = geopandas.read_file(download_map())

    # Filter for the Pacific Coast by Virginia
    #pacific_coast = gdf[gdf["name"].str.contains("Virginia", na=False)]
    #pacific_coast = pacific_coast.to_crs(epsg=3857)
    #pacific_coast.plot(ax=self.ax, alpha=0.5, edgecolor="k")
    
    m = gdf.explore(
        color="red",  # use red color on all points
        marker_kwds=dict(radius=5, fill=True),  # make marker radius 10px with fill
    )

    return m  # return gdf map object

def download_map():
    # Step 1: Download the dataset
    url = "https://naciscdn.org/naturalearth/110m/physical/ne_110m_lakes.zip"
    zip_path = "ne_110m_lakes.zip"

    

    response = requests.get(url)
    if response.status_code == 200:
        with open(zip_path, "wb") as file:
            file.write(response.content)
        print("Dataset downloaded successfully.")
    else:
        print(f"Failed to download dataset. Status code: {response.status_code}")
        exit()

    # Step 2: Unzip the dataset
    extract_dir = "lakes_data"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Dataset extracted to: {extract_dir}")

    # Step 3: Find the shapefile path
    # Look for .shp file
    shapefile_path = None
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".shp"):
                shapefile_path = os.path.join(root, file)
                break

    if shapefile_path:
        print(f"Shapefile path: {shapefile_path}")
    else:
        print("Shapefile not found.")
        exit()
    return shapefile_path;