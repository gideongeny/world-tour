import requests
try:
    print("Seeding database (GET)...")
    res = requests.get("https://world-tour-ngmj.onrender.com/seed")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text[:100]}...")
    
    # Verify count
    data = requests.get("https://world-tour-ngmj.onrender.com/booking/destinations?format=json").json()
    print(f"NEW COUNT: {len(data)}")
except Exception as e:
    print(f"ERROR: {e}")
