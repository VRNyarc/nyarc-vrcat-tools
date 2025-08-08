# Save/Load Operators Bridge
# Imports save/load operators from bone_transform_saver module to avoid duplication

from ...core.registry import try_import_module

# Import save/load operators from the main saver module
saver_module, SAVER_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transform_saver', 'bone_transform_saver')

# Import diff export operator from io module  
diff_export_module, DIFF_EXPORT_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.io.diff_export', 'bone_transforms.io.diff_export')

SAVE_LOAD_CLASSES = []

if SAVER_AVAILABLE:
    # Import specific operator classes from bone_transform_saver
    if hasattr(saver_module, 'ARMATURE_OT_save_bone_transforms'):
        SAVE_LOAD_CLASSES.append(saver_module.ARMATURE_OT_save_bone_transforms)
    
    if hasattr(saver_module, 'ARMATURE_OT_load_bone_transforms'):
        SAVE_LOAD_CLASSES.append(saver_module.ARMATURE_OT_load_bone_transforms)
    
    if hasattr(saver_module, 'ARMATURE_OT_load_bone_transforms_confirmed'):
        SAVE_LOAD_CLASSES.append(saver_module.ARMATURE_OT_load_bone_transforms_confirmed)
    
    if hasattr(saver_module, 'ARMATURE_OT_delete_bone_transforms'):
        SAVE_LOAD_CLASSES.append(saver_module.ARMATURE_OT_delete_bone_transforms)
    
    print(f"[DEBUG] save_load.py - imported {len(SAVE_LOAD_CLASSES)} classes from bone_transform_saver")
else:
    print("[DEBUG] save_load.py - bone_transform_saver not available")

# Add diff export operator
if DIFF_EXPORT_AVAILABLE and hasattr(diff_export_module, 'ARMATURE_OT_export_armature_diff'):
    SAVE_LOAD_CLASSES.append(diff_export_module.ARMATURE_OT_export_armature_diff)
    print(f"[DEBUG] save_load.py - added export_armature_diff operator")

print(f"[DEBUG] save_load.py - total classes: {len(SAVE_LOAD_CLASSES)}")