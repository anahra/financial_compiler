
path = r"c:\Users\agusn\OneDrive - HEC Paris\Documentos\0_General\PG\financial_compiler\data\retailers\kroger_store.csv"
with open(path, 'r', encoding='utf-8') as f:
    print("--- RAW KROGER ---")
    for i in range(3):
        print(f.readline().strip())
