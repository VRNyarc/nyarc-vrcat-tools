# Validation Utilities
# Input validation and safety checks for mirror flip operations

import bpy
import bmesh
from mathutils import Vector

def validate_selected_objects():
    """Validate that appropriate objects are selected for mirroring"""
    errors = []
    warnings = []
    
    selected_objects = bpy.context.selected_objects
    active_object = bpy.context.active_object
    
    if not selected_objects:
        errors.append("No objects selected")
        return errors, warnings
    
    # Check for mesh objects
    mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
    armature_objects = [obj for obj in selected_objects if obj.type == 'ARMATURE']
    
    if not mesh_objects and not armature_objects:
        errors.append("No mesh or armature objects selected")
    
    # Validate mesh objects
    for mesh_obj in mesh_objects:
        # Check if transforms are applied
        loc, rot, scale = mesh_obj.matrix_world.decompose()
        if (loc.length > 0.001 or 
            abs(rot.to_euler().x) > 0.001 or abs(rot.to_euler().y) > 0.001 or abs(rot.to_euler().z) > 0.001 or
            abs(scale.x - 1.0) > 0.001 or abs(scale.y - 1.0) > 0.001 or abs(scale.z - 1.0) > 0.001):
            warnings.append(f"Object '{mesh_obj.name}' has unapplied transforms")
    
    # Validate armature objects
    for armature_obj in armature_objects:
        # Check if transforms are applied
        loc, rot, scale = armature_obj.matrix_world.decompose()
        if (loc.length > 0.001 or 
            abs(rot.to_euler().x) > 0.001 or abs(rot.to_euler().y) > 0.001 or abs(rot.to_euler().z) > 0.001 or
            abs(scale.x - 1.0) > 0.001 or abs(scale.y - 1.0) > 0.001 or abs(scale.z - 1.0) > 0.001):
            warnings.append(f"Armature '{armature_obj.name}' has unapplied transforms")
    
    return errors, warnings

def validate_bone_selection(armature_obj):
    """Validate bone selection for mirroring operations"""
    errors = []
    warnings = []
    
    if not armature_obj or armature_obj.type != 'ARMATURE':
        errors.append("No armature object provided")
        return errors, warnings
    
    # Check if in edit mode and bones are selected
    if bpy.context.mode == 'EDIT_ARMATURE':
        selected_bones = [bone for bone in armature_obj.data.edit_bones if bone.select]
        if not selected_bones:
            warnings.append("No bones selected in edit mode")
    elif bpy.context.mode == 'POSE':
        selected_bones = [bone for bone in armature_obj.pose.bones if bone.bone.select]
        if not selected_bones:
            warnings.append("No bones selected in pose mode")
    
    return errors, warnings

def check_mesh_bone_relationships(mesh_objects, armature_objects):
    """Check relationships between meshes and armatures"""
    relationships = {}
    warnings = []
    
    for mesh_obj in mesh_objects:
        # Find armature modifiers
        armature_mods = [mod for mod in mesh_obj.modifiers if mod.type == 'ARMATURE']
        
        if not armature_mods:
            warnings.append(f"Mesh '{mesh_obj.name}' has no armature modifier")
            continue
        
        for mod in armature_mods:
            if mod.object and mod.object in armature_objects:
                if mesh_obj.name not in relationships:
                    relationships[mesh_obj.name] = []
                relationships[mesh_obj.name].append(mod.object.name)
            elif mod.object:
                warnings.append(f"Mesh '{mesh_obj.name}' references unselected armature '{mod.object.name}'")
    
    return relationships, warnings

def validate_naming_conventions(objects):
    """Check if objects follow proper naming conventions"""
    warnings = []
    suggestions = []
    
    from .naming import detect_naming_pattern, suggest_naming_fix
    
    for obj in objects:
        current_suffix, opposite_suffix, _ = detect_naming_pattern(obj.name)
        if not current_suffix:
            suggestion = suggest_naming_fix(obj.name)
            suggestions.append(f"Consider renaming '{obj.name}' to '{suggestion}' for better symmetry support")
    
    return warnings, suggestions

def check_context_mode():
    """Check if we're in appropriate mode for operations"""
    mode = bpy.context.mode
    valid_modes = ['OBJECT', 'EDIT_ARMATURE', 'POSE']
    
    if mode not in valid_modes:
        return f"Invalid mode '{mode}'. Switch to Object, Edit, or Pose mode"
    
    return None

def safe_mode_switch(target_mode):
    """Safely switch between modes with error handling"""
    current_mode = bpy.context.mode
    
    try:
        if target_mode == 'OBJECT' and current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        elif target_mode == 'EDIT' and current_mode != 'EDIT_ARMATURE':
            if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':
                bpy.ops.object.mode_set(mode='EDIT')
            else:
                return "No armature selected for edit mode"
        elif target_mode == 'POSE' and current_mode != 'POSE':
            if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':
                bpy.ops.object.mode_set(mode='POSE')
            else:
                return "No armature selected for pose mode"
        
        return None  # Success
        
    except Exception as e:
        return f"Failed to switch to {target_mode} mode: {str(e)}"