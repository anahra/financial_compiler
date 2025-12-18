
import csv
import os

files = [
    r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\walmart.csv",
    r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\target.csv",
    r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\costco.csv"
]

for fpath in files:
    print(f"\n--- Scanning {fpath} ---")
    if not os.path.exists(fpath):
        print("File does not exist (checking original location just in case)")
        # Fallback check
        base = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG"
        fn = os.path.basename(fpath)
        if fn == "target.csv": fn = "Target locations dataset.csv"
        if fn == "walmart.csv": fn = "STORE_STATUS_PUBLIC_VIEW_-8827503165297490716.csv"
        if fn == "costco.csv": fn = "costco-feb-2024.csv"
        
        orig = os.path.join(base, fn)
        if os.path.exists(orig):
             fpath = orig
             print(f"Found at original: {fpath}")
        else:
             print("Not found anywhere.")
             continue
        
    try:
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            headers = next(reader)
            print(f"Headers: {headers}")
            try:
                print(f"Row 1: {next(reader)}")
            except StopIteration:
                print("Empty file?")
    except Exception as e:
        print(f"Error: {e}")
