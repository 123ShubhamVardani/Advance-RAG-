#!/usr/bin/env python3
"""
AI Chatbot - Installation and Setup Script
Handles dependency installation and project setup
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    if run_command(f"{sys.executable} -m venv .venv", "Virtual environment creation"):
        print("✅ Virtual environment created")
        return True
    return False

def install_dependencies():
    """Install required packages"""
    
    # Determine pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip"
        python_cmd = ".venv\\Scripts\\python"
    else:  # Linux/Mac
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    # Check if we have requirements.txt, otherwise use requirements_clean.txt
    requirements_file = "requirements.txt"
    if not Path(requirements_file).exists():
        requirements_file = "requirements_clean.txt"
    
    if not Path(requirements_file).exists():
        print("❌ No requirements file found")
        return False
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    success = run_command(
        f"{pip_cmd} install -r {requirements_file}",
        f"Installing dependencies from {requirements_file}"
    )
    
    if success:
        print("✅ All dependencies installed successfully")
        return True
    else:
        print("❌ Some dependencies failed to install")
        return False

def setup_project_structure():
    """Create necessary directories and files"""
    directories = ["cache", "logs", "uploads"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .env template if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_template = """# AI Chatbot Configuration
# Add your API keys here (at least one is required)

# Groq (Recommended - Free tier available)
GROQ_API_KEY=your_groq_api_key_here

# Google Gemini (Free tier available)  
GOOGLE_API_KEY=your_google_api_key_here

# HuggingFace (Free)
HUGGINGFACE_API_TOKEN=your_huggingface_token_here

# SerpAPI for web search (Optional)
SERPAPI_API_KEY=your_serpapi_key_here
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("✅ Created .env template file")
    else:
        print("✅ .env file already exists")

def show_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*50)
    print("🎉 Installation completed successfully!")
    print("="*50)
    
    print("\n📝 Next Steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Get API keys from:")
    print("   • Groq: https://console.groq.com")
    print("   • Google: https://aistudio.google.com")
    print("   • HuggingFace: https://huggingface.co/settings/tokens")
    print("   • SerpAPI: https://serpapi.com")
    
    print("\n🚀 Run the application:")
    if os.name == 'nt':  # Windows
        print("   .venv\\Scripts\\activate")
        print("   streamlit run app.py")
    else:  # Linux/Mac
        print("   source .venv/bin/activate")
        print("   streamlit run app.py")
    
    print("\n💡 Tips:")
    print("   • At least one AI provider API key is required")
    print("   • The app works in offline mode without API keys")
    print("   • Upload documents for RAG functionality")
    print("   • Check the README.md for detailed usage instructions")

def main():
    """Main installation process"""
    print("🤖 AI Chatbot Installation Script")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to setup virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️ Some dependencies failed, but continuing...")
    
    # Setup project structure
    setup_project_structure()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
