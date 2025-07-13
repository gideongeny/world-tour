#!/usr/bin/env python3
"""
Image Optimization Script for World Tour Website
Compresses and optimizes all images in the static directory
"""

import os
import sys
from PIL import Image
import glob

def optimize_image(image_path, quality=85, max_size=(1920, 1080)):
    """
    Optimize a single image file
    
    Args:
        image_path (str): Path to the image file
        quality (int): JPEG quality (1-100)
        max_size (tuple): Maximum width and height
    """
    try:
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Get original file size
            original_size = os.path.getsize(image_path)
            
            # Save optimized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
            # Get new file size
            new_size = os.path.getsize(image_path)
            
            # Calculate savings
            savings = original_size - new_size
            savings_percent = (savings / original_size) * 100
            
            print(f"✅ {image_path}")
            print(f"   Original: {original_size:,} bytes")
            print(f"   Optimized: {new_size:,} bytes")
            print(f"   Savings: {savings:,} bytes ({savings_percent:.1f}%)")
            print()
            
            return savings
            
    except Exception as e:
        print(f"❌ Error optimizing {image_path}: {e}")
        return 0

def optimize_images_in_directory(directory="static", quality=85):
    """
    Optimize all images in a directory
    
    Args:
        directory (str): Directory to search for images
        quality (int): JPEG quality for optimization
    """
    # Supported image formats
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
    
    total_savings = 0
    total_files = 0
    
    print(f"🚀 Starting image optimization in {directory}/")
    print("=" * 50)
    
    # Find all image files
    image_files = []
    for ext in image_extensions:
        pattern = os.path.join(directory, ext)
        image_files.extend(glob.glob(pattern))
        # Also check subdirectories
        pattern = os.path.join(directory, "**", ext)
        image_files.extend(glob.glob(pattern, recursive=True))
    
    if not image_files:
        print("❌ No image files found!")
        return
    
    print(f"📁 Found {len(image_files)} image files")
    print()
    
    # Optimize each image
    for image_path in image_files:
        if os.path.isfile(image_path):
            savings = optimize_image(image_path, quality)
            total_savings += savings
            total_files += 1
    
    # Summary
    print("=" * 50)
    print(f"🎉 Optimization complete!")
    print(f"📊 Files processed: {total_files}")
    print(f"💰 Total space saved: {total_savings:,} bytes ({total_savings/1024/1024:.2f} MB)")
    
    if total_savings > 0:
        print(f"📈 Average savings per file: {total_savings/total_files:,.0f} bytes")

def create_webp_versions(directory="static"):
    """
    Create WebP versions of images for modern browsers
    """
    print(f"🔄 Creating WebP versions in {directory}/")
    print("=" * 50)
    
    # Find all JPEG and PNG files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        pattern = os.path.join(directory, ext)
        image_files.extend(glob.glob(pattern))
        pattern = os.path.join(directory, "**", ext)
        image_files.extend(glob.glob(pattern, recursive=True))
    
    webp_count = 0
    
    for image_path in image_files:
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Create WebP filename
                webp_path = os.path.splitext(image_path)[0] + '.webp'
                
                # Save as WebP
                img.save(webp_path, 'WEBP', quality=85, optimize=True)
                
                # Compare sizes
                original_size = os.path.getsize(image_path)
                webp_size = os.path.getsize(webp_path)
                savings = original_size - webp_size
                savings_percent = (savings / original_size) * 100
                
                print(f"✅ {webp_path}")
                print(f"   Original: {original_size:,} bytes")
                print(f"   WebP: {webp_size:,} bytes")
                print(f"   Savings: {savings:,} bytes ({savings_percent:.1f}%)")
                print()
                
                webp_count += 1
                
        except Exception as e:
            print(f"❌ Error creating WebP for {image_path}: {e}")
    
    print(f"🎉 Created {webp_count} WebP versions")

def main():
    """Main function"""
    print("🌍 World Tour Image Optimization Tool")
    print("=" * 50)
    
    # Check if static directory exists
    if not os.path.exists("static"):
        print("❌ Static directory not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Get optimization quality from command line or use default
    quality = 85
    if len(sys.argv) > 1:
        try:
            quality = int(sys.argv[1])
            if quality < 1 or quality > 100:
                print("❌ Quality must be between 1 and 100")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid quality value")
            sys.exit(1)
    
    print(f"🔧 Using quality setting: {quality}")
    print()
    
    # Optimize images
    optimize_images_in_directory("static", quality)
    
    print()
    
    # Ask if user wants WebP versions
    try:
        create_webp = input("🤔 Create WebP versions for modern browsers? (y/n): ").lower().strip()
        if create_webp in ['y', 'yes']:
            create_webp_versions("static")
    except KeyboardInterrupt:
        print("\n👋 Optimization cancelled")
    
    print()
    print("🎯 Next steps:")
    print("1. Update your HTML templates to use optimized images")
    print("2. Consider adding WebP support with fallbacks")
    print("3. Implement lazy loading for images below the fold")
    print("4. Test your website's performance improvement")

if __name__ == "__main__":
    main() 