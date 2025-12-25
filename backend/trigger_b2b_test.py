
import requests
import json

def trigger_b2b():
    print("Triggering B2B Rolling Calculation...")
    url = "http://localhost:8000/api/planning/rolling/run"
    payload = {
        "horizon_months": 12,
        "profile_id": "B2B"
    }
    
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("Success:", res.json())
        else:
            print(f"Failed: {res.status_code}", res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_b2b()
