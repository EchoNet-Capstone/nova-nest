#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import shutil
import platform
from pathlib import Path
import time
import requests
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster
from datetime import datetime
from NestUi.Utils.nest_db import create_buoy, list_buoys

class EarthRangerClient:
    def __init__(self):
        self.base_url = "https://buoy.pamdas.org/api/v1.0/gear/"
        self.token = "CVuqlvvFPsTkZ9nVlrk3o0kMY59MxC"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def get_buoys(self, lat, lon, state="deployed", page=1, page_size=100):
        params = {
            "lat": lat,
            "lon": lon,
            "state": state,
            "page": page,
            "page_size": page_size
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching buoys: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception while fetching buoys: {str(e)}")
            return None

class SetupWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Setup Progress")
        self.window.geometry("400x300")
        
        # Create text widget for output
        self.text = tk.Text(self.window, wrap=tk.WORD, height=15)
        self.text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.text, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
    def add_text(self, text):
        self.text.insert(tk.END, text + "\n")
        self.text.see(tk.END)
        self.window.update()

class LogHandler:
    def __init__(self, setup_window):
        self.setup_window = setup_window
    
    def write(self, data):
        if data.strip():
            self.setup_window.add_text(data.strip())
    
    def flush(self):
        pass

class RegionSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova Nest Region Selector")
        self.root.geometry("800x600")  # Increased window size
        
        # Initialize EarthRanger client
        self.earthranger = EarthRangerClient()
        
        # Set base paths
        self.base_dir = Path(__file__).parent
        self.tile_proc_dir = self.base_dir / "tile-proc"
        self.tiles_dir = self.base_dir / "tiles"
        
        # Load regions
        with open(self.tile_proc_dir / "regions.json", "r") as f:
            self.regions = json.load(f)
            
        # Helper function to calculate offshore points
        def get_offshore_points(coastal_points, nautical_miles=5):
            """
            Calculate points 5 nautical miles offshore from coastal points.
            Uses a simple approximation: 1 nautical mile ≈ 0.0167 degrees
            """
            offshore_points = []
            for point in coastal_points:
                # Calculate offshore point (assuming ocean is to the west for US West Coast)
                if point.get("region") == "west_coast":
                    offshore_points.append({
                        "lat": point["lat"],
                        "lon": point["lon"] - (nautical_miles * 0.0167)
                    })
                # For East Coast, ocean is to the east
                elif point.get("region") == "east_coast":
                    offshore_points.append({
                        "lat": point["lat"],
                        "lon": point["lon"] + (nautical_miles * 0.0167)
                    })
                # For other regions, we'll need to determine direction based on location
                else:
                    # Default to west for now, but this should be customized per region
                    offshore_points.append({
                        "lat": point["lat"],
                        "lon": point["lon"] - (nautical_miles * 0.0167)
                    })
            return offshore_points

        # Define coastal points for each region
        coastal_points = {
            "washington": [
                {"lat": 48.7519, "lon": -122.4787, "region": "west_coast"},  # Bellingham
                {"lat": 47.6062, "lon": -122.3321, "region": "west_coast"},  # Seattle
                {"lat": 47.2529, "lon": -122.4443, "region": "west_coast"},  # Tacoma
                {"lat": 46.9795, "lon": -123.8154, "region": "west_coast"},  # Aberdeen
                {"lat": 48.1171, "lon": -123.4307, "region": "west_coast"},  # Port Angeles
                {"lat": 47.1136, "lon": -124.1636, "region": "west_coast"},  # Ocean Shores
                {"lat": 48.5371, "lon": -123.1019, "region": "west_coast"},  # Port Townsend
                {"lat": 47.1129, "lon": -122.9665, "region": "west_coast"},  # Olympia
                {"lat": 46.3007, "lon": -124.0518, "region": "west_coast"},  # Long Beach
                {"lat": 48.5371, "lon": -123.1019, "region": "west_coast"}   # Anacortes
            ],
            "oregon": [
                {"lat": 46.1912, "lon": -123.8145, "region": "west_coast"},  # Astoria
                {"lat": 45.5231, "lon": -122.6765, "region": "west_coast"},  # Portland
                {"lat": 44.0521, "lon": -124.0840, "region": "west_coast"},  # Florence
                {"lat": 43.3665, "lon": -124.2179, "region": "west_coast"},  # Coos Bay
                {"lat": 42.4412, "lon": -124.4195, "region": "west_coast"},  # Brookings
                {"lat": 44.6368, "lon": -124.0535, "region": "west_coast"},  # Newport
                {"lat": 45.7079, "lon": -123.9389, "region": "west_coast"},  # Tillamook
                {"lat": 43.3417, "lon": -124.2179, "region": "west_coast"},  # Bandon
                {"lat": 42.0526, "lon": -124.2839, "region": "west_coast"},  # Gold Beach
                {"lat": 45.5946, "lon": -123.9429, "region": "west_coast"}   # Garibaldi
            ],
            "california": [
                {"lat": 41.7557, "lon": -124.2026, "region": "west_coast"},  # Crescent City
                {"lat": 40.8021, "lon": -124.1637, "region": "west_coast"},  # Eureka
                {"lat": 38.4404, "lon": -123.1001, "region": "west_coast"},  # Fort Bragg
                {"lat": 37.7749, "lon": -122.4194, "region": "west_coast"},  # San Francisco
                {"lat": 34.0522, "lon": -118.2437, "region": "west_coast"},  # Los Angeles
                {"lat": 32.7157, "lon": -117.1611, "region": "west_coast"},  # San Diego
                {"lat": 36.9741, "lon": -122.0308, "region": "west_coast"},  # Santa Cruz
                {"lat": 34.4208, "lon": -119.6982, "region": "west_coast"},  # Santa Barbara
                {"lat": 33.6846, "lon": -118.0169, "region": "west_coast"},  # Long Beach
                {"lat": 33.1581, "lon": -117.3506, "region": "west_coast"},  # Oceanside
                {"lat": 38.2919, "lon": -123.0151, "region": "west_coast"},  # Point Arena
                {"lat": 39.4457, "lon": -123.8053, "region": "west_coast"},  # Mendocino
                {"lat": 36.6177, "lon": -121.9166, "region": "west_coast"},  # Monterey
                {"lat": 35.2828, "lon": -120.6596, "region": "west_coast"},  # San Luis Obispo
                {"lat": 33.1959, "lon": -117.3795, "region": "west_coast"}   # Carlsbad
            ],
            "maine": [
                {"lat": 44.3876, "lon": -68.2039, "region": "east_coast"},   # Bar Harbor
                {"lat": 43.6615, "lon": -70.2553, "region": "east_coast"},   # Portland
                {"lat": 44.8012, "lon": -66.9639, "region": "east_coast"},   # Eastport
                {"lat": 44.3894, "lon": -68.2044, "region": "east_coast"},   # Acadia
                {"lat": 43.9137, "lon": -69.8206, "region": "east_coast"},   # Boothbay
                {"lat": 44.3923, "lon": -68.2041, "region": "east_coast"},   # Mount Desert
                {"lat": 43.8521, "lon": -69.6306, "region": "east_coast"},   # Bath
                {"lat": 44.1034, "lon": -69.1089, "region": "east_coast"},   # Rockland
                {"lat": 44.5354, "lon": -67.6074, "region": "east_coast"},   # Machias
                {"lat": 44.3923, "lon": -68.2041, "region": "east_coast"}    # Southwest Harbor
            ],
            "british-columbia": [
                {"lat": 48.4284, "lon": -123.3656, "region": "west_coast"},  # Victoria
                {"lat": 49.2827, "lon": -123.1207, "region": "west_coast"},  # Vancouver
                {"lat": 50.7211, "lon": -127.4197, "region": "west_coast"},  # Port Hardy
                {"lat": 54.3158, "lon": -130.3211, "region": "west_coast"},  # Prince Rupert
                {"lat": 52.1609, "lon": -128.1447, "region": "west_coast"},  # Bella Bella
                {"lat": 49.6897, "lon": -124.9937, "region": "west_coast"},  # Comox
                {"lat": 50.1107, "lon": -125.2737, "region": "west_coast"},  # Campbell River
                {"lat": 53.2547, "lon": -129.1197, "region": "west_coast"},  # Kitimat
                {"lat": 51.6417, "lon": -127.5807, "region": "west_coast"},  # Bella Coola
                {"lat": 49.1527, "lon": -123.9167, "region": "west_coast"},  # Nanaimo
                {"lat": 48.7747, "lon": -123.7087, "region": "west_coast"},  # Salt Spring Island
                {"lat": 49.3217, "lon": -124.3117, "region": "west_coast"},  # Parksville
                {"lat": 50.6877, "lon": -127.4197, "region": "west_coast"},  # Port McNeill
                {"lat": 52.1609, "lon": -128.1447, "region": "west_coast"},  # Ocean Falls
                {"lat": 53.2547, "lon": -129.1197, "region": "west_coast"}   # Hartley Bay
            ],
            "nova-scotia": [
                {"lat": 44.6488, "lon": -63.5752, "region": "east_coast"},   # Halifax
                {"lat": 45.1972, "lon": -61.3485, "region": "east_coast"},   # Canso
                {"lat": 43.8525, "lon": -66.1177, "region": "east_coast"},   # Yarmouth
                {"lat": 46.1368, "lon": -60.1942, "region": "east_coast"},   # Sydney
                {"lat": 45.6159, "lon": -61.3642, "region": "east_coast"},   # Port Hawkesbury
                {"lat": 44.6682, "lon": -63.5752, "region": "east_coast"},   # Dartmouth
                {"lat": 45.0715, "lon": -64.4545, "region": "east_coast"},   # Wolfville
                {"lat": 43.8256, "lon": -65.3236, "region": "east_coast"},   # Shelburne
                {"lat": 45.6159, "lon": -61.3642, "region": "east_coast"},   # Strait Area
                {"lat": 44.6682, "lon": -63.5752, "region": "east_coast"},   # Eastern Shore
                {"lat": 45.0715, "lon": -64.4545, "region": "east_coast"},   # Annapolis Valley
                {"lat": 43.8256, "lon": -65.3236, "region": "east_coast"},   # South Shore
                {"lat": 45.6159, "lon": -61.3642, "region": "east_coast"},   # Cape Breton
                {"lat": 44.6682, "lon": -63.5752, "region": "east_coast"},   # Halifax Regional
                {"lat": 45.0715, "lon": -64.4545, "region": "east_coast"}    # Fundy Shore
            ],
            "newfoundland-and-labrador": [
                {"lat": 47.5615, "lon": -52.7126, "region": "east_coast"},   # St. John's
                {"lat": 48.9485, "lon": -54.6109, "region": "east_coast"},   # Gander
                {"lat": 49.5895, "lon": -55.3214, "region": "east_coast"},   # Twillingate
                {"lat": 51.5834, "lon": -55.5312, "region": "east_coast"},   # St. Anthony
                {"lat": 47.5162, "lon": -59.1380, "region": "east_coast"},   # Port aux Basques
                {"lat": 48.9485, "lon": -54.6109, "region": "east_coast"},   # Gander Bay
                {"lat": 49.5895, "lon": -55.3214, "region": "east_coast"},   # Notre Dame Bay
                {"lat": 51.5834, "lon": -55.5312, "region": "east_coast"},   # White Bay
                {"lat": 47.5162, "lon": -59.1380, "region": "east_coast"},   # Bay of Islands
                {"lat": 48.9485, "lon": -54.6109, "region": "east_coast"},   # Bonavista Bay
                {"lat": 49.5895, "lon": -55.3214, "region": "east_coast"},   # Green Bay
                {"lat": 51.5834, "lon": -55.5312, "region": "east_coast"},   # Hare Bay
                {"lat": 47.5162, "lon": -59.1380, "region": "east_coast"},   # St. George's Bay
                {"lat": 48.9485, "lon": -54.6109, "region": "east_coast"},   # Trinity Bay
                {"lat": 49.5895, "lon": -55.3214, "region": "east_coast"}    # Notre Dame Bay
            ],
            "alaska": [
                {"lat": 58.3019, "lon": -134.4197, "region": "west_coast"},  # Juneau
                {"lat": 61.2181, "lon": -149.9003, "region": "west_coast"},  # Anchorage
                {"lat": 57.7900, "lon": -152.4072, "region": "west_coast"},  # Kodiak
                {"lat": 55.3422, "lon": -131.6461, "region": "west_coast"},  # Ketchikan
                {"lat": 64.8561, "lon": -147.8564, "region": "west_coast"},  # Fairbanks
                {"lat": 59.6498, "lon": -151.4881, "region": "west_coast"},  # Homer
                {"lat": 56.3920, "lon": -133.5957, "region": "west_coast"},  # Petersburg
                {"lat": 57.0531, "lon": -135.3300, "region": "west_coast"},  # Sitka
                {"lat": 58.3838, "lon": -134.1980, "region": "west_coast"},  # Douglas
                {"lat": 56.8519, "lon": -132.9557, "region": "west_coast"},  # Wrangell
                {"lat": 59.6498, "lon": -151.4881, "region": "west_coast"},  # Kenai
                {"lat": 56.3920, "lon": -133.5957, "region": "west_coast"},  # Craig
                {"lat": 57.0531, "lon": -135.3300, "region": "west_coast"},  # Angoon
                {"lat": 58.3838, "lon": -134.1980, "region": "west_coast"},  # Haines
                {"lat": 56.8519, "lon": -132.9557, "region": "west_coast"}   # Klawock
            ],
            "norway": [
                {"lat": 58.9700, "lon": 5.7331, "region": "north_sea"},     # Stavanger
                {"lat": 60.3913, "lon": 5.3221, "region": "north_sea"},     # Bergen
                {"lat": 63.4305, "lon": 10.3951, "region": "north_sea"},    # Trondheim
                {"lat": 69.6492, "lon": 18.9553, "region": "north_sea"},    # Tromsø
                {"lat": 70.6632, "lon": 23.6817, "region": "north_sea"},    # Hammerfest
                {"lat": 59.9139, "lon": 10.7522, "region": "north_sea"},    # Oslo
                {"lat": 58.1599, "lon": 8.0182, "region": "north_sea"},     # Kristiansand
                {"lat": 67.2804, "lon": 14.4050, "region": "north_sea"},    # Bodø
                {"lat": 59.7439, "lon": 10.2045, "region": "north_sea"},    # Drammen
                {"lat": 58.1599, "lon": 8.0182, "region": "north_sea"},     # Arendal
                {"lat": 67.2804, "lon": 14.4050, "region": "north_sea"},    # Narvik
                {"lat": 59.7439, "lon": 10.2045, "region": "north_sea"},    # Moss
                {"lat": 58.1599, "lon": 8.0182, "region": "north_sea"},     # Grimstad
                {"lat": 67.2804, "lon": 14.4050, "region": "north_sea"},    # Harstad
                {"lat": 59.7439, "lon": 10.2045, "region": "north_sea"}     # Fredrikstad
            ]
        }

        # Calculate offshore points for each region
        self.region_coordinates = {}
        for region, points in coastal_points.items():
            self.region_coordinates[region] = get_offshore_points(points)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Region selection
        ttk.Label(main_frame, text="Select Regions:").grid(row=0, column=0, sticky=tk.W)
        
        # Create listbox with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.region_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.region_listbox.yview)
        self.region_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.region_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Populate listbox
        for region in sorted(self.regions.keys()):
            self.region_listbox.insert(tk.END, region)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=2, column=0, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=10)
        
        # Process button
        self.process_btn = ttk.Button(button_frame, text="Process Selected Regions", command=self.process_regions)
        self.process_btn.grid(row=0, column=0, padx=5)
        
        # Fetch Buoys button
        self.fetch_buoys_btn = ttk.Button(button_frame, text="Fetch Buoys", command=self.fetch_buoys)
        self.fetch_buoys_btn.grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create map window
        self.map_window = None
    
    def make_executable(self, script_path):
        """Make a script executable if it exists."""
        if script_path.exists():
            os.chmod(str(script_path), 0o755)
            print(f"Made executable: {script_path}")
        else:
            print(f"Script not found: {script_path}")
    
    def get_script_name(self, base_name):
        """Get the appropriate script name based on OS."""
        if platform.system() == "Darwin":
            return f"{base_name}_mac"
        return base_name
    
    def update_progress(self, value, status):
        self.progress_var.set(value)
        self.status_var.set(status)
        self.root.update_idletasks()
    
    def process_regions(self):
        selected_indices = self.region_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one region")
            return
        
        selected_regions = [self.region_listbox.get(i) for i in selected_indices]
        
        # Disable button during processing
        self.process_btn.configure(state='disabled')
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_regions_thread, args=(selected_regions,))
        thread.daemon = True
        thread.start()
    
    def process_regions_thread(self, regions):
        try:
            # Make all scripts executable first
            self.update_progress(0, "Preparing scripts...")
            
            # Make setup and run scripts executable
            setup_script = self.base_dir / self.get_script_name("setup")
            run_script = self.base_dir / self.get_script_name("run")
            get_tiles_script = self.tile_proc_dir / self.get_script_name("get_tiles")
            
            print(f"Setup script path: {setup_script}")
            print(f"Run script path: {run_script}")
            print(f"Get tiles script path: {get_tiles_script}")
            
            self.make_executable(setup_script)
            self.make_executable(run_script)
            self.make_executable(get_tiles_script)
            
            # Process each region
            total_regions = len(regions)
            for i, region in enumerate(regions):
                progress = (i / total_regions) * 100
                self.update_progress(progress, f"Processing {region}...")
                
                # Check if mbtiles already exists
                mbtiles_file = self.tiles_dir / f"{region}.mbtiles"
                if mbtiles_file.exists():
                    self.update_progress(progress, f"Skipping {region} (already downloaded)...")
                    continue
                
                # Run get_tiles script for the region
                print(f"Running get_tiles script for {region}")
                subprocess.run([str(get_tiles_script), region], check=True, cwd=str(self.tile_proc_dir))
                
                # Move the mbtiles file to the tiles directory
                temp_mbtiles = self.tile_proc_dir / region / f"{region}.mbtiles"
                if temp_mbtiles.exists():
                    shutil.move(str(temp_mbtiles), str(mbtiles_file))
            
            self.update_progress(100, "Running setup script...")
            
            # Run setup script with timeout
            if setup_script.exists():
                print(f"Running setup script: {setup_script}")
                process = subprocess.Popen(
                    [str(setup_script)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=str(self.base_dir)
                )
                
                # Wait for 30 seconds
                start_time = time.time()
                while process.poll() is None:
                    if time.time() - start_time > 30:
                        process.terminate()
                        break
                    time.sleep(0.1)
                
                if process.returncode != 0 and process.returncode is not None:
                    raise subprocess.CalledProcessError(process.returncode, setup_script)
            else:
                print(f"Setup script not found: {setup_script}")
            
            self.update_progress(100, "Setup complete! Launching application...")
            
            # Run the application
            if run_script.exists():
                print(f"Running application: {run_script}")
                subprocess.run([str(run_script)], check=True, cwd=str(self.base_dir))
            else:
                print(f"Run script not found: {run_script}")
            
            messagebox.showinfo("Success", "Processing complete! Application launched.")
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.process_btn.configure(state='normal')
            self.update_progress(0, "Ready")

    def fetch_buoys(self):
        selected_indices = self.region_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one region")
            return
        
        selected_regions = [self.region_listbox.get(i) for i in selected_indices]
        
        # Disable buttons during processing
        self.process_btn.configure(state='disabled')
        self.fetch_buoys_btn.configure(state='disabled')
        
        # Start fetching in a separate thread
        thread = threading.Thread(target=self.fetch_buoys_thread, args=(selected_regions,))
        thread.daemon = True
        thread.start()

    def fetch_buoys_thread(self, regions):
        try:
            all_buoys = []
            stored_buoys = []
            
            for i, region in enumerate(regions):
                progress = (i / len(regions)) * 100
                self.update_progress(progress, f"Fetching buoys for {region}...")
                
                # Get region coordinates from our predefined coordinates
                region_coords_list = self.region_coordinates.get(region)
                if not region_coords_list:
                    print(f"No coordinates found for region: {region}")
                    continue
                
                # Fetch buoys for each coastal point in the region
                for coords in region_coords_list:
                    buoys_data = self.earthranger.get_buoys(
                        lat=coords["lat"],
                        lon=coords["lon"],
                        state="deployed"
                    )
                    
                    if buoys_data and "results" in buoys_data:
                        for buoy in buoys_data["results"]:
                            if "location" in buoy and "latitude" in buoy["location"] and "longitude" in buoy["location"]:
                                # Check if we already have this buoy (avoid duplicates)
                                buoy_id = buoy.get("id", "Unknown")
                                if not any(b["id"] == buoy_id for b in all_buoys):
                                    buoy_data = {
                                        "id": buoy_id,
                                        "subject": buoy.get("subject", "Unknown"),
                                        "lat": float(buoy["location"]["latitude"]),
                                        "lon": float(buoy["location"]["longitude"]),
                                        "battery": int(buoy.get("battery", 100)),  # Default to 100 if not provided
                                        "drop_time": datetime.now()  # Use current time as drop time
                                    }
                                    all_buoys.append(buoy_data)
                                    
                                    # Store buoy in database
                                    try:
                                        stored_buoy = create_buoy(
                                            lat=buoy_data["lat"],
                                            long_val=buoy_data["lon"],
                                            battery=buoy_data["battery"],
                                            drop_time=buoy_data["drop_time"]
                                        )
                                        stored_buoys.append(stored_buoy)
                                        print(f"Stored buoy {buoy_id} in database")
                                    except Exception as db_error:
                                        print(f"Error storing buoy {buoy_id} in database: {str(db_error)}")
            
            if all_buoys:
                self.show_buoys_map(all_buoys)
                messagebox.showinfo("Success", f"Found {len(all_buoys)} buoys and stored {len(stored_buoys)} in database")
            else:
                messagebox.showinfo("Info", "No buoys found in the selected regions")
            
        except Exception as e:
            print(f"Error fetching buoys: {str(e)}")
            messagebox.showerror("Error", f"An error occurred while fetching buoys: {str(e)}")
        finally:
            self.process_btn.configure(state='normal')
            self.fetch_buoys_btn.configure(state='normal')
            self.update_progress(0, "Ready")

    def show_buoys_map(self, buoys):
        # Create a new window for the map
        if self.map_window:
            self.map_window.destroy()
        
        self.map_window = tk.Toplevel(self.root)
        self.map_window.title("Buoy Locations")
        self.map_window.geometry("800x600")
        
        # Create a frame for the map
        map_frame = ttk.Frame(self.map_window)
        map_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the map
        m = folium.Map(location=[39.7749, -120.4194], zoom_start=5)
        
        # Add markers for each buoy
        marker_cluster = MarkerCluster().add_to(m)
        
        for buoy in buoys:
            popup_text = f"Buoy ID: {buoy['id']}<br>Subject: {buoy['subject']}"
            folium.Marker(
                location=[buoy['lat'], buoy['lon']],
                popup=popup_text,
                tooltip=f"Buoy {buoy['id']}"
            ).add_to(marker_cluster)
        
        # Save the map to a temporary HTML file
        temp_map_path = self.base_dir / "temp_map.html"
        m.save(str(temp_map_path))
        
        # Open the map in the default web browser
        import webbrowser
        webbrowser.open(f"file://{temp_map_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegionSelector(root)
    root.mainloop() 