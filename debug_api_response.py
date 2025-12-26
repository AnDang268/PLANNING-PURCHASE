import requests
import json
from datetime import date, datetime

def date_converter(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    return None

try:
    print("Fetching data from API...")
    r = requests.get("http://localhost:8000/api/planning/rolling/matrix?limit=1")
    if r.status_code == 200:
        data = r.json()
        print(f"Got {len(data)} records.")
        if len(data) > 0:
            row = data[0]
            print("\nSAMPLE ROW KEYS:", list(row.keys()))
            print("\nSAMPLE BUCKET_DATE:", repr(row.get('bucket_date')))
            print("\nFULL ROW JSON:")
            print(json.dumps(row, indent=2, default=str))
        else:
            print("API returned empty list.")
    else:
        print(f"Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Exception: {e}")
