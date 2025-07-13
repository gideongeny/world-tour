#!/usr/bin/env python3
"""
World Tour - Railway Deployment Script
This script will help you deploy your app to Railway for FREE!
"""

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 WORLD TOUR - RAILWAY DEPLOYMENT")
    print("=" * 60)
    print("Your app will be deployed for FREE!")
    print("=" * 60)

def check_files():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'Procfile',
        'railway.json',
        'runtime.txt',
        'config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found!")
    return True

def create_github_repo():
    """Guide user to create GitHub repository"""
    print("\n📋 STEP 1: Create GitHub Repository")
    print("-" * 40)
    print("1. Go to https://github.com")
    print("2. Click 'New repository'")
    print("3. Name it: world-tour-app")
    print("4. Make it PUBLIC")
    print("5. Don't initialize with README")
    print("6. Click 'Create repository'")
    
    input("\nPress Enter when you've created the repository...")
    
    # Get repository URL
    repo_url = input("Enter your GitHub repository URL (e.g., https://github.com/username/world-tour-app): ")
    
    if not repo_url.startswith("https://github.com/"):
        print("❌ Invalid GitHub URL")
        return None
    
    return repo_url

def setup_remote_repo(repo_url):
    """Add remote repository and push code"""
    print("\n📋 STEP 2: Push Code to GitHub")
    print("-" * 40)
    
    try:
        # Add remote
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
        print("✅ Added remote repository")
        
        # Push to GitHub
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        print("✅ Pushed code to GitHub")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def deploy_to_railway():
    """Guide user through Railway deployment"""
    print("\n📋 STEP 3: Deploy to Railway")
    print("-" * 40)
    print("1. Go to https://railway.app")
    print("2. Click 'Sign Up' (use GitHub)")
    print("3. Click 'New Project'")
    print("4. Select 'Deploy from GitHub repo'")
    print("5. Choose your 'world-tour-app' repository")
    print("6. Click 'Deploy'")
    
    input("\nPress Enter when you've started the deployment...")
    
    print("\n📋 STEP 4: Add Database")
    print("-" * 40)
    print("1. In Railway dashboard, click 'New'")
    print("2. Select 'Database' → 'PostgreSQL'")
    print("3. Railway will automatically set DATABASE_URL")
    
    input("\nPress Enter when you've added the database...")
    
    print("\n📋 STEP 5: Set Environment Variables")
    print("-" * 40)
    print("In Railway dashboard, go to 'Variables' and add:")
    print("SECRET_KEY=your-super-secret-key-here-12345")
    print("FLASK_ENV=production")
    
    input("\nPress Enter when you've set the variables...")

def final_steps():
    """Final deployment steps"""
    print("\n📋 STEP 6: Final Setup")
    print("-" * 40)
    print("1. Wait for deployment to complete (2-3 minutes)")
    print("2. Click on your app URL in Railway")
    print("3. Register a new account")
    print("4. Test all features")
    
    print("\n🎉 YOUR APP IS LIVE!")
    print("=" * 60)
    print("✅ Free hosting on Railway")
    print("✅ PostgreSQL database included")
    print("✅ SSL certificate automatic")
    print("✅ Custom domain available")
    print("✅ Mobile app (PWA) ready")
    print("=" * 60)

def main():
    print_banner()
    
    # Check files
    if not check_files():
        print("❌ Please ensure all required files are present")
        return
    
    # Create GitHub repo
    repo_url = create_github_repo()
    if not repo_url:
        return
    
    # Setup remote and push
    if not setup_remote_repo(repo_url):
        print("❌ Failed to push to GitHub")
        return
    
    # Deploy to Railway
    deploy_to_railway()
    
    # Final steps
    final_steps()
    
    # Open Railway
    print("\n🌐 Opening Railway...")
    webbrowser.open("https://railway.app")

if __name__ == "__main__":
    main() 