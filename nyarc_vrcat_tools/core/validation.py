"""
Shared validation utilities for all operators.

Provides consistent validation patterns across the addon to ensure
operators receive valid inputs and provide helpful error messages.
"""

import bpy
from typing import Optional


def validate_scene_props(context, operator=None):
    """
    Validate that scene properties exist and are accessible.

    Args:
        context: Blender context
        operator: Optional operator to report errors to

    Returns:
        NyarcToolsProperties object if valid, None otherwise
    """
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        if operator:
            operator.report({'ERROR'}, "Addon properties not initialized. Try reloading the addon.")
        return None
    return props


def validate_armature(armature_obj, operator=None, check_valid=True, check_bones=False):
    """
    Validate armature object is valid and usable.

    Args:
        armature_obj: Object to validate
        operator: Optional operator to report errors to
        check_valid: Whether to check if object still exists in scene
        check_bones: Whether to check if armature has bones

    Returns:
        True if valid, False otherwise
    """
    if not armature_obj:
        if operator:
            operator.report({'ERROR'}, "No armature selected. Please select an armature in the panel.")
        return False

    if check_valid and armature_obj.name not in bpy.data.objects:
        if operator:
            operator.report({'ERROR'}, f"Armature '{armature_obj.name}' no longer exists in scene")
        return False

    if armature_obj.type != 'ARMATURE':
        if operator:
            operator.report({'ERROR'}, f"Selected object '{armature_obj.name}' is not an armature (type: {armature_obj.type})")
        return False

    if check_bones and not armature_obj.data.bones:
        if operator:
            operator.report({'ERROR'}, f"Armature '{armature_obj.name}' has no bones")
        return False

    return True


def validate_mesh(mesh_obj, operator=None, check_valid=True, check_shape_keys=False):
    """
    Validate mesh object is valid and usable.

    Args:
        mesh_obj: Object to validate
        operator: Optional operator to report errors to
        check_valid: Whether to check if object still exists in scene
        check_shape_keys: Whether to check if mesh has shape keys

    Returns:
        True if valid, False otherwise
    """
    if not mesh_obj:
        if operator:
            operator.report({'ERROR'}, "No mesh selected. Please select a mesh in the panel.")
        return False

    if check_valid and mesh_obj.name not in bpy.data.objects:
        if operator:
            operator.report({'ERROR'}, f"Mesh '{mesh_obj.name}' no longer exists in scene")
        return False

    if mesh_obj.type != 'MESH':
        if operator:
            operator.report({'ERROR'}, f"Selected object '{mesh_obj.name}' is not a mesh (type: {mesh_obj.type})")
        return False

    if check_shape_keys:
        if not mesh_obj.data.shape_keys:
            if operator:
                operator.report({'ERROR'}, f"Mesh '{mesh_obj.name}' has no shape keys")
            return False

    return True


def validate_mode(context, required_mode, operator=None):
    """
    Validate that Blender is in the required mode.

    Args:
        context: Blender context
        required_mode: Required mode ('OBJECT', 'EDIT', 'POSE', etc.)
        operator: Optional operator to report errors to

    Returns:
        True if in correct mode, False otherwise
    """
    if context.mode != required_mode:
        if operator:
            mode_names = {
                'OBJECT': 'Object Mode',
                'EDIT_MESH': 'Edit Mode',
                'POSE': 'Pose Mode',
                'EDIT_ARMATURE': 'Edit Mode (Armature)',
            }
            current = mode_names.get(context.mode, context.mode)
            required = mode_names.get(required_mode, required_mode)
            operator.report({'ERROR'}, f"This operation requires {required}. Currently in {current}.")
        return False
    return True


def validate_object_list(objects, object_type=None, operator=None, min_count=1, max_count=None):
    """
    Validate a list of objects.

    Args:
        objects: List of objects to validate
        object_type: Required object type (e.g., 'MESH', 'ARMATURE'), or None for any type
        operator: Optional operator to report errors to
        min_count: Minimum number of objects required
        max_count: Maximum number of objects allowed, or None for unlimited

    Returns:
        True if valid, False otherwise
    """
    if not objects or len(objects) < min_count:
        if operator:
            type_str = f"{object_type} " if object_type else ""
            operator.report({'ERROR'}, f"Please select at least {min_count} {type_str}object(s)")
        return False

    if max_count and len(objects) > max_count:
        if operator:
            type_str = f"{object_type} " if object_type else ""
            operator.report({'ERROR'}, f"Too many objects selected. Maximum {max_count} {type_str}object(s) allowed")
        return False

    if object_type:
        invalid = [obj for obj in objects if obj.type != object_type]
        if invalid:
            if operator:
                names = ', '.join([obj.name for obj in invalid[:3]])
                if len(invalid) > 3:
                    names += f" and {len(invalid) - 3} more"
                operator.report({'ERROR'}, f"Invalid object type(s): {names}. Expected {object_type}")
            return False

    return True


def validate_property(obj, prop_name, operator=None):
    """
    Validate that an object has a specific property.

    Args:
        obj: Object to check
        prop_name: Property name to validate
        operator: Optional operator to report errors to

    Returns:
        True if property exists, False otherwise
    """
    if not hasattr(obj, prop_name):
        if operator:
            operator.report({'ERROR'}, f"Object missing required property: {prop_name}")
        return False
    return True


def get_selected_objects(context, object_type=None):
    """
    Get selected objects, optionally filtered by type.

    Args:
        context: Blender context
        object_type: Filter by object type (e.g., 'MESH'), or None for all types

    Returns:
        List of selected objects
    """
    if object_type:
        return [obj for obj in context.selected_objects if obj.type == object_type]
    return list(context.selected_objects)


def validate_not_same_object(obj1, obj2, operator=None, obj1_name="source", obj2_name="target"):
    """
    Validate that two objects are not the same.

    Args:
        obj1: First object
        obj2: Second object
        operator: Optional operator to report errors to
        obj1_name: Name to use for first object in error message
        obj2_name: Name to use for second object in error message

    Returns:
        True if different objects, False if same
    """
    if obj1 == obj2:
        if operator:
            operator.report({'ERROR'}, f"The {obj1_name} and {obj2_name} cannot be the same object")
        return False
    return True
