from backend.database import SessionLocal
from backend.models import SystemConfig
from datetime import datetime # Added for datetime.now()

default_configs = [
    # MISA CRM (Sales)
    ("MISA_APP_ID", "kttwebshop", "MISA CRM App ID"),
    ("MISA_ACCESS_KEY", "9JfVc6h2Q0Nq1mT61o14NN4Ck+Qyt7kI6Pxt9TQcd/8=", "MISA CRM Secret Key"),
    ("MISA_API_URL", "https://crmconnect.misa.vn/api/v2", "MISA CRM API URL"),
    ("LAST_ORDER_SYNC_TIME", "2023-01-01T00:00:00", "Last successful sync time for Orders"),
    
    # MISA AMIS ACCOUNTING (Finance)
    ("MISA_AMIS_ACT_APP_ID", "04991a48-9138-42a0-93a2-1a529c47f379", "MISA AMIS ACT App ID"),
    ("MISA_AMIS_ACT_ACCESS_CODE", "dIe3QQpQ6mWBumZyAoYKbIS8zcmfg+uJhqtmly1j+xAm2HbWqDn8dQb+Al+xc4cluMwLZdqeCN9eiPaJGHRssGy8YRw5nxQZop/CVCOS2+jcnTuXzq4XrRD9233iMFzVk+UNMtx+nSLKmOh0ogovywSCFmDqolVainCotUD/Ny+YK9PV6kMGRSOiD7SJZIsOAqi56OJCIIRB077X47Aw0hEoauBlfUYIn/tOu2G1Lo+AyXz8fMNj0YgpcAMfd5eDFgeuVOf9mHeRi2xaTpuksg==", "MISA AMIS ACT Access Code"),
    ("MISA_AMIS_ACT_ORG_CODE", "CÔNG TY TNHH KIÊN THÀNH TÍN", "MISA AMIS ACT Organization Code"),
    ("MISA_AMIS_ACT_BASE_URL", "https://actapp.misa.vn", "MISA AMIS ACT Base URL")
]

print("--- FIXING SYSTEM CONFIG ---")
db = SessionLocal()
try:
    for key, val, desc in default_configs:
        existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if not existing:
            print(f"[NEW] Adding {key}")
            db.add(SystemConfig(config_key=key, config_value=val, description=desc))
        else:
            # OPTIONAL: Force Update if user wants to reset keys
            print(f"[UPDATE] Updating {key}") 
            existing.config_value = val
            existing.updated_at = datetime.now()
            
    db.commit()
    print("[SUCCESS] Config Updated.")
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    db.close()
