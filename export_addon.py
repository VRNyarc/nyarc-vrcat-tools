#!/usr/bin/env python3
"""
Export Blender Addon Script
Creates a ZIP file of the addon with custom or timestamped name
"""

import os
import zipfile
import datetime
import sys
import argparse

def export_addon(custom_name=None):
    """Export the nyarc_vrcat_tools addon to exported_zips folder"""
    
    # Define paths
    addon_dir = "nyarc_vrcat_tools"  # Addon files are now in this subdirectory
    export_dir = "exported_zips"
    
    # Check if addon directory exists
    if not os.path.exists(addon_dir):
        raise FileNotFoundError(f"Addon directory '{addon_dir}' not found. Make sure you're in the project root.")
    
    # Generate zip name based on custom name or default with timestamp
    if custom_name:
        # Ensure .zip extension
        if not custom_name.endswith('.zip'):
            custom_name += '.zip'
        zip_name = custom_name
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"nyarc_vrcat_tools_{timestamp}.zip"
    
    zip_path = os.path.join(export_dir, zip_name)
    
    # Ensure export directory exists
    os.makedirs(export_dir, exist_ok=True)
    
    print(f"Exporting addon to: {zip_path}")
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the nyarc_vrcat_tools directory and include all Python files
        for root, dirs, files in os.walk(addon_dir):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git'} and not d.startswith('.')]
            
            for file in files:
                # Include all Python files from the addon directory
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    # Create archive path - maintain the nyarc_vrcat_tools structure
                    rel_path = os.path.relpath(file_path, '.')
                    zipf.write(file_path, rel_path)
                    print(f"  Added: {rel_path}")
    
    print(f"[OK] Addon exported successfully: {zip_name}")
    print(f"[INFO] Install in Blender via: Edit > Preferences > Add-ons > Install...")
    return zip_path

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Export Blender addon to ZIP file')
    parser.add_argument('name', nargs='?', help='Custom name for the ZIP file (optional)')
    parser.add_argument('--name', '-n', dest='custom_name', help='Custom name for the ZIP file')
    
    args = parser.parse_args()
    
    # Use positional argument if provided, otherwise use --name flag
    custom_name = args.name or args.custom_name
    
    return export_addon(custom_name)

if __name__ == "__main__":
    main()