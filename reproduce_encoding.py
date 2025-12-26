import requests
import json
from backend.database import SessionLocal
from backend.models import SystemConfig
from backend.amis_accounting_client import AmisAccountingClient

def reproduce():
    with open("reproduce_output.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            try:
                f.write(str(msg) + "\n")
            except Exception as e:
                print(f"Log Error: {e}")

        db = SessionLocal()
        try:
            def get_config(key):
                cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
                return cfg.config_value if cfg else None

            app_id = get_config('MISA_AMIS_ACT_APP_ID')
            access_code = get_config('MISA_AMIS_ACT_ACCESS_CODE')
            base_url = get_config('MISA_AMIS_ACT_BASE_URL') or "https://actapp.misa.vn"
            
            log(f"AppID: {app_id}")
            
            client = AmisAccountingClient(app_id, access_code, "CÔNG TY TNHH KIÊN THÀNH TÍN", base_url)
            
            # We need to manually call the API to inspect bytes
            if not client.token:
                try:
                    token = client.get_token()
                    log(f"Token acquired: {token[:10]}...")
                except Exception as e:
                    log(f"Token Error: {e}")
                    return

            # Manually reproduce get_dictionary(1) aka Partners which has Groups
            endpoint = "apir/sync/actopen/get_dictionary"
            url = f"{client.base_url}/{endpoint}"
            
            headers = {
                "Content-Type": "application/json",
                "X-MISA-AccessToken": client.token
            }
            
            payload = {
                "app_id": client.app_id,
                "data_type": 1, # Partners
                "skip": 0,
                "take": 20,
                "last_sync_time": ""
            }
            
            log("--- Sending Request ---")
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=60)
                
                log(f"Status: {resp.status_code}")
                # log(f"Original Encoding guessed by requests: {resp.encoding}")
                log(f"Content-Type Header: {resp.headers.get('Content-Type')}")
                
                content_bytes = resp.content
                log(f"Raw Bytes Sample (first 200 chars): {content_bytes[:200]}")
                
                # Try decoding with UTF-8
                try:
                    decoded_utf8 = content_bytes.decode('utf-8')
                    log("\nDecoded with UTF-8 (sample):")
                    log(decoded_utf8[:1000]) # 1000 chars
                except Exception as e:
                    log(f"\nDecoding UTF-8 Failed: {e}")

                # Try decoding with UTF-8-SIG
                try:
                    decoded_utf8sig = content_bytes.decode('utf-8-sig')
                    log("\nDecoded with UTF-8-SIG (sample):")
                    log(decoded_utf8sig[:1000])
                except Exception as e:
                    log(f"\nDecoding UTF-8-SIG Failed: {e}")
                    
                # Try decoding with ISO-8859-1
                try:
                    decoded_iso = content_bytes.decode('ISO-8859-1')
                    log("\nDecoded with ISO-8859-1 (sample):")
                    log(decoded_iso[:1000])
                except Exception as e:
                     log(f"\nDecoding ISO Failed: {e}")
                     
            except Exception as e:
                log(f"Request Error: {e}")

        finally:
            db.close()

if __name__ == "__main__":
    reproduce()
