#!/usr/bin/env python3
"""
Script to update all config imports to use the new unified settings
"""
import re
from pathlib import Path

def update_file(file_path: Path) -> bool:
    """Update imports in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace import statements
    replacements = [
        # Replace postgres_config imports
        (r'from app\.core\.postgres_config import settings', 'from app.core.settings import settings'),
        (r'from app\.core\.postgres_config import PostgreSQLSettings', 'from app.core.settings import Settings'),
        (r'import app\.core\.postgres_config', 'import app.core.settings'),
        
        # Replace config imports
        (r'from app\.core\.config import settings', 'from app.core.settings import settings'),
        (r'from app\.core\.config import Settings', 'from app.core.settings import Settings'),
        (r'import app\.core\.config', 'import app.core.settings'),
        
        # Replace production_config imports
        (r'from app\.core\.production_config import production_settings', 'from app.core.settings import settings'),
        (r'from app\.core\.production_config import ProductionSettings', 'from app.core.settings import ProductionSettings'),
        (r'import app\.core\.production_config', 'import app.core.settings'),
        
        # Replace any remaining references
        (r'app\.core\.postgres_config\.settings', 'app.core.settings.settings'),
        (r'app\.core\.config\.settings', 'app.core.settings.settings'),
        (r'app\.core\.production_config\.production_settings', 'app.core.settings.settings'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Update all Python files in the backend"""
    backend_dir = Path(__file__).parent.parent
    updated_files = []
    
    # Find all Python files
    for py_file in backend_dir.rglob("*.py"):
        # Skip the new settings file itself
        if py_file.name == "settings.py" and "app/core" in str(py_file):
            continue
        
        # Skip this script
        if py_file.name == "update_config_imports.py":
            continue
            
        # Skip old config files
        if py_file.name in ["config.py", "postgres_config.py", "production_config.py"] and "app/core" in str(py_file):
            continue
        
        if update_file(py_file):
            updated_files.append(py_file)
            print(f"✅ Updated: {py_file.relative_to(backend_dir)}")
    
    print(f"\n📊 Summary: Updated {len(updated_files)} files")
    
    if updated_files:
        print("\n📝 Updated files:")
        for f in sorted(updated_files):
            print(f"  - {f.relative_to(backend_dir)}")

if __name__ == "__main__":
    main()