#!/usr/bin/env python3
"""
Image Optimization Script for World Tour Website
This script compresses and optimizes images for better loading performance.
"""

import os
import sys
from PIL import Image
import requests
from io import BytesIO

def optimize_image(input_path, output_path, max_width=1200, quality=85):
    """Optimize a single image"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_width = max_width
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # Get file sizes
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            savings = ((original_size - optimized_size) / original_size) * 100
            
            print(f"✓ {os.path.basename(input_path)}: {original_size/1024:.1f}KB → {optimized_size/1024:.1f}KB ({savings:.1f}% smaller)")
            
            return True
    except Exception as e:
        print(f"✗ Error optimizing {input_path}: {e}")
        return False

def create_webp_version(input_path, output_path, quality=80):
    """Create WebP version of image"""
    try:
        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save as WebP
            img.save(output_path, 'WEBP', quality=quality, optimize=True)
            
            webp_size = os.path.getsize(output_path)
            print(f"  ↳ WebP: {webp_size/1024:.1f}KB")
            
            return True
    except Exception as e:
        print(f"  ✗ WebP creation failed: {e}")
        return False

def optimize_all_images():
    """Optimize all images in the static folder"""
    static_dir = "static"
    optimized_dir = "static/optimized"
    
    # Create optimized directory if it doesn't exist
    if not os.path.exists(optimized_dir):
        os.makedirs(optimized_dir)
    
    # Image files to optimize
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    total_original_size = 0
    total_optimized_size = 0
    processed_count = 0
    
    print("Starting image optimization...\n")
    
    for filename in os.listdir(static_dir):
        if filename.lower().endswith(image_extensions):
            input_path = os.path.join(static_dir, filename)
            output_path = os.path.join(optimized_dir, filename)
            
            # Skip if already optimized
            if os.path.exists(output_path):
                print(f"Skipping {filename} - already optimized...")
                continue
            
            # Get original file size
            original_size = os.path.getsize(input_path)
            total_original_size += original_size
            
            # Optimize image
            if optimize_image(input_path, output_path):
                optimized_size = os.path.getsize(output_path)
                total_optimized_size += optimized_size
                processed_count += 1
                
                # Create WebP version
                webp_path = output_path.rsplit('.', 1)[0] + '.webp'
                create_webp_version(input_path, webp_path)
    
    # Summary
    print(f"\nOptimization Summary:")
    print(f"   Processed: {processed_count} images")
    if total_original_size > 0:
        print(f"   Original size: {total_original_size/1024/1024:.1f}MB")
        print(f"   Optimized size: {total_optimized_size/1024/1024:.1f}MB")
        print(f"   Total savings: {((total_original_size - total_optimized_size) / total_original_size) * 100:.1f}%")
    else:
        print("   No images were processed")
    
    return processed_count > 0

def create_responsive_images():
    """Create responsive image versions"""
    static_dir = "static"
    responsive_dir = "static/responsive"
    
    if not os.path.exists(responsive_dir):
        os.makedirs(responsive_dir)
    
    # Responsive breakpoints
    breakpoints = {
        'small': 480,
        'medium': 768,
        'large': 1200
    }
    
    print("\nCreating responsive images...")
    
    for filename in os.listdir(static_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            input_path = os.path.join(static_dir, filename)
            
            with Image.open(input_path) as img:
                width, height = img.size
                
                for size_name, max_width in breakpoints.items():
                    if width > max_width:
                        # Calculate new dimensions
                        ratio = max_width / width
                        new_width = max_width
                        new_height = int(height * ratio)
                        
                        # Resize image
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Create filename
                        name, ext = os.path.splitext(filename)
                        responsive_filename = f"{name}-{size_name}{ext}"
                        output_path = os.path.join(responsive_dir, responsive_filename)
                        
                        # Save resized image
                        resized_img.save(output_path, 'JPEG', quality=85, optimize=True)
                        print(f"  ✓ {responsive_filename}: {new_width}x{new_height}")

def update_html_for_optimized_images():
    """Update HTML templates to use optimized images"""
    print("\nUpdating HTML for optimized images...")
    
    # This would update the templates to use responsive images
    # For now, we'll create a simple replacement guide
    replacements = {
        'modern.jpg': 'optimized/modern.jpg',
        'luxury.jpg': 'optimized/luxury.jpg',
        'minimalist.jpg': 'optimized/minimalist.jpg'
    }
    
    print("Replace image paths in templates:")
    for old, new in replacements.items():
        print(f"  {old} → {new}")

def main():
    """Main function"""
    print("World Tour Image Optimization Tool")
    print("=" * 50)
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("❌ Pillow (PIL) is required. Install with: pip install Pillow")
        sys.exit(1)
    
    # Optimize images
    if optimize_all_images():
        # Create responsive versions
        create_responsive_images()
        
        # Update HTML guidance
        update_html_for_optimized_images()
        
        print("\nImage optimization completed!")
        print("\n📝 Next steps:")
        print("1. Update image paths in templates to use optimized versions")
        print("2. Consider implementing lazy loading for images")
        print("3. Add WebP support with fallbacks")
        print("4. Implement responsive images with srcset")
    else:
        print("\nNo images were processed.")

if __name__ == "__main__":
    main() 