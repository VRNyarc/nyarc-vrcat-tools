"""
Bone iteration and common bone operations.

Provides utilities for working with bones in different modes (Edit, Pose, Data)
and common bone manipulation operations.
"""

import bpy
from typing import Optional, List, Iterator


def iter_bones(armature, mode='EDIT'):
    """
    Iterate over bones in armature (mode-aware).

    Args:
        armature: Armature object
        mode: Mode to get bones from ('EDIT', 'POSE', 'DATA')

    Returns:
        Bone collection for the specified mode, or empty list if invalid

    Example:
        >>> for bone in iter_bones(armature, 'POSE'):
        ...     print(bone.name)
    """
    if not armature or armature.type != 'ARMATURE':
        return []

    try:
        if mode == 'EDIT':
            # Edit bones - only available in edit mode
            if hasattr(armature.data, 'edit_bones'):
                return armature.data.edit_bones
            return []
        elif mode == 'POSE':
            # Pose bones
            if hasattr(armature, 'pose') and hasattr(armature.pose, 'bones'):
                return armature.pose.bones
            return []
        elif mode == 'DATA':
            # Data bones (always available)
            return armature.data.bones
        else:
            print(f"Unknown bone mode: {mode}")
            return []

    except (AttributeError, TypeError) as e:
        print(f"Error accessing bones in mode {mode}: {e}")
        return []


def get_bone(armature, bone_name: str, mode='EDIT'):
    """
    Get bone by name (mode-aware).

    Args:
        armature: Armature object
        bone_name: Name of bone to get
        mode: Mode to get bone from ('EDIT', 'POSE', 'DATA')

    Returns:
        Bone object if found, None otherwise

    Example:
        >>> bone = get_bone(armature, "Hips", mode='POSE')
        >>> if bone:
        ...     bone.location = (0, 0, 0)
    """
    bones = iter_bones(armature, mode)

    if not bones:
        return None

    try:
        return bones.get(bone_name)
    except (AttributeError, KeyError, TypeError):
        return None


def get_all_bone_names(armature, mode='DATA') -> List[str]:
    """
    Get list of all bone names in armature.

    Args:
        armature: Armature object
        mode: Mode to get bones from ('EDIT', 'POSE', 'DATA')

    Returns:
        List of bone names

    Example:
        >>> names = get_all_bone_names(armature)
        >>> if "Hips" in names:
        ...     print("Has hips bone")
    """
    bones = iter_bones(armature, mode)
    if not bones:
        return []

    try:
        return [bone.name for bone in bones]
    except (AttributeError, TypeError):
        return []


def bone_exists(armature, bone_name: str, mode='DATA') -> bool:
    """
    Check if bone exists in armature.

    Args:
        armature: Armature object
        bone_name: Name of bone to check
        mode: Mode to check in ('EDIT', 'POSE', 'DATA')

    Returns:
        True if bone exists, False otherwise
    """
    return get_bone(armature, bone_name, mode) is not None


def get_selected_bones(armature, mode='EDIT') -> List:
    """
    Get list of selected bones in armature.

    Args:
        armature: Armature object
        mode: Mode to get bones from ('EDIT', 'POSE')

    Returns:
        List of selected bone objects
    """
    bones = iter_bones(armature, mode)
    if not bones:
        return []

    try:
        return [bone for bone in bones if bone.select]
    except (AttributeError, TypeError):
        return []


def get_bone_count(armature) -> int:
    """
    Get number of bones in armature.

    Args:
        armature: Armature object

    Returns:
        Number of bones, or 0 if invalid
    """
    if not armature or armature.type != 'ARMATURE':
        return 0

    try:
        return len(armature.data.bones)
    except (AttributeError, TypeError):
        return 0


