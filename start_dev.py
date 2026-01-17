#!/usr/bin/env python3
"""
World Tour - Development Server Starter
Runs both Flask backend and Vite frontend simultaneously
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def check_command(cmd):
    """Check if a command is available"""
    try:
        subprocess.run([cmd, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_dependencies():
    """Install npm dependencies if needed"""
    # Check frontend dependencies
    frontend_node_modules = Path('frontend/node_modules')
    if not frontend_node_modules.exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd='frontend', check=True)
    
    # Check root dependencies (concurrently)
    root_node_modules = Path('node_modules')
    if not root_node_modules.exists():
        print("📦 Installing root dependencies...")
        subprocess.run(['npm', 'install'], check=True)

def main():
    print("=" * 60)
    print("🚀 WORLD TOUR - Starting Development Server")
    print("=" * 60)
    print("Starting both Backend (Flask) and Frontend (Vite)...")
    print("=" * 60)
    print()
    
    # Check Python
    if not check_command('python') and not check_command('python3'):
        print("❌ Python is not installed or not in PATH")
        print("Please install Python 3.8+ and try again")
        sys.exit(1)
    
    python_cmd = 'python3' if check_command('python3') else 'python'
    
    # Check Node.js
    if not check_command('node'):
        print("❌ Node.js is not installed or not in PATH")
        print("Please install Node.js 16+ and try again")
        sys.exit(1)
    
    # Check npm
    if not check_command('npm'):
        print("❌ npm is not installed or not in PATH")
        print("Please install npm and try again")
        sys.exit(1)
    
    # Install dependencies
    try:
        install_dependencies()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)
    
    print()
    print("✅ All dependencies installed!")
    print()
    print("🎯 Starting services...")
    print("  - Backend: http://localhost:5000")
    print("  - Frontend: http://localhost:5173")
    print()
    print("Press Ctrl+C to stop both services")
    print("=" * 60)
    print()
    
    # Check if concurrently is available
    try:
        subprocess.run(['npx', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # Start both services using concurrently
        backend_cmd = f'{python_cmd} app.py'
        frontend_cmd = 'cd frontend && npm run dev'
        
        if platform.system() == 'Windows':
            # Windows uses different shell
            subprocess.run([
                'npx', 'concurrently',
                '--kill-others',
                '--prefix-colors', 'blue,green',
                '--prefix', '{name}',
                '--names', 'BACKEND,FRONTEND',
                backend_cmd,
                frontend_cmd
            ])
        else:
            # Unix-like systems
            subprocess.run([
                'npx', 'concurrently',
                '--kill-others',
                '--prefix-colors', 'blue,green',
                '--prefix', '{name}',
                '--names', 'BACKEND,FRONTEND',
                backend_cmd,
                frontend_cmd
            ])
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
