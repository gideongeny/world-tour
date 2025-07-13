from app import app, db, Destination

def check_destinations():
    with app.app_context():
        all_destinations = Destination.query.all()
        available_destinations = Destination.query.filter_by(available=True).all()
        
        print(f"\n=== DESTINATION STATUS ===")
        print(f"Total destinations: {len(all_destinations)}")
        print(f"Available destinations: {len(available_destinations)}")
        print(f"Unavailable destinations: {len(all_destinations) - len(available_destinations)}")
        
        print(f"\n=== UNAVAILABLE DESTINATIONS ===")
        unavailable = Destination.query.filter_by(available=False).all()
        for dest in unavailable:
            print(f"- {dest.name}, {dest.country} (ID: {dest.id})")
        
        print(f"\n=== AVAILABLE DESTINATIONS ===")
        for dest in available_destinations:
            print(f"- {dest.name}, {dest.country} (ID: {dest.id})")

if __name__ == '__main__':
    check_destinations() 