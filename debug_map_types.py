from backend.amis_accounting_client import AmisAccountingClient
from backend.database import SessionLocal
from backend.models import SystemConfig
import json

# CONFIG
db = SessionLocal()
def get_conf(key):
    c = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    return c.config_value if c else None

APP_ID = get_conf("MISA_AMIS_ACT_APP_ID")
ACCESS_CODE = get_conf("MISA_AMIS_ACT_ACCESS_CODE")
ORG_NAME = "CÔNG TY TNHH KIÊN THÀNH TÍN"
BASE_URL = "https://actapp.misa.vn"
db.close()

print(f"--- MAPPING TYPES 1-15 ---")
client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)

with open("map_results.txt", "w", encoding="utf-8") as f:
    for i in range(1, 16):
        print(f"Checking {i}...")
        f.write(f"\n> Checking Type {i}\n")
        try:
            items = client.get_dictionary(data_type=i, take=1)
            if items:
                count = len(items)
                first = items[0]
                if isinstance(first, dict):
                    keys = list(first.keys())
                    f.write(f"  [FOUND] Type {i}: Keys={keys}\n")
                    if "group_id" in keys or "inventory_item_category_id" in keys:
                        f.write("  -> POSSIBLE GROUP!\n")
                else:
                    f.write(f"  [RAW] Type {i}: {str(first)[:100]}\n")
            else:
                f.write("  [EMPTY]\n")
        except Exception as e:
            f.write(f"  [ERR] {e}\n")
