# Bone Transforms Operators Module
# All Blender operators for bone transformation functionality

from ...core.registry import try_import_module

# Try to import operator modules with graceful fallbacks
pose_mode_module, POSE_MODE_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.operators.pose_mode', 'bone_transforms.operators.pose_mode')
save_load_module, SAVE_LOAD_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.operators.save_load', 'bone_transforms.operators.save_load')
apply_rest_module, APPLY_REST_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.operators.apply_rest', 'bone_transforms.operators.apply_rest')
inherit_scale_module, INHERIT_SCALE_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.operators.inherit_scale', 'bone_transforms.operators.inherit_scale')
pose_history_operators_module, POSE_HISTORY_OPERATORS_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.pose_history.operators', 'bone_transforms.pose_history.operators')

# Collect all operator classes
OPERATOR_CLASSES = []

print(f"[DEBUG] Operators module - checking imports:")
print(f"[DEBUG] POSE_MODE_AVAILABLE: {POSE_MODE_AVAILABLE}")
print(f"[DEBUG] SAVE_LOAD_AVAILABLE: {SAVE_LOAD_AVAILABLE}")
print(f"[DEBUG] APPLY_REST_AVAILABLE: {APPLY_REST_AVAILABLE}")
print(f"[DEBUG] INHERIT_SCALE_AVAILABLE: {INHERIT_SCALE_AVAILABLE}")
print(f"[DEBUG] POSE_HISTORY_OPERATORS_AVAILABLE: {POSE_HISTORY_OPERATORS_AVAILABLE}")

if POSE_MODE_AVAILABLE and hasattr(pose_mode_module, 'POSE_MODE_CLASSES'):
    OPERATOR_CLASSES.extend(pose_mode_module.POSE_MODE_CLASSES)
    print(f"[DEBUG] Added {len(pose_mode_module.POSE_MODE_CLASSES)} pose mode classes")

if SAVE_LOAD_AVAILABLE and hasattr(save_load_module, 'SAVE_LOAD_CLASSES'):
    OPERATOR_CLASSES.extend(save_load_module.SAVE_LOAD_CLASSES)
    print(f"[DEBUG] Added {len(save_load_module.SAVE_LOAD_CLASSES)} save/load classes")

if APPLY_REST_AVAILABLE and hasattr(apply_rest_module, 'classes'):
    OPERATOR_CLASSES.extend(apply_rest_module.classes)
    print(f"[DEBUG] Added {len(apply_rest_module.classes)} apply_rest classes")

if INHERIT_SCALE_AVAILABLE and hasattr(inherit_scale_module, 'INHERIT_SCALE_CLASSES'):
    OPERATOR_CLASSES.extend(inherit_scale_module.INHERIT_SCALE_CLASSES)
    print(f"[DEBUG] Added {len(inherit_scale_module.INHERIT_SCALE_CLASSES)} inherit scale classes")

if POSE_HISTORY_OPERATORS_AVAILABLE and hasattr(pose_history_operators_module, 'classes'):
    OPERATOR_CLASSES.extend(pose_history_operators_module.classes)
    print(f"[DEBUG] Added {len(pose_history_operators_module.classes)} pose history classes")

print(f"[DEBUG] Total OPERATOR_CLASSES: {len(OPERATOR_CLASSES)}")