# Bone Transform Calculations Module
# Mathematical operations and transformations for bone manipulations

from ...core.registry import try_import_module

# Import diff export modules with graceful fallbacks
transforms_module, TRANSFORMS_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.diff_export.transforms_diff', 'bone_transforms.diff_export.transforms_diff')
armature_diff_module, ARMATURE_DIFF_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.diff_export.armature_diff', 'bone_transforms.diff_export.armature_diff')

# Re-export commonly used functions if available
if TRANSFORMS_AVAILABLE:
    try:
        from nyarc_vrcat_tools.bone_transforms.diff_export.transforms_diff import (
            apply_head_tail_transform_with_mesh_deformation,
            matrix_to_pose_transform,
            apply_armature_to_mesh_with_no_shape_keys,
            apply_armature_to_mesh_with_shape_keys
        )
    except ImportError:
        pass

if ARMATURE_DIFF_AVAILABLE:
    try:
        from nyarc_vrcat_tools.bone_transforms.diff_export.armature_diff import (
            get_armature_transforms,
            calculate_head_tail_differences,
            transforms_different
        )
    except ImportError:
        pass

# head_tail_diff.py removed - precision correction system supersedes the fallback approach

# Classes to be registered (empty for calculations module)
CALCULATION_CLASSES = []