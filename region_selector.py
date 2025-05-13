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
        self.root.geometry("600x400")
        
        # Set base paths
        self.base_dir = Path(__file__).parent
        self.tile_proc_dir = self.base_dir / "tile-proc"
        self.tiles_dir = self.base_dir / "tiles"
        
        # Load regions
        with open(self.tile_proc_dir / "regions.json", "r") as f:
            self.regions = json.load(f)
        
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
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Process Selected Regions", command=self.process_regions)
        self.process_btn.grid(row=4, column=0, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
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

if __name__ == "__main__":
    root = tk.Tk()
    app = RegionSelector(root)
    root.mainloop() 