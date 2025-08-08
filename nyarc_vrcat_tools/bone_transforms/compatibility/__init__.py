# VRChat Bone Compatibility Module
# Handles bone name matching and compatibility checking for VRChat avatars

from .vrchat_bones import (
    check_bone_compatibility,
    get_compatibility_warning_message,
    VRCHAT_STANDARD_BONES
)

__all__ = [
    'check_bone_compatibility',
    'get_compatibility_warning_message', 
    'VRCHAT_STANDARD_BONES'
]