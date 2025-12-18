
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

# 1. WALMART & SAM'S CLUB
print("Processing Walmart & Sam's Club...")
w_locs = []
sams_locs = []
try:
    df_w = pd.read_csv(os.path.join(data_dir, "walmart.csv"))
    for _, row in df_w.iterrows():
        try:
            lat, lon = web_mercator_to_latlon(row['x'], row['y'])
            if 24 <= lat <= 50 and -125 <= lon <= -66: 
                coord = (round(lat, 5), round(lon, 5))
                if str(row.get('Type', '')).strip().upper() == "WHOLESALE":
                    sams_locs.append(coord)
                else:
                    w_locs.append(coord)
        except: continue
    print(f"Walmart: {len(w_locs)} locations")
    print(f"Sam's Club: {len(sams_locs)} locations")
except Exception as e:
    print(f"Walmart/Sams Error: {e}")

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

# 4. KROGER (Refined)
print("Processing Kroger (Splitting Brands & Filtering Jewelry)...")
k_main_locs = []
k_sub_locs = []
try:
    with open(os.path.join(data_dir, "kroger_store.csv"), 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if len(lines) > 0:
        header_line = lines[0].strip()
        headers = next(csv.reader([header_line]))
        
        try:
            lat_idx = headers.index('latitude')
            lon_idx = headers.index('longitude')
            brand_idx = headers.index('brand')
            type_idx = headers.index('loc_type') # New
            
            excluded_count = 0
            filtered_samples = []
            seen_types = set()
            
            for line in lines[1:]:
                line = line.strip()
                if not line: continue
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1].replace('""', '"')
                
                try:
                    row = next(csv.reader([line]))
                    if len(row) > max(lon_idx, brand_idx, type_idx):
                        lat = float(row[lat_idx])
                        lon = float(row[lon_idx])
                        brand = row[brand_idx].strip().upper()
                        ltype = row[type_idx].strip().upper()
                        
                        # FILTER: Exclude Jewelry (Brand 'JEWELRY' or Type 'J')
                        if brand == "JEWELRY" or ltype == "J":
                            continue
                            
                        if 24 <= lat <= 50 and -125 <= lon <= -66:
                            coord = (round(lat, 5), round(lon, 5))
                            
                            if brand == "KROGER":
                                k_main_locs.append(coord)
                            else:
                                k_sub_locs.append(coord) # Subsidiaries
                except (ValueError, StopIteration):
                    continue
        except ValueError:
             print("Kroger: headers missing")
             
    print(f"Kroger Main: {len(k_main_locs)}")
    print(f"Kroger Subs: {len(k_sub_locs)}")
except Exception as e:
    print(f"Kroger Error: {e}")

# --- WRITE OUTPUT ---
out_path = os.path.join(r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\utils", "real_retail_data.py")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"WALMART_LOCATIONS = {w_locs}\n")
    f.write(f"SAMS_LOCATIONS = {sams_locs}\n")
    f.write(f"TARGET_LOCATIONS = {t_locs}\n")
    f.write(f"COSTCO_LOCATIONS = {c_locs}\n")
    f.write(f"KROGER_LOCATIONS = {k_main_locs}\n")
    f.write(f"KROGER_SUB_LOCATIONS = {k_sub_locs}\n")
print("Done.")
