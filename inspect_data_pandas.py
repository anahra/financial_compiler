
import pandas as pd
import os

base_dir = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers"
files = {
    "Walmart": "walmart.csv",
    "Target": "target.csv",
    "Costco": "costco.csv"
}

for brand, fname in files.items():
    fpath = os.path.join(base_dir, fname)
    print(f"\n=== {brand} ({fname}) ===")
    if not os.path.exists(fpath):
        print("FILE NOT FOUND")
        continue
    
    try:
        # Try reading with pandas for smarter parsing
        # Try default comma
        if brand == "Costco":
            df = pd.read_csv(fpath, sep=';') # Saw semi-colon earlier
        else:
            df = pd.read_csv(fpath)
            
        print("Columns:", df.columns.tolist())
        print(df.head(2).T)
    except Exception as e:
        print(f"Error reading: {e}")
