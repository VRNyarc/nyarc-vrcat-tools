# Preset File Management
# Handles the actual file operations for presets

import bpy
import json
import os
import platform
import subprocess

def get_presets_directory():
    """Get the presets directory path (creates if it doesn't exist)"""
    presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
    os.makedirs(presets_dir, exist_ok=True)
    return presets_dir

def open_presets_folder():
    """Open the presets folder in the OS file explorer (cross-platform)"""
    presets_dir = get_presets_directory()
    
    try:
        system = platform.system().lower()
        if system == "windows":
            # Windows: use explorer
            subprocess.run(['explorer', presets_dir], check=False)
        elif system == "darwin":  # macOS
            # macOS: use open command
            subprocess.run(['open', presets_dir], check=False)
        elif system == "linux":
            # Linux: try common file managers
            try:
                subprocess.run(['xdg-open', presets_dir], check=False)
            except FileNotFoundError:
                # Fallback to nautilus, dolphin, or thunar
                for fm in ['nautilus', 'dolphin', 'thunar', 'pcmanfm']:
                    try:
                        subprocess.run([fm, presets_dir], check=False)
                        break
                    except FileNotFoundError:
                        continue
        else:
            # Unknown system - return directory path for manual opening
            return f"Open manually: {presets_dir}"
        
        return f"Opened: {presets_dir}"
        
    except Exception as e:
        return f"Error opening folder: {str(e)}"

def get_available_presets():
    """Get list of available bone transform presets (newest first)"""
    presets = []
    presets_dir = get_presets_directory()
    
    if os.path.exists(presets_dir):
        # Get presets with their modification times
        preset_files = []
        for filename in os.listdir(presets_dir):
            if filename.endswith('.json'):
                preset_name = filename[:-5]  # Remove .json extension
                file_path = os.path.join(presets_dir, filename)
                mod_time = os.path.getmtime(file_path)
                preset_files.append((preset_name, mod_time))
        
        # Sort by modification time (newest first)
        preset_files.sort(key=lambda x: x[1], reverse=True)
        presets = [preset_name for preset_name, _ in preset_files]
    
    return presets

def save_preset_to_file(preset_name, preset_data):
    """Save preset data to file"""
    presets_dir = get_presets_directory()
    
    preset_file = os.path.join(presets_dir, f"{preset_name}.json")
    
    with open(preset_file, 'w') as f:
        json.dump(preset_data, f, indent=2)
    
    return preset_file

def load_preset_from_file(preset_name):
    """Load preset data from file"""
    presets_dir = get_presets_directory()
    preset_file = os.path.join(presets_dir, f"{preset_name}.json")
    
    if not os.path.exists(preset_file):
        raise FileNotFoundError(f"Preset '{preset_name}' not found")
    
    with open(preset_file, 'r') as f:
        preset_data = json.load(f)
    
    return preset_data

def delete_preset_file(preset_name):
    """Delete preset file"""
    presets_dir = get_presets_directory()
    preset_file = os.path.join(presets_dir, f"{preset_name}.json")
    
    if not os.path.exists(preset_file):
        raise FileNotFoundError(f"Preset '{preset_name}' not found")
    
    os.remove(preset_file)
    return True