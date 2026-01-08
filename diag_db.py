import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app import app, db
from new_models import Destination, Hotel, Flight

print("--- Diagnosing Backend Models ---")

with app.app_context():
    print(f"DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    print("\n[Destination Model]")
    print(f"Columns: {Destination.__table__.columns.keys()}")
    
    print("\n[Hotel Model]")
    print(f"Columns: {Hotel.__table__.columns.keys()}")
    
    print("\n[Flight Model]")
    print(f"Columns: {Flight.__table__.columns.keys()}")
    
    print("\nTesting Hotel constructor...")
    try:
        h = Hotel(
            name='Test Hotel', 
            location='Test Loc', 
            price=100.0, 
            rating=5.0, 
            destination_id=1, 
            image_url='http://test.jpg', 
            description='Test Desc'
        )
        print("Hotel construct success!")
        db.session.add(h)
        print("Hotel add to session success!")
        db.session.rollback()
        print("Hotel rollback success!")
    except Exception as e:
        print(f"FAILED to construct/add Hotel: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n--- Diagnostic Complete ---")
