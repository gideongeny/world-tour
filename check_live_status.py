
import requests
import json

BASE_URL = "https://world-tour-ngmj.onrender.com"

def check_endpoint(name, path, method="GET"):
    print(f"--- Checking {name} ---")
    try:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{path}", timeout=10)
        else:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
        
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            # snippet
            print(f"Data (snippet): {str(data)[:200]}")
            if isinstance(data, list):
                print(f"Count: {len(data)}")
        except:
            print(f"Content: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

check_endpoint("Health", "/healthz")
check_endpoint("Destinations", "/booking/destinations?format=json")
check_endpoint("Seed Database", "/seed", method="GET") # Try GET seed first as defined in some routes, or POST
