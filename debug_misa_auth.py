
import requests
import json
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import SystemConfig

def debug_auth():
    db = SessionLocal()
    try:
        # Get Credentials
        client_id_cfg = db.query(SystemConfig).filter(SystemConfig.config_key == 'MISA_CRM_CLIENT_ID').first()
        client_secret_cfg = db.query(SystemConfig).filter(SystemConfig.config_key == 'MISA_CRM_CLIENT_SECRET').first()
        
        if not client_id_cfg or not client_secret_cfg:
            print("Missing Credentials in DB")
            return

        client_id = client_id_cfg.config_value
        client_secret = client_secret_cfg.config_value
        
        print(f"Authenticating with ID: {client_id}")
        
        url = "https://amisapp.misa.vn/crm/gc/api/public/api/v2/Account"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        resp = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {resp.status_code}")
        print("Response Headers:", dict(resp.headers))
        
        try:
            data = resp.json()
            print("\nResponse Body (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Check if token is just a string or object
            token_data = data.get("data")
            if isinstance(token_data, str):
                print(f"\nToken is a STRING: {token_data[:20]}...")
                # If it's a string, maybe it's a JWT? Let's decode it
                if len(token_data.split('.')) == 3:
                     print("\nToken looks like JWT. Decoding payload...")
                     import base64
                     try:
                         # Padding fix
                         payload = token_data.split('.')[1]
                         payload += '=' * (-len(payload) % 4)
                         decoded = base64.b64decode(payload)
                         json_payload = json.loads(decoded.decode('utf-8'))
                         
                         with open("debug_jwt_payload.txt", "w", encoding="utf-8") as f:
                             json.dump(json_payload, f, indent=4)
                             
                         print("\n[SUCCESS] Decoded payload written to debug_jwt_payload.txt")
                     except Exception as e:
                         print(f"JWT Decode Error: {e}")

            else:
                print(f"\nToken is OBJECT/Other: {type(token_data)}")
                
        except Exception as e:
            print(f"Not JSON: {resp.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_auth()
