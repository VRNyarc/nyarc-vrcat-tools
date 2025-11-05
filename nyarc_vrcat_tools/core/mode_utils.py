"""
Safe mode switching utilities.

Provides context managers and utilities for safely switching between
Blender modes (Object, Edit, Pose, etc.) with automatic cleanup and
error handling.
"""

import bpy
from contextlib import contextmanager
from typing import Optional


@contextmanager
def safe_mode_switch(obj, target_mode: str):
    """
    Context manager for safe mode switching with automatic restoration.

    Switches to target mode, yields, then restores original mode and active object.
    Handles errors gracefully and ensures cleanup even on exceptions.

    Args:
        obj: Object to switch mode for
        target_mode: Target mode ('OBJECT', 'EDIT', 'POSE', etc.)

    Yields:
        bool: True if mode switch successful, False otherwise

    Example:
        >>> with safe_mode_switch(armature, 'POSE') as success:
        ...     if success:
        ...         # Do pose mode operations
        ...         pass
    """
    if not obj:
        yield False
        return

    original_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    original_active = bpy.context.view_layer.objects.active
    success = False

    try:
        # Set as active object
        bpy.context.view_layer.objects.active = obj

        # Switch to target mode if not already in it
        if bpy.context.object and bpy.context.object.mode != target_mode:
            bpy.ops.object.mode_set(mode=target_mode)

        success = True
        yield True

    except (RuntimeError, TypeError, AttributeError) as e:
        print(f"Mode switch to {target_mode} failed: {e}")
        yield False

    finally:
        # Restore original state (best effort)
        try:
            # Only restore if we successfully switched
            if success and bpy.context.object:
                current_mode = bpy.context.object.mode
                if current_mode != original_mode:
                    bpy.ops.object.mode_set(mode=original_mode)

            # Restore original active object
            if original_active and original_active.name in bpy.data.objects:
                bpy.context.view_layer.objects.active = original_active

        except (RuntimeError, TypeError, AttributeError) as e:
            # Best effort - log but don't raise
            print(f"Failed to restore original mode/active object: {e}")


@contextmanager
def ensure_object_mode(obj=None):
    """
    Context manager to ensure Object mode for operations.

    Args:
        obj: Optional object to make active before switching

    Yields:
        bool: True if successfully in object mode

    Example:
        >>> with ensure_object_mode(armature):
        ...     # Safely in object mode
        ...     bpy.ops.object.select_all(action='DESELECT')
    """
    if obj:
        with safe_mode_switch(obj, 'OBJECT') as success:
            yield success
    else:
        # Just switch mode without changing active object
        original_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
        try:
            if bpy.context.object and original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            yield True
        except (RuntimeError, TypeError, AttributeError) as e:
            print(f"Failed to switch to object mode: {e}")
            yield False
        finally:
            try:
                if bpy.context.object and bpy.context.object.mode != original_mode:
                    bpy.ops.object.mode_set(mode=original_mode)
            except (RuntimeError, TypeError, AttributeError):
                pass


@contextmanager
def ensure_edit_mode(obj):
    """
    Context manager to ensure Edit mode for operations.

    Args:
        obj: Object to edit

    Yields:
        bool: True if successfully in edit mode
    """
    with safe_mode_switch(obj, 'EDIT') as success:
        yield success


@contextmanager
def ensure_pose_mode(armature):
    """
    Context manager to ensure Pose mode for armature operations.

    Args:
        armature: Armature object to pose

    Yields:
        bool: True if successfully in pose mode
    """
    if not armature or armature.type != 'ARMATURE':
        yield False
        return

    with safe_mode_switch(armature, 'POSE') as success:
        yield success


def switch_to_mode(mode: str, obj: Optional[object] = None) -> bool:
    """
    Switch to specified mode (non-context manager version).

    Args:
        mode: Target mode ('OBJECT', 'EDIT', 'POSE', etc.)
        obj: Optional object to make active before switching

    Returns:
        True if successful, False otherwise
    """
    try:
        if obj:
            bpy.context.view_layer.objects.active = obj

        if bpy.context.object and bpy.context.object.mode != mode:
            bpy.ops.object.mode_set(mode=mode)

        return True

    except (RuntimeError, TypeError, AttributeError) as e:
        print(f"Failed to switch to mode {mode}: {e}")
        return False


def get_current_mode() -> str:
    """
    Get current Blender mode.

    Returns:
        Current mode string ('OBJECT', 'EDIT', 'POSE', etc.)
    """
    if bpy.context.object:
        return bpy.context.object.mode
    return 'OBJECT'


def is_valid_mode_for_object(obj, mode: str) -> bool:
    """
    Check if a mode is valid for a given object type.

    Args:
        obj: Object to check
        mode: Mode to validate

    Returns:
        True if mode is valid for object type, False otherwise
    """
    if not obj:
        return False

    valid_modes = {
        'MESH': ['OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'],
        'ARMATURE': ['OBJECT', 'EDIT', 'POSE'],
        'CURVE': ['OBJECT', 'EDIT'],
        'SURFACE': ['OBJECT', 'EDIT'],
        'META': ['OBJECT', 'EDIT'],
        'FONT': ['OBJECT', 'EDIT'],
        'LATTICE': ['OBJECT', 'EDIT'],
    }

    allowed_modes = valid_modes.get(obj.type, ['OBJECT'])
    return mode in allowed_modes


@contextmanager
def temporary_active_object(obj):
    """
    Temporarily set active object, then restore original.

    Args:
        obj: Object to make temporarily active

    Yields:
        The temporarily active object
    """
    original_active = bpy.context.view_layer.objects.active

    try:
        bpy.context.view_layer.objects.active = obj
        yield obj

    finally:
        try:
            if original_active and original_active.name in bpy.data.objects:
                bpy.context.view_layer.objects.active = original_active
        except (RuntimeError, TypeError, AttributeError):
            pass


@contextmanager
def selection_guard():
    """
    Save and restore object selection state.

    Yields:
        List of originally selected objects

    Example:
        >>> with selection_guard():
        ...     bpy.ops.object.select_all(action='DESELECT')
        ...     obj.select_set(True)
        ...     # Do operation
        ... # Selection automatically restored
    """
    original_selection = [obj for obj in bpy.context.selected_objects]
    original_active = bpy.context.view_layer.objects.active

    try:
        yield original_selection

    finally:
        try:
            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selection:
                if obj.name in bpy.data.objects:
                    obj.select_set(True)

            # Restore active
            if original_active and original_active.name in bpy.data.objects:
                bpy.context.view_layer.objects.active = original_active

        except (RuntimeError, TypeError, AttributeError) as e:
            print(f"Failed to restore selection: {e}")
