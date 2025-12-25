from backend.database import SessionLocal
from backend.models import SystemConfig

db = SessionLocal()
try:
    conf = db.query(SystemConfig).filter(SystemConfig.config_key == "MISA_AMIS_ACT_ORG_CODE").first()
    if conf:
        conf.config_value = "CÔNG TY TNHH KIÊN THÀNH TÍN" # Revert to Full Name
        print("Updated MISA_AMIS_ACT_ORG_CODE back to 'CÔNG TY TNHH KIÊN THÀNH TÍN'")
    db.commit()
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
