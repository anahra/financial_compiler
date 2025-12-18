
import pandas as pd
import csv
import os

path = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\kroger_store.csv"

rows = []
try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) > 0:
        header_line = lines[0].strip()
        headers = next(csv.reader([header_line]))
        
        try:
            brand_idx = headers.index('brand')
            type_idx = headers.index('loc_type')
        except ValueError:
            print("Missing columns")
            exit()
            
        for line in lines[1:]:
             line = line.strip()
             if not line: continue
             if line.startswith('"') and line.endswith('"'):
                 line = line[1:-1].replace('""', '"')
             try:
                 row = next(csv.reader([line]))
                 if len(row) > max(brand_idx, type_idx):
                     rows.append((row[brand_idx], row[type_idx]))
             except: continue

    df = pd.DataFrame(rows, columns=['brand', 'loc_type'])
    print("Cross Tab (Brand vs LocType):")
    print(pd.crosstab(df['brand'], df['loc_type']))

except Exception as e:
    print(e)
