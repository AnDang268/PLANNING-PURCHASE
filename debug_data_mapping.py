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

client = AmisAccountingClient(APP_ID, ACCESS_CODE, company_code=ORG_NAME, base_url=BASE_URL)

def check_mapping(name, data_type, field_map):
    print(f"\n--- CHECKING {name} (Type {data_type}) ---")
    items = client.get_dictionary(data_type, take=1)
    if not items:
        print("  [EMPTY]")
        return
        
    item = items[0]
    # print(f"  Raw Keys: {list(item.keys())}")
    
    print("  PROPOSED MAPPING:")
    for db_col, api_key in field_map.items():
        val = item.get(api_key, 'N/A')
        print(f"    {db_col} ({api_key}) = {str(val)[:50]}")

# 1. Product
check_mapping("Product", 2, {
    "sku_id": "inventory_item_code",
    "product_name": "inventory_item_name",
    "base_unit_id": "unit_id",
    "group_id": "inventory_item_category_id_list", # Caution: List?
    "amis_act_id": "inventory_item_id"
})

# 2. Unit
check_mapping("Unit", 4, {
    "unit_id": "unit_id",
    "unit_name": "unit_name",
    "description": "description"
})

# 3. Product Group
check_mapping("Product Group", 14, {
    "group_id": "inventory_category_id",
    "group_name": "inventory_category_name",
    "misa_code": "inventory_category_code"
})

# 4. Customer/Vendor (Type 1)
check_mapping("Customer", 1, {
    "customer_id": "account_object_code",
    "customer_name": "account_object_name",
    "address": "address",
    "phone": "tel",
    "email": "email", # Not found in keys? Check raw.
    "misa_code": "account_object_code",
    "group_id": "account_object_group_id_list"
})
