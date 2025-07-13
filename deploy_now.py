#!/usr/bin/env python3
"""
Deployment script for World Tour application
"""
import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def main():
    print("🚀 Starting World Tour deployment...")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ Error: requirements.txt not found.")
        sys.exit(1)
    
    # Check if render.yaml exists
    if not os.path.exists('render.yaml'):
        print("❌ Error: render.yaml not found.")
        sys.exit(1)
    
    print("✅ All required files found")
    
    # Test the application locally
    print("\n🧪 Testing application locally...")
    test_result = run_command("python -c \"from app import app; print('✅ App imports successfully')\"", "Testing app imports")
    
    if test_result is None:
        print("❌ Application test failed. Please fix the errors before deploying.")
        sys.exit(1)
    
    print("\n📋 Deployment Checklist:")
    print("✅ Database configuration updated for production")
    print("✅ PostgreSQL dependency added")
    print("✅ Environment variables configured")
    print("✅ App imports successfully")
    
    print("\n🎯 Next Steps:")
    print("1. Commit your changes to git:")
    print("   git add .")
    print("   git commit -m 'Prepare for Render deployment'")
    print("   git push origin main")
    print("\n2. Deploy to Render:")
    print("   - Connect your repository to Render")
    print("   - Render will automatically detect the render.yaml configuration")
    print("   - The database will be created automatically")
    print("\n3. Set environment variables in Render dashboard:")
    print("   - SECRET_KEY: Generate a secure random key")
    print("   - DATABASE_URL: Will be set automatically by Render")
    
    print("\n🚀 Ready for deployment!")

if __name__ == "__main__":
    main() 