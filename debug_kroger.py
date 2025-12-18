
import pandas as pd
import os

path = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\kroger_store.csv"
try:
    df = pd.read_csv(path)
    print("Cols:", df.columns.tolist())
    print("Head:\n", df.head(1).T)
    # Check nulls in latitude
    if 'latitude' in df.columns:
        print("Null Lats:", df['latitude'].isnull().sum())
        print("First valid lat:", df['latitude'].dropna().iloc[0] if not df['latitude'].dropna().empty else "None")
except Exception as e:
    print(e)
