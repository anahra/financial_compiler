
import csv

file_path = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\STORE_STATUS_PUBLIC_VIEW_-8827503165297490716.csv"

try:
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"Headers: {headers}")
        print("First 3 rows:")
        for i, row in enumerate(reader):
            if i >= 3: break
            print(row)
except Exception as e:
    print(f"Error reading file: {e}")
