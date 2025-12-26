
from backend.database import SessionLocal
from backend.models import SystemConfig

def list_configs():
    db = SessionLocal()
    try:
        configs = db.query(SystemConfig).all()
        print("--- Existing Config Keys ---")
        for c in configs:
            val_preview = c.config_value[:5] + "..." if c.config_value else "None"
            print(f"{c.config_key}: {val_preview}")
    finally:
        db.close()

if __name__ == "__main__":
    list_configs()
