import requests
try:
    print("Seeding database...")
    res = requests.post("https://world-tour-ngmj.onrender.com/seed")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    # Verify count
    data = requests.get("https://world-tour-ngmj.onrender.com/booking/destinations?format=json").json()
    print(f"NEW COUNT: {len(data)}")
except Exception as e:
    print(f"ERROR: {e}")
