
import random

def is_valid_us_land(lat, lon):
    # Hard bounds
    if not (24.5 <= lat <= 49.5 and -125.0 <= lon <= -66.9): return False
    # Atlantic cuts
    if lat < 35.0 and lon > -75.5: return False
    if 35.0 <= lat < 40.0 and lon > -74.0: return False
    if lat >= 40.0 and lon > -69.5: return False
    # Gulf cut
    if lat < 30.0 and (-95.0 < lon < -82.0): return False
    # Pacific cuts
    if lat < 35.0 and lon < -120.0: return False
    if lat >= 35.0 and lon < -124.0: return False
    return True

def generate_points(center_lat, center_lon, n, spread):
    pts = []
    attempts = 0
    while len(pts) < n and attempts < n*20:
        attempts += 1
        lat = center_lat + (random.random() - 0.5) * spread
        lon = center_lon + (random.random() - 0.5) * spread
        if is_valid_us_land(lat, lon):
            pts.append((round(lat, 4), round(lon, 4)))
    return pts

# Major Hubs
hubs = [
    (40.7128, -74.0060, 0.15), (42.3601, -71.0589, 0.10), (39.9526, -75.1652, 0.08),
    (38.9072, -77.0369, 0.08), (33.7490, -84.3880, 0.12), (25.7617, -80.1918, 0.10),
    (28.5383, -81.3792, 0.08), (36.1627, -86.7816, 0.08), (35.2271, -80.8431, 0.08),
    (41.8781, -87.6298, 0.12), (42.3314, -83.0458, 0.10), (44.9778, -93.2650, 0.08),
    (39.9612, -82.9988, 0.08), (38.6270, -90.1994, 0.08), (32.7767, -96.7970, 0.12),
    (29.7604, -95.3698, 0.12), (30.2672, -97.7431, 0.08), (39.7392, -104.9903, 0.08),
    (34.0522, -118.2437, 0.15), (37.7749, -122.4194, 0.10), (32.7157, -117.1611, 0.08),
    (33.4484, -112.0740, 0.10), (47.6062, -122.3321, 0.08), (36.1699, -115.1398, 0.05)
]

w_pts = []
t_pts = []
c_pts = []

random.seed(42)

for lat, lon, density in hubs:
    w_pts.extend(generate_points(lat, lon, int(1500 * density * 0.6), 2.5))
    t_pts.extend(generate_points(lat, lon, int(600 * density * 0.7), 1.8))
    c_pts.extend(generate_points(lat, lon, int(300 * density * 0.8), 1.2))

# Rural Fill for Walmart
w_rural = generate_points(38.0, -95.0, 400, 20.0) # Broad scatter
w_pts.extend(w_rural)

print("WALMART_LOCATIONS = " + str(w_pts))
print("TARGET_LOCATIONS = " + str(t_pts))
print("COSTCO_LOCATIONS = " + str(c_pts))
