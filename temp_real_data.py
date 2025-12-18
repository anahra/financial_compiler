
import random

# REAL RETAIL DATA (Sourced from Open Data Repositories)
# Counts:
# Walmart: 0
# Target: 0
# Costco: 0 (If 0, using fallback)

def get_sampled_locations(locations, sample_ratio=0.2):
    if not locations: return []
    sample_size = int(len(locations) * sample_ratio)
    # Use random.sample for unique elements
    return random.sample(locations, max(1, sample_size))

REAL_WALMART_LOCATIONS = []
REAL_TARGET_LOCATIONS = []
REAL_COSTCO_LOCATIONS = [] # Needs Fallback 
