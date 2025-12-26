import requests
import json
from datetime import datetime

class MisaCrmV2Client:
    def __init__(self, client_id, client_secret, company_code, base_url="https://amisapp.misa.vn/crm/gc/api/public/api/v2"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.company_code = company_code
        self.base_url = base_url.rstrip("/")
        self.token = None

    def authenticate(self):
        """
        Get Access Token using Client ID/Secret.
        Endpoint: /Account
        """
        url = f"{self.base_url}/Account"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    self.token = data.get("data")
                    return self.token
                else:
                    raise Exception(f"Auth Failed: {data.get('code')} - {data.get('data')}")
            else:
                raise Exception(f"HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            raise Exception(f"Connection Error: {e}")

    def get_product_ledger(self, stock_id=None, page=1, page_size=100):
        """
        Fetch Inventory (Product Ledger).
        Endpoint: /Stocks/product_ledger
        """
        if not self.token:
            self.authenticate()

        url = f"{self.base_url}/Stocks/product_ledger"
        headers = {
            "authorization": f"Bearer {self.token}", 
            "clientid": self.client_id,
            "companycode": self.company_code,
            # "Content-Type": "application/json" # Remove for GET
        }
        
        params = {
            "page": page,
            "pageSize": page_size
        }
        if stock_id:
            params["stockID"] = stock_id
            
        print(f"[DEBUG] Sending Headers: {headers}")
        print(f"[DEBUG] Sending Params: {params}") 

        # Try lowercase headers to match error msg hint
        headers["companycode"] = self.company_code

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                # API quirks: success might be missing/false but code=0 and data present implies success
                code = data.get("code")
                items_data = data.get("data")
                
                if data.get("success") or str(code) == "0" or (isinstance(items_data, list) and len(items_data) > 0):
                    items = items_data if isinstance(items_data, list) else []
                    return items
                else:
                    raise Exception(f"API Error: {code} - {data.get('data')}")
            else:
                 print(f"DEBUG API ERROR: {resp.status_code}")
                 print(f"Headers: {resp.headers}")
                 print(f"Body: {resp.text}")
                 raise Exception(f"HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
             raise Exception(f"Inventory Fetch Error: {e}")
