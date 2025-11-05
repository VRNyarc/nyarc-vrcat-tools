"""
Core utilities for NYARC VRChat Tools.

This package contains shared utilities used across all modules:
- validation: Input validation and error checking
- mode_utils: Safe mode switching and context managers
- bone_utils: Bone iteration and common operations
- registry: Module registration system
- data_structures: Shared data classes
"""

# Import validation utilities
from .validation import (
    validate_scene_props,
    validate_armature,
    validate_mesh,
    validate_mode,
    validate_object_list,
    validate_property,
    validate_not_same_object,
    get_selected_objects,
)

# Import mode utilities
from .mode_utils import (
    safe_mode_switch,
    ensure_object_mode,
    ensure_edit_mode,
    ensure_pose_mode,
    switch_to_mode,
    get_current_mode,
    is_valid_mode_for_object,
    temporary_active_object,
    selection_guard,
)

# Import bone utilities
from .bone_utils import (
    iter_bones,
    get_bone,
    get_all_bone_names,
    bone_exists,
    get_selected_bones,
    get_bone_count,
    select_bone,
    deselect_all_bones,
    get_parent_bone,
    get_child_bones,
    get_bone_chain,
    bones_are_connected,
)

# Import existing modules
from .registry import ModuleRegistry, try_import_module

__all__ = [
    # Validation
    'validate_scene_props',
    'validate_armature',
    'validate_mesh',
    'validate_mode',
    'validate_object_list',
    'validate_property',
    'validate_not_same_object',
    'get_selected_objects',
    # Mode utilities
    'safe_mode_switch',
    'ensure_object_mode',
    'ensure_edit_mode',
    'ensure_pose_mode',
    'switch_to_mode',
    'get_current_mode',
    'is_valid_mode_for_object',
    'temporary_active_object',
    'selection_guard',
    # Bone utilities
    'iter_bones',
    'get_bone',
    'get_all_bone_names',
    'bone_exists',
    'get_selected_bones',
    'get_bone_count',
    'select_bone',
    'deselect_all_bones',
    'get_parent_bone',
    'get_child_bones',
    'get_bone_chain',
    'bones_are_connected',
    # Registry
    'ModuleRegistry',
    'try_import_module',
]
