
import pandas as pd
import os
import csv

path = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\kroger_store.csv"

# Read robustly like before
rows = []
try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) > 0:
        header_line = lines[0].strip()
        headers = next(csv.reader([header_line]))
        brand_idx = headers.index('brand')
        
        for line in lines[1:]:
             line = line.strip()
             if not line: continue
             if line.startswith('"') and line.endswith('"'):
                 line = line[1:-1].replace('""', '"')
             try:
                 row = next(csv.reader([line]))
                 if len(row) > brand_idx:
                     rows.append(row[brand_idx])
             except: continue

    # Count unique brands
    df_brands = pd.Series(rows)
    print("Unique Brands:\n", df_brands.value_counts())

except Exception as e:
    print(e)
