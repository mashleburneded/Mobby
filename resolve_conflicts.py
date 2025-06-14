#!/usr/bin/env python3
"""
Dependency Conflict Resolver for Möbius AI Assistant
Automatically detects and resolves package conflicts
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_conflicts():
    """Check for known conflicting packages"""
    print("🔍 Checking for conflicting packages...")
    
    conflicts = []
    
    # Check for ggshield
    success, stdout, stderr = run_command("pip show ggshield")
    if success:
        conflicts.append("ggshield (security scanner)")
    
    # Check for paradex-py
    success, stdout, stderr = run_command("pip show paradex-py")
    if success:
        conflicts.append("paradex-py (trading API)")
    
    # Check for realtime
    success, stdout, stderr = run_command("pip show realtime")
    if success:
        conflicts.append("realtime (real-time features)")
    
    return conflicts

def install_compatible():
    """Install compatible requirements"""
    print("📦 Installing compatible requirements...")
    
    if os.path.exists("requirements_compatible.txt"):
        print("Using requirements_compatible.txt...")
        success, stdout, stderr = run_command("pip install -r requirements_compatible.txt")
    elif os.path.exists("requirements_minimal.txt"):
        print("Using requirements_minimal.txt...")
        success, stdout, stderr = run_command("pip install -r requirements_minimal.txt")
    else:
        print("❌ No compatible requirements file found!")
        return False
    
    if success:
        print("✅ Installation successful!")
        return True
    else:
        print(f"❌ Installation failed: {stderr}")
        return False

def install_minimal():
    """Install only essential packages"""
    print("📦 Installing minimal requirements...")
    
    essential_packages = [
        "python-telegram-bot[job-queue]>=20.0,<22.0",
        "APScheduler>=3.10.0,<4.0",
        "pytz>=2023.3",
        "groq>=0.8.0",
        "openai>=1.12.0",
        "google-generativeai>=0.4.0",
        "anthropic>=0.20.0",
        "cryptography>=41.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "textblob>=0.17.0",
        "pycoingecko>=3.1.0",
        "web3>=6.15.0",
        "peewee>=3.16.0"
    ]
    
    for package in essential_packages:
        print(f"Installing {package}...")
        success, stdout, stderr = run_command(f"pip install '{package}'")
        if not success:
            print(f"⚠️ Failed to install {package}: {stderr}")
    
    print("✅ Minimal installation complete!")
    return True

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Test core imports
        import telegram
        import groq
        import requests
        import pandas
        import numpy
        print("✅ Core packages imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main conflict resolution workflow"""
    print("🚀 Möbius AI Assistant - Dependency Conflict Resolver")
    print("=" * 60)
    
    # Check for conflicts
    conflicts = check_conflicts()
    
    if conflicts:
        print(f"⚠️ Found conflicting packages: {', '.join(conflicts)}")
        print("\nChoose resolution method:")
        print("1. Install compatible versions (recommended)")
        print("2. Install minimal packages only")
        print("3. Exit and use virtual environment")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            success = install_compatible()
        elif choice == "2":
            success = install_minimal()
        elif choice == "3":
            print("\n📋 Virtual Environment Instructions:")
            print("python -m venv mobius_env")
            print("source mobius_env/bin/activate  # On Windows: mobius_env\\Scripts\\activate")
            print("pip install -r requirements.txt")
            return
        else:
            print("❌ Invalid choice!")
            return
    else:
        print("✅ No conflicts detected! Installing full requirements...")
        success, stdout, stderr = run_command("pip install -r requirements.txt")
        if not success:
            print(f"❌ Installation failed: {stderr}")
            print("Trying compatible version...")
            success = install_compatible()
    
    # Test installation
    if success:
        if test_installation():
            print("\n🎉 Installation successful! You can now run:")
            print("python src/main.py")
        else:
            print("\n⚠️ Installation completed but some imports failed.")
            print("Try running: python test_all_commands.py")
    else:
        print("\n❌ Installation failed. Please try manual installation:")
        print("pip install python-telegram-bot groq openai requests pandas numpy")

if __name__ == "__main__":
    main()