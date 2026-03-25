import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from engine_6D_ocean import OceanManifold6D
import warnings

# Suppress some standard xarray/dask warnings for clean output
warnings.filterwarnings('ignore')

base_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Load ALL files at once using the wildcard (*)
print("Stitching NetCDF files 1993-2026 via open_mfdataset...")
file_pattern = os.path.join(base_dir, 'elnino_decade_forecast*.nc')

# Use 'nested' to blindly stack the files without checking the timeline first
ds = xr.open_mfdataset(file_pattern, combine='nested', concat_dim='time', chunks={'time': 12})

# Force the timeline into chronological order and delete any overlapping duplicate months!
ds = ds.sortby('time')
ds = ds.drop_duplicates(dim='time')

num_time_steps = len(ds['time'])
print(f"Successfully stitched {num_time_steps} total months of data.")

print("Igniting 6D Ocean Manifold Engine for Timeseries Sweep...")
engine = OceanManifold6D()

dates = []
max_shear_values = []

# 2. Sweep through the decades
for i in range(num_time_steps):
    # Extract timestamp
    current_date = ds['time'].isel(time=i).values
    
    # Grab Temp and Salinity
    T_raw = ds['thetao'].isel(time=i).compute().values
    S_raw = ds['so'].isel(time=i).compute().values

    # IRONCLAD 2D ENFORCER
    if len(T_raw.shape) == 3:
        T = T_raw[0, :, :]
        S = S_raw[0, :, :]
    else:
        T = T_raw.squeeze()
        S = S_raw.squeeze()

    # Execute the Math
    alpha_matrix = engine.calculate_metric_condensation(T, S)
    metric_shear = engine.calculate_metric_shear(alpha_matrix)
    
    # Extract the absolute peak stress for this month (ignoring landmass NaNs)
    current_max_shear = np.nanmax(metric_shear)
    
    dates.append(current_date)
    max_shear_values.append(current_max_shear)

    # Print a progress update every year (12 months)
    if (i + 1) % 12 == 0 or i == num_time_steps - 1:
        year_str = str(current_date)[:4]
        print(f"  -> Processed through {year_str}... Current Peak Shear: {current_max_shear:.6f}")

# 3. Export to CSV for Deep Analysis
print("\nSweep Complete! Formatting data...")
import pandas as pd

# Create a clean data table
df = pd.DataFrame({
    'Date': dates,
    'Max_Metric_Shear': max_shear_values
})

# Save to CSV
csv_filename = "El_Nino_30Year_Shear_Data.csv"
df.to_csv(csv_filename, index=False)

print(f"Success! All raw data saved to: {csv_filename}")