import requests
import json
from datetime import datetime

class AmisAccountingClient:
    def __init__(self, app_id, access_code, company_code=None, base_url="https://actapp.misa.vn"):
        """
        Client for MISA AMIS Accounting (ACT).
        :param app_id: Provided by User.
        :param access_code: Long secret string.
        :param company_code: Org Company Code check 'X-MISA-CompanyCode' header?
        """
        self.app_id = app_id
        self.access_code = access_code
        self.company_code = company_code
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.token_expiry = None

    def get_token(self):
        """
        Authenticates with actapp.misa.vn to get Access Token.
        """
        endpoint = "api/oauth/actopen/connect"
        url = f"{self.base_url}/{endpoint}"
        payload = {
            "app_id": self.app_id,
            "access_code": self.access_code,
            "org_company_code": self.company_code # Added per User Request
        }
        
        try:
            print(f"[ACT-AUTH] Connecting to {url}...")
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("Success"):
                    # Token is inside 'Data' string
                    inner_data = json.loads(data.get("Data", "{}"))
                    self.token = inner_data.get("access_token")
                    print(f"[ACT-AUTH] Success! Token: {self.token[:10]}...")
                    return self.token
                else:
                    print(f"[ACT-AUTH] Failed: {data.get('ErrorMessage')}")
            else:
                print(f"[ACT-AUTH] HTTP Error: {resp.status_code} {resp.text}")
                
        except Exception as e:
            print(f"[ACT-AUTH] Exception: {e}")
        return None

    def _get_headers(self):
        if not self.token:
            self.get_token()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        # Add Company Code if required (User mentioned 'org_company_code')
        if self.company_code:
             headers["X-MISA-CompanyCode"] = self.company_code
             headers["CompanyCode"] = self.company_code # Try both just in case
        
        return headers

    def get_dictionary(self, data_type, skip=0, take=20, last_sync_time=""):
        """
        Fetches Dictionary Data from MISA AMIS Accounting.
        Target URL: /apir/sync/actopen/get_dictionary
        """
        if not self.token:
            self.get_token()
            
        endpoint = "apir/sync/actopen/get_dictionary"
        url = f"{self.base_url}/{endpoint}"
        
        # User defined headers that work (No Authorization Bearer, No CompanyCode)
        headers = {
            "Content-Type": "application/json",
            "X-MISA-AccessToken": self.token
        }
        
        payload = {
            "app_id": self.app_id,
            "data_type": int(data_type), # Ensure INT
            "skip": skip,
            "take": take,
            "last_sync_time": last_sync_time or ""
        }
        
        try:
            print(f"[ACT-DICT] Fetching Type {data_type}...")
            # print(f"Payload: {json.dumps(payload)}") 
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("Success"):
                    # Handle Data as String or List
                    raw_data = data.get("Data", [])
                    if isinstance(raw_data, str):
                        try:
                            return json.loads(raw_data)
                        except:
                            print(f"   [FAIL] Could not parse Data string.")
                            return []
                    return raw_data
                else:
                    print(f"   [FAIL] Msg: {data.get('ErrorMessage')}")
            else:
                print(f"   [FAIL] HTTP {resp.status_code}")
                # print(f"   [FAIL] Body: {resp.text[:200]}")
        except Exception as e:
            print(f"   [ERROR] {e}")
        return []

    def get_account_objects(self):
        """Type 1: Customers and Vendors"""
        return self.get_dictionary(1)

    def get_inventory_items(self):
        """Type 2: Products / VTHH"""
        return self.get_dictionary(2)

    def get_stocks(self):
        """Type 3: Warehouses / Kho"""
        return self.get_dictionary(3)

    def get_units(self):
        """Type 4: Units / ĐVT"""
        return self.get_dictionary(4)
        
    def get_inventory_item_categories(self):
        """Type 14: Product Groups / Nhóm VTHH"""
        return self.get_dictionary(14)
        
    def call_api(self, endpoint, method="GET", params=None, payload=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            resp = requests.request(method, url, headers=headers, params=params, json=payload, timeout=30)
            resp.raise_for_status()
            
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"[ACT-API] Error: {e}")
            if e.response: print(f"   Body: {e.response.text}")
            return None
