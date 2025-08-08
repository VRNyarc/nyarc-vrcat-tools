# Bone Transforms Module
# Complete bone transformation workflow for VRChat avatars

from ..core.registry import ModuleRegistry, try_import_module

# Module information
MODULE_INFO = {
    'name': 'bone_transforms',
    'version': '1.0.0',
    'description': 'Bone transformation tools for VRChat avatars',
    'dependencies': ['core'],
    'classes': []
}

# Try to import all submodules with graceful fallbacks
operators_module, OPERATORS_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.operators', 'bone_transforms.operators')
diff_export_module, DIFF_EXPORT_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.diff_export', 'bone_transforms.diff_export')
io_module, IO_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.io', 'bone_transforms.io')
ui_module, UI_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.ui', 'bone_transforms.ui')
presets_module, PRESETS_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.presets', 'bone_transforms.presets')
pose_history_module, POSE_HISTORY_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.pose_history', 'bone_transforms.pose_history')

def register_module():
    """Register the bone transforms module"""
    import bpy
    
    # Debug import status
    print(f"[DEBUG] PRESETS_AVAILABLE: {PRESETS_AVAILABLE}")
    print(f"[DEBUG] POSE_HISTORY_AVAILABLE: {POSE_HISTORY_AVAILABLE}")
    
    if PRESETS_AVAILABLE:
        print(f"[DEBUG] presets_module attributes: {dir(presets_module)}")
        print(f"[DEBUG] Has SCROLL_CLASSES: {hasattr(presets_module, 'SCROLL_CLASSES')}")
        if hasattr(presets_module, 'SCROLL_CLASSES'):
            print(f"[DEBUG] SCROLL_CLASSES content: {presets_module.SCROLL_CLASSES}")
    
    if POSE_HISTORY_AVAILABLE:
        print(f"[DEBUG] pose_history_module loaded successfully")
        print(f"[DEBUG] pose_history functions: {[name for name in dir(pose_history_module) if not name.startswith('_')]}")
    else:
        print(f"[DEBUG] pose_history_module failed to load")
    
    # Collect all classes from available submodules
    all_classes = []
    
    if OPERATORS_AVAILABLE and hasattr(operators_module, 'OPERATOR_CLASSES'):
        all_classes.extend(operators_module.OPERATOR_CLASSES)
        print(f"[DEBUG] Added {len(operators_module.OPERATOR_CLASSES)} operator classes")
    
    if UI_AVAILABLE and hasattr(ui_module, 'UI_CLASSES'):
        all_classes.extend(ui_module.UI_CLASSES)
        print(f"[DEBUG] Added {len(ui_module.UI_CLASSES)} UI classes")
    
    if PRESETS_AVAILABLE and hasattr(presets_module, 'SCROLL_CLASSES'):
        all_classes.extend(presets_module.SCROLL_CLASSES)
        print(f"[DEBUG] Added {len(presets_module.SCROLL_CLASSES)} scroll classes")
    
    print(f"[DEBUG] Total classes to register: {len(all_classes)}")
    
    # Register classes directly with Blender
    for cls in all_classes:
        try:
            bpy.utils.register_class(cls)
            print(f"[OK] Registered {cls.__name__} (bl_idname: {getattr(cls, 'bl_idname', 'N/A')})")
        except Exception as e:
            print(f"[ERROR] Failed to register {cls.__name__}: {e}")
    
    # Store for unregistration
    MODULE_INFO['classes'] = all_classes
    
    # Also register with registry for tracking
    registry = ModuleRegistry.get_instance()
    registry.register_module(MODULE_INFO)

def unregister_module():
    """Unregister the bone transforms module"""
    import bpy
    
    # Unregister classes directly from Blender
    if 'classes' in MODULE_INFO:
        for cls in reversed(MODULE_INFO['classes']):
            try:
                bpy.utils.unregister_class(cls)
                print(f"[OK] Unregistered {cls.__name__}")
            except Exception as e:
                print(f"[ERROR] Failed to unregister {cls.__name__}: {e}")
    
    # Also unregister from registry
    registry = ModuleRegistry.get_instance()
    registry.unregister_module('bone_transforms')