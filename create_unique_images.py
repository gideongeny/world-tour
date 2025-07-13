from app import app, db, Destination
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(destination_name, country, filename):
    """Create a placeholder image with destination name and country"""
    try:
        # Create a new image with a gradient background
        width, height = 800, 600
        
        # Create gradient background
        image = Image.new('RGB', (width, height), color='#667eea')
        draw = ImageDraw.Draw(image)
        
        # Add gradient effect
        for y in range(height):
            r = int(102 + (y / height) * 30)  # 102 to 132
            g = int(126 + (y / height) * 30)  # 126 to 156
            b = int(234 + (y / height) * 30)  # 234 to 264
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add destination name
        try:
            # Try to use a larger font
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Calculate text position (center)
        text = destination_name
        bbox = draw.textbbox((0, 0), text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 30
        
        # Draw destination name
        draw.text((x, y), text, fill='white', font=font_large)
        
        # Add country name
        country_text = country
        bbox = draw.textbbox((0, 0), country_text, font=font_small)
        country_width = bbox[2] - bbox[0]
        country_x = (width - country_width) // 2
        country_y = y + text_height + 20
        
        draw.text((country_x, country_y), country_text, fill='#ffd700', font=font_small)
        
        # Add "Travel Destination" text
        travel_text = "Travel Destination"
        bbox = draw.textbbox((0, 0), travel_text, font=font_small)
        travel_width = bbox[2] - bbox[0]
        travel_x = (width - travel_width) // 2
        travel_y = country_y + 40
        
        draw.text((travel_x, travel_y), travel_text, fill='#ffffff', font=font_small)
        
        # Save the image
        filepath = os.path.join('static', filename)
        image.save(filepath, 'JPEG', quality=85)
        
        print(f"✅ Created placeholder: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to create placeholder {filename}: {e}")
        return False

def create_unique_images():
    with app.app_context():
        # Destinations that need unique images
        destinations_to_update = [
            ('Cairo', 'Egypt', 'cairo.jpg'),
            ('Marrakech', 'Morocco', 'marrakech.jpg'),
            ('Nairobi', 'Kenya', 'nairobi.jpg'),
            ('Bali', 'Indonesia', 'bali.jpg'),
            ('Dubai', 'UAE', 'dubai.jpg')
        ]
        
        print(f"\n=== CREATING UNIQUE IMAGES ===")
        print(f"Destinations to update: {len(destinations_to_update)}")
        
        # Create static directory if it doesn't exist
        if not os.path.exists('static'):
            os.makedirs('static')
        
        updated_count = 0
        
        for dest_name, country, filename in destinations_to_update:
            print(f"\n🔄 Creating unique image for: {dest_name}, {country}")
            print(f"   Filename: {filename}")
            
            if create_placeholder_image(dest_name, country, filename):
                # Update database
                dest = Destination.query.filter_by(name=dest_name).first()
                if dest:
                    dest.image_url = f"/static/{filename}"
                    updated_count += 1
                    print(f"   ✅ Updated database for {dest_name}")
                else:
                    print(f"   ❌ Destination not found in database: {dest_name}")
            else:
                print(f"   ❌ Failed to create image for {dest_name}")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n🎉 Successfully updated {updated_count} destinations!")
            print(f"📝 NOTE: These are placeholder images. You can manually replace them with real photos later.")
        except Exception as e:
            print(f"❌ Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_unique_images() 