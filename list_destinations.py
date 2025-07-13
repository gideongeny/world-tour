from app import app, db, Destination

def list_all_destinations():
    with app.app_context():
        destinations = Destination.query.all()
        print(f"\n=== ALL DESTINATIONS IN DATABASE ({len(destinations)} total) ===\n")
        
        for i, dest in enumerate(destinations, 1):
            print(f"{i:2d}. {dest.name}, {dest.country} - ${dest.price} ({dest.duration} days)")
            print(f"     Category: {dest.category}")
            print(f"     Climate: {dest.climate}")
            print()

if __name__ == '__main__':
    list_all_destinations() 