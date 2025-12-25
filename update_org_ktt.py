from backend.database import SessionLocal
from backend.models import SystemConfig

db = SessionLocal()
try:
    conf = db.query(SystemConfig).filter(SystemConfig.config_key == "MISA_AMIS_ACT_ORG_CODE").first()
    if conf:
        conf.config_value = "KTT"
        print("Updated MISA_AMIS_ACT_ORG_CODE to 'KTT'")
    else:
        new_conf = SystemConfig(config_key="MISA_AMIS_ACT_ORG_CODE", config_value="KTT", description="AMIS ACT Org Code")
        db.add(new_conf)
        print("Created MISA_AMIS_ACT_ORG_CODE = 'KTT'")
    db.commit()
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
