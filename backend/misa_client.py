import requests
import json
from datetime import datetime

class MisaClient:
    def __init__(self, app_id, access_key, base_url="https://crmconnect.misa.vn"):
        """
        Khởi tạo Client kết nối MISA.
        :param app_id: ID ứng dụng được MISA cấp.
        :param access_key: Secret Key để xác thực.
        :param base_url: Đường dẫn gốc của API MISA (mặc định là CRM Connect).
        """
        self.app_id = app_id
        self.access_key = access_key
        self.base_url = base_url.rstrip("/")
        self.token = None
    
    def get_token(self):
        """
        Hàm Xác thực (Authentication):
        1. Gọi sang MISA với AppID và SecretKey.
        2. Nhận về 'Access Token' (chìa khóa tạm thời).
        3. Lưu Token này để dùng cho các bước sau.
        """
        endpoint = "api/v2/Account"
        url = f"{self.base_url}/{endpoint}"
        payload = {
             "client_id": self.app_id, 
             "client_secret": self.access_key
        }
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                # The token is in data['data'] based on swagger example
                self.token = data.get("data")
                return self.token
            else:
                print(f"Token Generation Failed: {data}")
                return None
        except Exception as e:
            print(f"Token Request Error: {e}")
            return None

    def _get_headers(self):
        if not self.token:
            self.get_token()
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def call_api(self, endpoint, method="GET", params=None, payload=None):
        """
        Hàm bọc (Wrapper) để gọi API an toàn:
        1. Tự động lấy Header chứa Token.
        2. Tự động xử lý lỗi mạng (try/except).
        3. Trả về kết quả JSON đã lọc sạch.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            response.raise_for_status()
            
            # Force UTF-8 if it seems to be default ASCII/ISO
            # MISA API often returns json with implicit UTF-8 but requests detects it as ISO-8859-1
            if response.encoding is None or 'ISO' in response.encoding.upper():
                response.encoding = 'utf-8-sig' # Try utf-8-sig to handle BOM if present
            
            # Additional Debug
            # print(f" DEBUG: Response Encoding: {response.encoding}")
            
            data = response.json()
            
            # Auto-extract List if wrapped in 'Data' or 'data'
            if isinstance(data, dict):
                if "Data" in data and isinstance(data["Data"], list):
                    return data["Data"]
                if "data" in data and isinstance(data["data"], list):
                    return data["data"]
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            if e.response is not None:
                 print(f"Response Body: {e.response.text}")
            return [] # Return empty list on error to stop loops

    def get_products(self, page_index=1, page_size=100):
        """
        Lấy danh mục Hàng hóa (Master Data).
        :param page_index: Trang số mấy (MISA phân trang để tránh quá tải).
        """
        # Assuming standard REST for Products as per other endpoints
        endpoint = "api/v2/Products" 
        params = {
            "page": page_index,    # Swagger uses 'page' (0-indexed)
            "pageSize": page_size  # Swagger uses 'pageSize'
        }
        return self.call_api(endpoint, method="GET", params=params)

    def get_orders(self, from_date=None, to_date=None, page_index=1, page_size=100):
        """
        Lấy dữ liệu Đơn hàng Bán (Transaction Data).
        :param from_date: Lấy đơn từ ngày nào (Quan trọng cho Incremental Sync).
        """
        # User insisted on GET.
        # If standard REST applies:
        endpoint = "api/v2/Orders" 
        
        params = {
            "page": page_index,
            "pageSize": page_size
        }
        # Add date filters if applicable (guessing param names based on MISA conventions)
        if from_date:
            params["FromDate"] = from_date
        if to_date:
            params["ToDate"] = to_date
            
        return self.call_api(endpoint, method="GET", params=params)

    def get_customers(self, page_index=1, page_size=100):
        endpoint = "api/v2/AccountObjects" 
        params = {
            "page": page_index,
            "pageSize": page_size,
            "isCustomer": "true" 
        }
        return self.call_api(endpoint, method="GET", params=params)

    def get_vendors(self, page_index=1, page_size=100):
        endpoint = "api/v2/AccountObjects"
        params = {
            "page": page_index,
            "pageSize": page_size,
            "isVendor": "true"
        }
        return self.call_api(endpoint, method="GET", params=params)

