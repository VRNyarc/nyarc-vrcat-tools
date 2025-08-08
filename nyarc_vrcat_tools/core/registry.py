# Dynamic Module Registry System
# Handles graceful loading and registration of modular components

import bpy
from typing import Dict, List, Any, Optional
import importlib


class ModuleRegistry:
    """Singleton registry for managing modular addon components"""
    
    _instance = None
    
    def __init__(self):
        self.registered_modules: Dict[str, Dict] = {}
        self.available_modules: Dict[str, bool] = {}
        self.classes_to_register: List[Any] = []
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_module(self, module_info: Dict) -> bool:
        """Register a module and its components"""
        module_name = module_info['name']
        
        try:
            # Mark module as available
            self.available_modules[module_name] = True
            self.registered_modules[module_name] = module_info
            
            # Add classes to registration list
            if 'classes' in module_info:
                self.classes_to_register.extend(module_info['classes'])
            
            print(f"[OK] Registered module: {module_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to register module {module_name}: {e}")
            self.available_modules[module_name] = False
            return False
    
    def unregister_module(self, module_name: str):
        """Unregister a module and its components"""
        if module_name in self.registered_modules:
            del self.registered_modules[module_name]
        self.available_modules[module_name] = False
        print(f"[UNREGISTER] Unregistered module: {module_name}")
    
    def is_module_available(self, module_name: str) -> bool:
        """Check if a module is available and loaded"""
        return self.available_modules.get(module_name, False)
    
    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """Get information about a registered module"""
        return self.registered_modules.get(module_name)
    
    def register_all_classes(self):
        """Register all collected Blender classes"""
        for cls in self.classes_to_register:
            try:
                bpy.utils.register_class(cls)
            except Exception as e:
                print(f"[ERROR] Failed to register class {cls.__name__}: {e}")
    
    def unregister_all_classes(self):
        """Unregister all collected Blender classes"""
        for cls in reversed(self.classes_to_register):
            try:
                bpy.utils.unregister_class(cls)
            except Exception as e:
                print(f"[ERROR] Failed to unregister class {cls.__name__}: {e}")
        self.classes_to_register.clear()


def try_import_module(module_path: str, fallback_name: str = None) -> tuple:
    """
    Safely import a module with graceful fallback
    
    Returns:
        (module, is_available): Tuple of module and availability flag
    """
    try:
        module = importlib.import_module(module_path)
        return module, True
    except ImportError as e:
        name = fallback_name or module_path.split('.')[-1]
        print(f"[WARN] Warning: {name} not available - {e}")
        return None, False