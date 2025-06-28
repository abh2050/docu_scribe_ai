#!/usr/bin/env python3
"""
DocuScribe AI Setup Script
Run this script to set up your DocuScribe AI environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🩺 DocuScribe AI - Setup Script")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detected")
    print()

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        print("Please install manually: pip install -r requirements.txt")
        sys.exit(1)
    print()

def setup_environment():
    """Set up environment file"""
    print("Setting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys before running the application")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example file found")
    print()

def verify_structure():
    """Verify project structure"""
    print("Verifying project structure...")
    
    required_dirs = ["agents", "data", "utils"]
    required_files = ["app.py", "requirements.txt"]
    
    all_good = True
    
    for directory in required_dirs:
        if Path(directory).is_dir():
            print(f"✅ {directory}/ directory found")
        else:
            print(f"❌ {directory}/ directory missing")
            all_good = False
    
    for file in required_files:
        if Path(file).is_file():
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            all_good = False
    
    if all_good:
        print("✅ Project structure verified")
    else:
        print("❌ Some files/directories are missing")
        print("Please ensure you have the complete project structure")
    print()

def show_next_steps():
    """Show next steps to user"""
    print("🚀 Setup Complete!")
    print("Next steps:")
    print("1. Edit .env file with your API keys:")
    print("   - OPENAI_API_KEY=your_key_here")
    print("   - GOOGLE_API_KEY=your_key_here")
    print("   - ANTHROPIC_API_KEY=your_key_here")
    print()
    print("2. Run the application:")
    print("   streamlit run app.py")
    print()
    print("3. Open your browser to:")
    print("   http://localhost:8501")
    print()
    print("For help, see README.md or visit: https://github.com/docuscribe-ai")
    print("=" * 60)

def main():
    """Main setup function"""
    print_header()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    check_python_version()
    verify_structure()
    install_dependencies()
    setup_environment()
    show_next_steps()

if __name__ == "__main__":
    main()
