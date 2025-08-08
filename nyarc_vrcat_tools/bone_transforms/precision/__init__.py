"""
Precision Correction Module for Amateur Diff Exports
Handles iterative precision correction for enhanced accuracy in complex bone inheritance scenarios
"""

# Import precision correction functions
try:
    from .correction_engine import (
        apply_precision_corrections,
        preset_has_precision_data,
        is_diff_export_preset
    )
    from .apply_rest_diff_calc import (
        save_shape_keys_for_diff_calc,
        restore_shape_keys_after_diff_calc,
        apply_rest_pose_diff_calc_only
    )
    PRECISION_AVAILABLE = True
except ImportError:
    PRECISION_AVAILABLE = False
    print("Warning: Precision correction module not available")

__all__ = [
    'apply_precision_corrections',
    'preset_has_precision_data', 
    'is_diff_export_preset',
    'save_shape_keys_for_diff_calc',
    'restore_shape_keys_after_diff_calc', 
    'apply_rest_pose_diff_calc_only',
    'PRECISION_AVAILABLE'
]