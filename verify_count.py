import requests
try:
    data = requests.get("https://world-tour-ngmj.onrender.com/booking/destinations?format=json").json()
    print(f"COUNT: {len(data)}")
except Exception as e:
    print(f"ERROR: {e}")
