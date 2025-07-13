from app import app, db, Destination

def check_database():
    with app.app_context():
        print("=== CHECKING DATABASE FOR SPECIFIC DESTINATIONS ===")
        
        # Check specific destinations
        destinations_to_check = ['Cairo', 'Marrakech', 'Nairobi', 'Bali', 'Dubai']
        
        for dest_name in destinations_to_check:
            dest = Destination.query.filter_by(name=dest_name).first()
            if dest:
                print(f"\n{dest.name}, {dest.country}:")
                print(f"  Image URL: {dest.image_url}")
            else:
                print(f"\n❌ {dest_name} not found in database")
        
        print("\n=== ALL DESTINATIONS ===")
        all_dests = Destination.query.all()
        for dest in all_dests:
            print(f"{dest.name}, {dest.country} - {dest.image_url}")

if __name__ == '__main__':
    check_database() 