"""
Installation script for Spanish Deck Exporter Plugin
"""

import os
import shutil
import sys
import zipfile
from pathlib import Path


def get_anki_addons_folder():
    """Get the Anki addons folder for the current platform"""
    if sys.platform == "win32":
        return os.path.expanduser(r"~\AppData\Roaming\Anki2\addons21")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/Anki2/addons21")
    else:  # Linux
        return os.path.expanduser("~/.local/share/Anki2/addons21")


def create_plugin_package():
    """Create a .ankiaddon package file"""
    plugin_dir = Path("anki_deck_exporter")
    if not plugin_dir.exists():
        print("❌ Plugin directory not found!")
        return None
    
    # Create zip file
    package_name = "spanish_deck_exporter.ankiaddon"
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in plugin_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                arcname = file_path.relative_to(plugin_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created plugin package: {package_name}")
    return package_name


def install_plugin_manually():
    """Install plugin manually to Anki addons folder"""
    addons_folder = get_anki_addons_folder()
    
    if not os.path.exists(addons_folder):
        print(f"❌ Anki addons folder not found: {addons_folder}")
        print("Please make sure Anki is installed and has been run at least once.")
        return False
    
    plugin_dir = Path("anki_deck_exporter")
    if not plugin_dir.exists():
        print("❌ Plugin directory not found!")
        return False
    
    # Generate a unique addon ID (timestamp-based)
    import time
    addon_id = str(int(time.time()))
    
    target_dir = os.path.join(addons_folder, addon_id)
    
    try:
        # Copy plugin files
        shutil.copytree(plugin_dir, target_dir)
        print(f"✅ Plugin installed to: {target_dir}")
        print("🔄 Please restart Anki to activate the plugin")
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False


def main():
    print("🔧 Spanish Deck Exporter Plugin Installer")
    print()
    
    choice = input("Choose installation method:\n"
                  "1. Create .ankiaddon package (recommended)\n"
                  "2. Install directly to Anki folder\n"
                  "Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        package_file = create_plugin_package()
        if package_file:
            print()
            print("📦 Installation Instructions:")
            print(f"1. Open Anki")
            print(f"2. Go to Tools → Add-ons")
            print(f"3. Click 'Install from file...'")
            print(f"4. Select the file: {package_file}")
            print(f"5. Restart Anki")
    
    elif choice == "2":
        success = install_plugin_manually()
        if success:
            print()
            print("🎉 Plugin installed successfully!")
            print("Please restart Anki to activate the plugin.")
    
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()