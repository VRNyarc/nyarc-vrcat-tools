# Bone Transforms I/O Module
# Import/export functionality for bone transformation data

from ...core.registry import try_import_module

# Try to import I/O modules with graceful fallbacks
presets_module, PRESETS_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.io.presets', 'bone_transforms.io.presets')
diff_export_module, DIFF_EXPORT_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.io.diff_export', 'bone_transforms.io.diff_export')

# Re-export commonly used functions if available
if PRESETS_AVAILABLE:
    try:
        from nyarc_vrcat_tools.bone_transforms.io.presets import load_bone_transforms_internal
    except ImportError:
        pass

if DIFF_EXPORT_AVAILABLE:
    try:
        from nyarc_vrcat_tools.bone_transforms.io.diff_export import ARMATURE_OT_export_armature_diff
    except ImportError:
        pass

# Classes to be registered
IO_CLASSES = []
if DIFF_EXPORT_AVAILABLE and hasattr(diff_export_module, 'ARMATURE_OT_export_armature_diff'):
    IO_CLASSES.append(diff_export_module.ARMATURE_OT_export_armature_diff)