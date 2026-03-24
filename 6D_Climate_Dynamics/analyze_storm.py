import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from engine_6D_climate import FluidManifold6D

# 1. Setup the Output Directory
output_dir = "hurricane_katrina"
os.makedirs(output_dir, exist_ok=True)

# 2. Load the ERA5 Winter Storm Data
print("Loading NetCDF Data...")
ds = xr.open_dataset('hurricane_katrina.nc')

ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180))
ds = ds.sortby('longitude')

lats = ds['latitude'].values
lons = ds['longitude'].values
num_time_steps = len(ds['valid_time'])

# 3. Initialize the 6D Symplectic Engine
print("Igniting 6D Manifold Engine...")
engine = FluidManifold6D()

print(f"Found {num_time_steps} hours of data. Beginning analytical sweep...")

# 4. Loop Through Every Hour
for i in range(num_time_steps):
    # Extract the timestamp to use in our title
    raw_time = str(ds['valid_time'].isel(valid_time=i).values)
    clean_time = raw_time[:13].replace('T', ' ') + ":00" # Formats to "YYYY-MM-DD HH:00"
    
    print(f"Processing Frame {i+1}/{num_time_steps} - {clean_time}")
    
    # Grab the Temp and Pressure for this specific hour
    T = ds['t2m'].isel(valid_time=i).values
    P = ds['sp'].isel(valid_time=i).values

    # Execute the Math
    alpha_matrix = engine.calculate_metric_condensation(T, P)
    metric_shear = engine.calculate_metric_shear(alpha_matrix)
    flip_zones = engine.find_manifold_flips(metric_shear, threshold=0.015)

    # Visualize the Results
    fig = plt.figure(figsize=(12, 8))
    # Move the camera to point at Florida/The Gulf of Mexico
    ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=-83, central_latitude=30))

    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.2)

    # Plot the Metric Shear
    # We set vmax=0.03 so the color scale doesn't jump around between frames
    shear_plot = ax.contourf(lons, lats, metric_shear, levels=20, 
                             transform=ccrs.PlateCarree(), cmap='magma', 
                             vmin=0, vmax=0.03, extend='max')

    plt.colorbar(shear_plot, label=r'Metric Shear Magnitude ($|| \nabla \alpha ||$)')

    # Overlay the Flip Zones
    ax.contour(lons, lats, flip_zones, levels=[0.5], 
               transform=ccrs.PlateCarree(), colors='cyan', linewidths=2)

    plt.title(f"6D Symplectic Manifold: Hurricane Katrina (2005)\nTimestamp: {clean_time} UTC\nCyan Outlines = Manifold Flip Zones (Cyclogenesis)")

    # Save the frame with leading zeros (e.g., frame_000.png, frame_001.png)
    filename = f"{output_dir}/frame_{i:03d}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    # CRITICAL: Close the figure to free up system memory
    plt.close(fig)

print(f"Sweep complete! All frames saved to the '{output_dir}' folder.")