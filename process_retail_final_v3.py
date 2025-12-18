
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

# 1. WALMART
print("Processing Walmart...")
w_locs = []
try:
    df_w = pd.read_csv(os.path.join(data_dir, "walmart.csv"))
    for _, row in df_w.iterrows():
        try:
            lat, lon = web_mercator_to_latlon(row['x'], row['y'])
            if 24 <= lat <= 50 and -125 <= lon <= -66: 
                w_locs.append((round(lat, 5), round(lon, 5)))
        except: continue
    print(f"Walmart: {len(w_locs)} locations")
except Exception as e:
    print(f"Walmart Error: {e}")

# 2. TARGET
print("Processing Target...")
t_locs = []
try:
    with open(os.path.join(data_dir, "target.csv"), 'r', encoding='latin1') as f:
        lines = f.readlines()
    header_line = lines[0].strip()
    headers = next(csv.reader([header_line]))
    
    try:
        lat_idx = next(i for i, h in enumerate(headers) if 'Address.Latitude' in h)
        lon_idx = next(i for i, h in enumerate(headers) if 'Address.Longitude' in h)
    except StopIteration:
        lat_idx, lon_idx = -1, -1

    if lat_idx != -1:
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1].replace('""', '"')
            try:
                row = next(csv.reader([line]))
                if len(row) > lon_idx:
                    lat = float(row[lat_idx])
                    lon = float(row[lon_idx])
                    if 24 <= lat <= 50 and -125 <= lon <= -66:
                        t_locs.append((round(lat, 5), round(lon, 5)))
            except: continue
    print(f"Target: {len(t_locs)} locations")
except Exception as e:
    print(f"Target Error: {e}")

# 3. COSTCO
print("Processing Costco (Geocoding)...")
c_locs = []
try:
    import pgeocode
    nomi = pgeocode.Nominatim('us')
    df_c = pd.read_csv(os.path.join(data_dir, "costco.csv"), sep=';')
    if 'Zipcode' in df_c.columns:
        zips = df_c['Zipcode'].astype(str).apply(lambda x: x.split('-')[0].strip()[:5]).tolist()
        results = nomi.query_postal_code(zips)
        valid_geo = results.dropna(subset=['latitude', 'longitude'])
        for _, row in valid_geo.iterrows():
             lat = row['latitude']
             lon = row['longitude']
             if 24 <= lat <= 50 and -125 <= lon <= -66:
                 c_locs.append((round(lat, 5), round(lon, 5)))
        print(f"Costco: {len(c_locs)} locations")
except Exception as e:
    print(f"Costco Error: {e}")

# 4. KROGER
print("Processing Kroger...")
k_locs = []
try:
    with open(os.path.join(data_dir, "kroger_store.csv"), 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if len(lines) > 0:
        header_line = lines[0].strip()
        headers = next(csv.reader([header_line]))
        
        # Find indices
        try:
            lat_idx = headers.index('latitude')
            lon_idx = headers.index('longitude')
            
            for line in lines[1:]:
                line = line.strip()
                if not line: continue
                # Handle whole-row quoting: "val,val,val"
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1] # Strip outer
                    line = line.replace('""', '"') # Unescape inner
                
                try:
                    row = next(csv.reader([line]))
                    if len(row) > lon_idx:
                        lat = float(row[lat_idx])
                        lon = float(row[lon_idx])
                        if 24 <= lat <= 50 and -125 <= lon <= -66:
                            k_locs.append((round(lat, 5), round(lon, 5)))
                except (ValueError, StopIteration):
                    continue
        except ValueError:
             print("Kroger: Could not find 'latitude' or 'longitude' in headers")
             
    print(f"Kroger: {len(k_locs)} locations")
except Exception as e:
    print(f"Kroger Error: {e}")
    import traceback
    traceback.print_exc()

# --- WRITE OUTPUT ---
out_path = os.path.join(r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\utils", "real_retail_data.py")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"WALMART_LOCATIONS = {w_locs}\n")
    f.write(f"TARGET_LOCATIONS = {t_locs}\n")
    f.write(f"COSTCO_LOCATIONS = {c_locs}\n")
    f.write(f"KROGER_LOCATIONS = {k_locs}\n")
print("Done.")
