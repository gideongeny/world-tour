#!/usr/bin/env python3
"""
Automated Deployment Script for World Tour
Builds frontend, deploys to Firebase, and pushes to GitHub
"""
import os
import subprocess
import sys
import platform
from datetime import datetime

def check_command(cmd, install_cmd=None):
    """Check if a command is available, optionally install it"""
    try:
        subprocess.run([cmd, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        if install_cmd:
            print(f"⚠️ {cmd} not found. Installing...")
            try:
                subprocess.run(install_cmd, shell=True, check=True)
                return True
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {cmd}")
                return False
        return False

def run_command(command, description, cwd=None, shell=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("🚀 WORLD TOUR - Automated Deployment")
    print("=" * 60)
    print("This script will:")
    print("1. Build the frontend")
    print("2. Deploy to Firebase")
    print("3. Push to GitHub")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check Node.js
    if not check_command('node'):
        print("❌ Node.js is not installed or not in PATH")
        print("Please install Node.js 16+ and try again")
        sys.exit(1)
    
    # Check Python
    if not check_command('python') and not check_command('python3'):
        print("❌ Python is not installed or not in PATH")
        sys.exit(1)
    
    # Check Firebase CLI
    if not check_command('firebase', install_cmd='npm install -g firebase-tools'):
        print("❌ Firebase CLI is required for deployment")
        print("Install it manually: npm install -g firebase-tools")
        sys.exit(1)
    
    # Step 1: Install frontend dependencies
    frontend_node_modules = os.path.join('frontend', 'node_modules')
    if not os.path.exists(frontend_node_modules):
        if not run_command('npm install', 'Installing frontend dependencies', cwd='frontend'):
            sys.exit(1)
    else:
        print("✅ Frontend dependencies already installed")
    
    # Step 2: Build frontend
    if not run_command('npm run build', 'Building frontend', cwd='frontend'):
        sys.exit(1)
    
    # Step 3: Git add and commit
    print("\n📤 Step 3: Pushing to GitHub...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Deploy: Auto-deployment {timestamp}"
    
    # Add all changes
    run_command('git add .', 'Staging changes', shell=True)
    
    # Try to commit (might fail if no changes)
    try:
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
        print("✅ Changes committed")
    except subprocess.CalledProcessError:
        print("ℹ️ No changes to commit")
    
    # Push to GitHub
    if run_command('git push origin main', 'Pushing to GitHub', shell=True):
        print("✅ Pushed to GitHub successfully!")
    else:
        print("⚠️ Warning: Failed to push to GitHub. Continuing with Firebase deployment...")
    
    # Step 4: Deploy to Firebase
    print("\n🔥 Step 4: Deploying to Firebase...")
    if not run_command('firebase deploy --only hosting', 'Deploying to Firebase', shell=True):
        print("\n❌ Firebase deployment failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("Your website is now live on Firebase!")
    print("Backend is running automatically on Render")
    print("=" * 60)

if __name__ == '__main__':
    main()
