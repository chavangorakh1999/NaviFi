#!/usr/bin/env python3
"""
NaviFi API Setup Script
Installs essential packages and handles missing dependencies gracefully
"""

import subprocess
import sys
import importlib

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    print("🚀 NaviFi API Setup")
    print("=" * 40)
    
    # Essential packages for basic functionality
    essential_packages = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0", 
        "pydantic>=2.5.0",
        "requests>=2.31.0"
    ]
    
    # Optional packages for testing
    optional_packages = [
        "aiohttp>=3.9.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0"
    ]
    
    print("📦 Installing essential packages...")
    for package in essential_packages:
        package_name = package.split('>=')[0].split('[')[0]
        if not check_package(package_name):
            print(f"   Installing {package}...")
            if install_package(package):
                print(f"   ✅ {package_name} installed successfully")
            else:
                print(f"   ❌ Failed to install {package_name}")
                return False
        else:
            print(f"   ✅ {package_name} already installed")
    
    print("\n🔧 Checking optional packages...")
    missing_optional = []
    for package in optional_packages:
        package_name = package.split('>=')[0].split('[')[0]
        if not check_package(package_name):
            missing_optional.append(package)
            print(f"   ⚠️  {package_name} not installed (optional)")
        else:
            print(f"   ✅ {package_name} available")
    
    if missing_optional:
        print(f"\n📋 Optional packages not installed: {', '.join(missing_optional)}")
        print("   These are only needed for advanced testing features")
        print("   To install them: pip install " + " ".join(missing_optional))
    
    print("\n✅ Setup completed!")
    print("\n🚀 To start the API:")
    print("   python start_simple_api.py")
    print("\n🧪 To run basic tests:")
    print("   python quick_test.py")
    print("\n📚 API documentation will be available at:")
    print("   http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    main() 