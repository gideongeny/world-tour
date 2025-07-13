from app import app, db, Destination

def test_travel_route():
    with app.app_context():
        # Simulate the travel route logic
        query = Destination.query.filter_by(available=True)
        destinations = query.order_by(Destination.rating.desc()).all()
        
        print(f"\n=== TRAVEL ROUTE TEST ===")
        print(f"Destinations returned by travel route: {len(destinations)}")
        print(f"First 10 destinations:")
        
        for i, dest in enumerate(destinations[:10], 1):
            print(f"{i:2d}. {dest.name}, {dest.country} - Rating: {dest.rating}")
        
        if len(destinations) > 10:
            print(f"... and {len(destinations) - 10} more destinations")
        
        # Check if there are any destinations with missing data
        print(f"\n=== CHECKING FOR MISSING DATA ===")
        for dest in destinations:
            if not dest.name or not dest.country or not dest.image_url:
                print(f"WARNING: {dest.id} - Missing data: name={dest.name}, country={dest.country}, image={dest.image_url}")

if __name__ == '__main__':
    test_travel_route() 