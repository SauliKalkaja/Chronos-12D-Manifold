import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from engine_6D_ocean import OceanManifold6D

# This finds where the script is currently located
base_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Setup the Output Directory
output_dir = "el_nino_ocean"
os.makedirs(output_dir, exist_ok=True)

# 2. Load the CMEMS Deep Ocean Data using Dask Chunks
print("Loading NetCDF Data via Dask...")
file_path = os.path.join(base_dir, 'elnino_2015_calib.nc')
# chunks={'time': 10} tells Python to only load 10 frames into RAM at once!
ds = xr.open_dataset(file_path, chunks={'time': 10})

lats = ds['latitude'].values
lons = ds['longitude'].values
num_time_steps = len(ds['time'])

# 3. Initialize the 6D Symplectic Ocean Engine
print("Igniting 6D Ocean Manifold Engine...")
engine = OceanManifold6D()

print(f"Found {num_time_steps} frames of data. Beginning analytical sweep...")

# 4. Loop Through Every Frame
for i in range(num_time_steps):
    # Extract the timestamp 
    raw_time = str(ds['time'].isel(time=i).values)
    clean_time = raw_time[:13].replace('T', ' ') + ":00" 
    
    print(f"Processing Frame {i+1}/{num_time_steps} - {clean_time}")
    
    # Grab the Temperature and Salinity for this specific frame
    T_raw = ds['thetao'].isel(time=i).compute().values
    S_raw = ds['so'].isel(time=i).compute().values

    # IRONCLAD 2D ENFORCER:
    # If Copernicus gave us a 3D block (Depth, Lat, Lon), strictly grab the first depth layer [0, :, :]
    if len(T_raw.shape) == 3:
        T = T_raw[0, :, :]
        S = S_raw[0, :, :]
    else:
        T = T_raw.squeeze()
        S = S_raw.squeeze()

    # Execute the Math
    alpha_matrix = engine.calculate_metric_condensation(T, S)
    metric_shear = engine.calculate_metric_shear(alpha_matrix)
    
    # Calculate the dynamic threshold for the ocean's metric stress
    current_max = np.nanmax(metric_shear)
    print(f"      -> Max Ocean Shear: {current_max:.6f}")
    
    # Dynamically trigger the flip zone at 80% of the maximum stress
    flip_zones = engine.find_manifold_flips(metric_shear, threshold=(current_max * 0.8))

    # Visualize the Results
    fig = plt.figure(figsize=(14, 6)) 
    
    # Move the camera to point at the Equatorial Pacific (El Nino region)
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_extent([140, 280, -25, 25], crs=ccrs.PlateCarree()) 

    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='white')
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='white')
    ax.add_feature(cfeature.LAND, facecolor='black') 

    # Plot the Metric Shear (Auto-scaled colors!)
    shear_plot = ax.contourf(lons, lats, metric_shear, levels=20, 
                             transform=ccrs.PlateCarree(), cmap='magma', extend='max')

    plt.colorbar(shear_plot, label=r'Thermocline Metric Shear Magnitude ($|| \nabla \alpha ||$)')

    # Overlay the Flip Zones (Where the deep heat breaches the geometric limit)
    ax.contour(lons, lats, flip_zones, levels=[0.5], 
               transform=ccrs.PlateCarree(), colors='cyan', linewidths=2)

    plt.title(f"6D Symplectic Manifold: Equatorial Pacific (El Niño Monitor)\nTimestamp: {clean_time} UTC\nCyan Outlines = Thermocline Manifold Flips")

    # Save the frame
    filename = f"{output_dir}/frame_{i:03d}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
    
    plt.close(fig)

print(f"Sweep complete! All frames saved to the '{output_dir}' folder.")