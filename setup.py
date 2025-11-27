#!/usr/bin/env python3
"""
Setup script for LangChain Chatbot with RAG & Voice
This script helps set up the development environment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    # Require Python 3.11 or newer for reliable runtime behavior
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.11+")
        return False

def create_venv():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path(".venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv .venv", "Creating virtual environment")

def activate_venv():
    """Get activation command for virtual environment"""
    if os.name == 'nt':  # Windows
        return r".\.venv\Scripts\activate"
    else:  # Unix/Linux/Mac
        return "source .venv/bin/activate"

def install_requirements():
    """Install requirements"""
    venv_python = ".venv\\Scripts\\python.exe" if os.name == 'nt' else ".venv/bin/python"
    
    # Try pyproject.toml first, then requirements.txt
    if Path("pyproject.toml").exists():
        return run_command(f"{venv_python} -m pip install -e .", "Installing from pyproject.toml")
    elif Path("requirements.txt").exists():
        return run_command(f"{venv_python} -m pip install -r requirements.txt", "Installing from requirements.txt")
    else:
        print("❌ No pyproject.toml or requirements.txt found")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    example_file = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file exists")
        return True
    elif example_file.exists():
        print("⚠️  .env file not found. Please copy env.example to .env and add your API keys")
        print("   Example: copy env.example .env")
        return False
    else:
        print("⚠️  No .env or env.example file found")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up LangChain Chatbot with RAG & Voice")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_venv():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Check environment file
    check_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print(f"1. Activate virtual environment: {activate_venv()}")
    if not Path(".env").exists():
        print("2. Copy env.example to .env and add your API keys")
        print("3. Run the app: python main.py or streamlit run app.py")
    else:
        print("2. Run the app: python main.py or streamlit run app.py")

if __name__ == "__main__":
    main()