def select_bone(armature, bone_name: str, mode='EDIT', deselect_others=False) -> bool:
    """
    Select a bone by name.

    Args:
        armature: Armature object
        bone_name: Name of bone to select
        mode: Mode bones are in ('EDIT', 'POSE')
        deselect_others: Whether to deselect other bones first

    Returns:
        True if bone was selected, False otherwise
    """
    bones = iter_bones(armature, mode)
    if not bones:
        return False

    try:
        if deselect_others:
            for bone in bones:
                bone.select = False

        bone = bones.get(bone_name)
        if bone:
            bone.select = True
            return True

        return False

    except (AttributeError, KeyError, TypeError) as e:
        print(f"Failed to select bone {bone_name}: {e}")
        return False


def deselect_all_bones(armature, mode='EDIT') -> bool:
    """
    Deselect all bones in armature.

    Args:
        armature: Armature object
        mode: Mode bones are in ('EDIT', 'POSE')

    Returns:
        True if successful, False otherwise
    """
    bones = iter_bones(armature, mode)
    if not bones:
        return False

    try:
        for bone in bones:
            bone.select = False
        return True

    except (AttributeError, TypeError) as e:
        print(f"Failed to deselect bones: {e}")
        return False


def get_parent_bone(armature, bone_name: str, mode='DATA'):
    """
    Get parent bone of specified bone.

    Args:
        armature: Armature object
        bone_name: Name of bone to get parent for
        mode: Mode to get bones from ('EDIT', 'POSE', 'DATA')

    Returns:
        Parent bone object if exists, None otherwise
    """
    bone = get_bone(armature, bone_name, mode)
    if not bone:
        return None

    try:
        return bone.parent
    except (AttributeError, TypeError):
        return None


def get_child_bones(armature, bone_name: str, mode='DATA', recursive=False) -> List:
    """
    Get child bones of specified bone.

    Args:
        armature: Armature object
        bone_name: Name of bone to get children for
        mode: Mode to get bones from ('EDIT', 'POSE', 'DATA')
        recursive: Whether to get all descendants (recursive) or just direct children

    Returns:
        List of child bone objects
    """
    bone = get_bone(armature, bone_name, mode)
    if not bone:
        return []

    try:
        if not recursive:
            return list(bone.children)

        # Recursive: get all descendants
        children = []
        def add_descendants(bone):
            for child in bone.children:
                children.append(child)
                add_descendants(child)

        add_descendants(bone)
        return children

    except (AttributeError, TypeError):
        return []


def get_bone_chain(armature, bone_name: str, mode='DATA') -> List:
    """
    Get bone chain from root to specified bone.

    Args:
        armature: Armature object
        bone_name: Name of bone to get chain for
        mode: Mode to get bones from ('EDIT', 'POSE', 'DATA')

    Returns:
        List of bones from root to target bone (inclusive)
    """
    bone = get_bone(armature, bone_name, mode)
    if not bone:
        return []

    chain = []
    try:
        current = bone
        while current:
            chain.insert(0, current)  # Insert at beginning to get root-to-tip order
            current = current.parent
        return chain

    except (AttributeError, TypeError):
        return []


def bones_are_connected(armature, bone1_name: str, bone2_name: str, mode='DATA') -> bool:
    """
    Check if two bones are connected (child's head at parent's tail).

    Args:
        armature: Armature object
        bone1_name: First bone name
        bone2_name: Second bone name
        mode: Mode to get bones from

    Returns:
        True if bones are connected, False otherwise
    """
    bone1 = get_bone(armature, bone1_name, mode)
    bone2 = get_bone(armature, bone2_name, mode)

    if not bone1 or not bone2:
        return False

    try:
        # Check if bone2 is child of bone1 and connected
        if bone2.parent == bone1:
            return bone2.use_connect if hasattr(bone2, 'use_connect') else False

        # Check if bone1 is child of bone2 and connected
        if bone1.parent == bone2:
            return bone1.use_connect if hasattr(bone1, 'use_connect') else False

        return False

    except (AttributeError, TypeError):
        return False
