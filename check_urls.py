
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ("Walmart", "https://raw.githubusercontent.com/ilyazub/walmart-store-locator/master/output/walmart_stores.csv"),
    ("Walmart2", "https://raw.githubusercontent.com/ilyazub/walmart-store-locator/main/output/walmart_stores.csv"),
    ("Costco", "https://raw.githubusercontent.com/swinton/Visualize-This/master/ch08/geocode/costcos-limited.csv"),
    ("Target", "https://gist.githubusercontent.com/4590327f311c62b5d444453535/raw/target_usa.csv"), # Placeholder, unlikely to work without ID
]

for name, url in urls:
    try:
        with urllib.request.urlopen(url, context=ctx, timeout=5) as response:
            if response.getcode() == 200:
                print(f"[SUCCESS] {name}")
                print(response.read().decode('utf-8')[:200]) # Print first 200 chars
            else:
                print(f"[FAILED] {name}: {response.getcode()}")
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
