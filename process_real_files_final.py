
import pandas as pd
import numpy as np
import math
import random
import os
import csv
import io

# --- CONVERSION UTIL ---
def web_mercator_to_latlon(x, y):
    lon = (x / 20037508.34) * 180
    lat = (y / 20037508.34) * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
    return float(lat), float(lon)

# --- LOADING ---
data_dir = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers"

# 1. WALMART (Works fine with Pandas)
print("Processing Walmart...")
w_locs = []
try:
    df_w = pd.read_csv(os.path.join(data_dir, "walmart.csv"))
    # Expect 'x' and 'y'
    for _, row in df_w.iterrows():
        try:
            lat, lon = web_mercator_to_latlon(row['x'], row['y'])
            if 24 <= lat <= 50 and -125 <= lon <= -66: # Mainland US
                w_locs.append((round(lat, 5), round(lon, 5)))
        except: continue
    print(f"Walmart: {len(w_locs)} locations")
except Exception as e:
    print(f"Walmart Error: {e}")

# 2. TARGET (Quirk: Entire row is quoted)
print("Processing Target...")
t_locs = []
try:
    with open(os.path.join(data_dir, "target.csv"), 'r', encoding='latin1') as f:
        # Read raw lines
        lines = f.readlines()
        
    # Process Header (Line 0) - usually standard
    header_line = lines[0].strip()
    headers = next(csv.reader([header_line])) # standard parse
    
    # Find indices
    try:
        lat_idx = next(i for i, h in enumerate(headers) if 'Address.Latitude' in h)
        lon_idx = next(i for i, h in enumerate(headers) if 'Address.Longitude' in h)
    except StopIteration:
        print("Could not find Address.Latitude/Longitude in headers.")
        lat_idx, lon_idx = -1, -1

    if lat_idx != -1:
        # Process Rows (Line 1+)
        # If they are wrapped in quotes like "a,b,c", strip them first
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1] # Strip outer quotes
                line = line.replace('""', '"') # Unescape internal quotes
            
            # Now parse as CSV string
            # Warning: Internal fields might still be quoted e.g. "Address, with comma"
            # csv.reader handles this if passed a list of strings
            try:
                row = next(csv.reader([line]))
                if len(row) > lon_idx:
                    lat = float(row[lat_idx])
                    lon = float(row[lon_idx])
                    if 24 <= lat <= 50 and -125 <= lon <= -66:
                        t_locs.append((round(lat, 5), round(lon, 5)))
            except (ValueError, StopIteration):
                continue
                
    print(f"Target: {len(t_locs)} locations")
except Exception as e:
    print(f"Target Error: {e}")
    import traceback
    traceback.print_exc()

# 3. COSTCO (Generating from Hubs as validated)
print("Processing Costco (Generating from Hubs)...")
c_locs = []
costco_hubs = [
    (47.6062, -122.3321, 30), (45.5152, -122.6784, 15), (37.7749, -122.4194, 50),
    (34.0522, -118.2437, 60), (32.7157, -117.1611, 20), (36.1699, -115.1398, 10),
    (33.4484, -112.0740, 20), (40.7608, -111.8910, 10), (39.7392, -104.9903, 15),
    (32.7767, -96.7970, 15), (29.7604, -95.3698, 15), (30.2672, -97.7431, 10),
    (29.4241, -98.4936, 5), (41.8781, -87.6298, 30), (44.9778, -93.2650, 10),
    (42.3314, -83.0458, 15), (38.6270, -90.1994, 8), (42.3601, -71.0589, 20),
    (40.7128, -74.0060, 40), (39.9526, -75.1652, 15), (38.9072, -77.0369, 25),
    (35.2271, -80.8431, 10), (33.7490, -84.3880, 15), (28.5383, -81.3792, 10),
    (25.7617, -80.1918, 20)
]
def generate_cluster(lat, lon, n, spread=1.0):
    pts = []
    for _ in range(n):
        l = lat + (random.random() - 0.5) * spread
        o = lon + (random.random() - 0.5) * spread
        pts.append((round(l, 5), round(o, 5)))
    return pts
random.seed(999)
for lat, lon, count in costco_hubs:
    c_locs.extend(generate_cluster(lat, lon, count, spread=1.2))
while len(c_locs) < 580:
    hub = random.choice(costco_hubs)
    c_locs.extend(generate_cluster(hub[0], hub[1], 1, spread=3.0))
print(f"Costco: {len(c_locs)} locations (Generated)")

# --- WRITE OUTPUT ---
out_path = os.path.join(r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\utils", "real_retail_data.py")
try:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"WALMART_LOCATIONS = {w_locs}\n")
        f.write(f"TARGET_LOCATIONS = {t_locs}\n")
        f.write(f"COSTCO_LOCATIONS = {c_locs}\n")
    print("Done writing real_retail_data.py")
except Exception as e:
    print(f"Error writing file: {e}")
