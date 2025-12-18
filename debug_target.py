
import csv

target_file = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\target.csv"

print("--- TARGET HEADERS ---")
try:
    with open(target_file, 'r', encoding='utf-8', errors='replace') as f:
        line1 = f.readline()
        line2 = f.readline()
        print(f"L1: {line1.strip()}")
        print(f"L2: {line2.strip()}")
except Exception as e:
    print(f"Error: {e}")
