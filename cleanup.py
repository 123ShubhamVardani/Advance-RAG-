#!/usr/bin/env python3
"""
Project cleanup and organization script
Removes redundant files and organizes the project structure
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up and organize the project"""
    
    print("🧹 Starting project cleanup...")
    
    # Files to keep
    keep_files = {
        'app_new.py',
        'requirements_clean.txt', 
        'README_new.md',
        '.env',
        '.gitignore',
        'LICENSE',
        'install.py',
        'TROUBLESHOOTING.md',
        'PROJECT_REVIEW.md'
    }
    
    # Directories to keep
    keep_dirs = {
        '.venv',
        'assets',
        'cache',
        'logs', 
        'uploads',
        '.git'
    }
    
    # Create directories if they don't exist
    for directory in ['cache', 'logs', 'uploads']:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Move cache files to cache directory
    cache_files = [f for f in os.listdir('.') if f.startswith('cache_') and f.endswith('.json')]
    for cache_file in cache_files:
        shutil.move(cache_file, f"cache/{cache_file}")
        print(f"📦 Moved {cache_file} to cache/")
    
    # Archive old files
    archive_dir = Path('archive')
    archive_dir.mkdir(exist_ok=True)
    
    # Files to archive (not delete)
    archive_files = [
        'app.py',
        'app_basic.py', 
        'app_original_backup.py',
        'requirements.txt',
        'README.md',
        'api_server.py',
        'database_manager.py',
        'load_balancer.py',
        'task_queue.py',
        'docker-compose.yml',
        'Dockerfile',
        'k8s-deployment.yaml'
    ]
    
    for file in archive_files:
        if os.path.exists(file):
            shutil.move(file, f"archive/{file}")
            print(f"📁 Archived: {file}")
    
    # Remove redundant requirements files
    redundant_files = [
        'requirements-basic.txt',
        'requirements-dev.txt', 
        'requirements-enterprise.txt',
        'requirements-production.txt',
        'test_offline.py',
        'test_env.py',
        'startup_debug.log',
        'chat_log.txt'
    ]
    
    for file in redundant_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Removed: {file}")
    
    # Rename main files
    if os.path.exists('app_new.py'):
        if os.path.exists('app.py'):
            shutil.move('app.py', 'archive/app_old.py')
        shutil.move('app_new.py', 'app.py')
        print("✅ app_new.py → app.py")
        # obsolete duplicates removed: app_new.py, README_new.md
    
    if os.path.exists('requirements_clean.txt'):
        if os.path.exists('requirements.txt'):
            shutil.move('requirements.txt', 'archive/requirements_old.txt')
        shutil.move('requirements_clean.txt', 'requirements.txt')
        print("✅ requirements_clean.txt → requirements.txt")
    
    if os.path.exists('README_new.md'):
        if os.path.exists('README.md'):
            shutil.move('README.md', 'archive/README_old.md')
        shutil.move('README_new.md', 'README.md')
        print("✅ README_new.md → README.md")
        # Removed duplicate migration logic for app_new.py / README_new.md (cleaned)
    
    print("\n🎉 Cleanup complete!")
    print("\n📁 Final project structure:")
    print("├── app.py                 # Main application")
    print("├── requirements.txt       # Dependencies")
    print("├── README.md             # Documentation")
    print("├── .env                  # Configuration")
    print("├── install.py            # Installation script")
    print("├── cache/                # Response cache")
    print("├── logs/                 # Application logs")
    print("├── uploads/              # Temporary uploads")
    print("├── assets/               # Images and assets")
    print("└── archive/              # Old files")
    
    print("\n🚀 Your project is now clean and organized!")
    print("Run: streamlit run app.py")

if __name__ == "__main__":
    cleanup_project()
