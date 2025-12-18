
import urllib.request
import ssl
import csv
import io
import random

# Disable SSL verification
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_and_print_sample(url, label, lat_col, lon_col):
    print(f"\n--- {label} ---")
    try:
        with urllib.request.urlopen(url, context=ctx, timeout=10) as response:
            if response.getcode() == 200:
                content = response.read().decode('utf-8', errors='ignore')
                reader = csv.DictReader(io.StringIO(content))
                points = []
                for row in reader:
                    try:
                        lat = float(row.get(lat_col))
                        lon = float(row.get(lon_col))
                        points.append((lat, lon))
                    except (ValueError, TypeError):
                        continue
                
                print(f"Total Points: {len(points)}")
                if points:
                    sample = random.sample(points, min(10, len(points)))
                    print(f"Sample: {sample}")
                    return points
            else:
                print(f"Failed: HTTP {response.getcode()}")
    except Exception as e:
        print(f"Error: {e}")
    return []

# Walmart (Confirmed URL, checking formatting)
walmart_data = fetch_and_print_sample(
    "https://raw.githubusercontent.com/theriley106/WaltonAnalytics/master/Walmarts.csv",
    "Walmart", "Lat", "Long"
)

# Target (Specific Gist)
# I will try a few likely raw URLs for the gist "target_usa.csv"
target_data = fetch_and_print_sample(
    "https://gist.githubusercontent.com/4590327f311c62b5d444453535/raw/target_usa.csv", # Placeholder Attempt
    "Target", "Latitude", "Longitude" 
)

# Costco (Kaggle Dataset is not direct linkable. Using a known fallback gist if one exists, else stub)
# I will use a placeholder list for Costco if I can't find a direct CSV.
# The user wants REAL data. 
# Search result earlier mentioned: https://gist.githubusercontent.com/isaacabraham/ee50e72c9ee4978a2af62a582221dba8/raw/locations.csv 
# Let's check headers of that one.
costco_data = fetch_and_print_sample(
    "https://gist.githubusercontent.com/isaacabraham/ee50e72c9ee4978a2af62a582221dba8/raw/locations.csv",
    "Costco_Candidate", "lat", "long" # Guessing
)
