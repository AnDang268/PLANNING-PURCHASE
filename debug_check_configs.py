
from backend.database import SessionLocal
from backend.models import SystemConfig

def check_crm_configs():
    db = SessionLocal()
    try:
        keys_to_check = [
            'MISA_CRM_CLIENT_ID', 'MISA_CRM_CLIENT_SECRET', # New standardized keys
            'MISA_CRM_COMPANY_CODE', # << Added this
            'MISA_APP_ID', 'MISA_ACCESS_KEY', 'MISA_ACCESS_TOKEN', # Potential ambiguous keys
            'MISA_AMIS_ACT_APP_ID' # Known Accounting key
        ]
        
        print("--- Config Check ---")
        for k in keys_to_check:
            cfg = db.query(SystemConfig).filter(SystemConfig.config_key == k).first()
            if cfg:
                print(f"{k}: '{cfg.config_value}'")
            else:
                print(f"{k}: <MISSING>")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_crm_configs()
