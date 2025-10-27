# Mesh Utilities for Shape Key Transfer
# Handles mesh validation, compatibility, and preparation

import bpy
import bmesh
import re


def sanitize_display_name(name):
    """Sanitize object/shape key names for safe UI display"""
    if not name:
        return "Unnamed"
    
    # Remove potential UI-breaking characters
    safe_name = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str(name))
    
    # Limit length to prevent UI overflow
    if len(safe_name) > 64:
        safe_name = safe_name[:61] + "..."
    
    # Ensure not empty after sanitization
    if not safe_name.strip():
        safe_name = "InvalidName"
    
    return safe_name


def ensure_surface_deform_compatibility(obj):
    """
    Prepare mesh for surface deform compatibility by adding temporary modifiers.

    This function addresses common mesh topology issues that can cause
    Surface Deform modifier binding failures, particularly with meshes that have:
    - N-gons (faces with more than 4 vertices)
    - Non-manifold edges
    - Disconnected geometry

    IMPORTANT: This function adds TEMPORARY MODIFIERS that must be removed later.
    Use remove_surface_deform_compatibility_modifiers() to clean up.

    Args:
        obj: Blender mesh object to prepare

    Returns:
        dict: {'modified': bool, 'modifiers_added': [str]} - modifier names to remove later
    """

    if not obj or obj.type != 'MESH':
        return {'modified': False, 'modifiers_added': []}

    modifiers_added = []

    # Store original mode
    original_mode = bpy.context.mode

    try:
        # Store current context
        original_active = bpy.context.active_object
        original_selected = bpy.context.selected_objects.copy()

        # Check if we can safely change modes
        if bpy.context.mode not in {'OBJECT', 'EDIT_MESH'}:
            print(f"Warning: ensure_surface_deform_compatibility called in unsupported mode: {bpy.context.mode}")
            return {'modified': False, 'modifiers_added': []}

        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as mode_error:
                print(f"Could not switch to object mode: {mode_error}")
                return {'modified': False, 'modifiers_added': []}

        # Setup context for this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Check if mesh needs processing
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Check if we need triangulation (any face that's not a triangle)
        needs_triangulation = any(len(face.verts) > 3 for face in bm.faces)

        # Check for non-manifold edges (we still need to fix these destructively)
        non_manifold_edges = [edge for edge in bm.edges if not edge.is_manifold]
        needs_cleanup = len(non_manifold_edges) > 0

        bm.free()

        # If non-manifold edges exist, fix them destructively (no good modifier alternative)
        if needs_cleanup:
            try:
                bm_edit = bmesh.new()
                bm_edit.from_mesh(obj.data)
                bm_edit.edges.ensure_lookup_table()
                bm_edit.verts.ensure_lookup_table()

                # Split non-manifold edges
                non_manifold_verts = [v for v in bm_edit.verts if not v.is_manifold]
                if non_manifold_verts:
                    bmesh.ops.split_edges(bm_edit, edges=[e for e in bm_edit.edges if not e.is_manifold])
                    bm_edit.to_mesh(obj.data)
                    obj.data.update()
                    print(f"Fixed non-manifold edges on '{obj.name}'")

                bm_edit.free()
            except Exception as cleanup_error:
                print(f"Error during non-manifold cleanup: {cleanup_error}")

        # Add Triangulate modifier NON-DESTRUCTIVELY (can be removed later)
        if needs_triangulation:
            try:
                # Check if a temp triangulate modifier already exists
                modifier_name = f"TEMP_Triangulate_{obj.name}"
                existing_mod = obj.modifiers.get(modifier_name)

                if not existing_mod:
                    tri_mod = obj.modifiers.new(name=modifier_name, type='TRIANGULATE')
                    tri_mod.quad_method = 'BEAUTY'
                    tri_mod.ngon_method = 'BEAUTY'
                    tri_mod.keep_custom_normals = True
                    modifiers_added.append(modifier_name)
                    print(f"Added temporary Triangulate modifier to '{obj.name}'")
                else:
                    # Already exists, just track it
                    modifiers_added.append(modifier_name)
                    print(f"Temporary Triangulate modifier already exists on '{obj.name}'")

            except Exception as tri_error:
                print(f"Error adding Triangulate modifier: {tri_error}")

        modified = needs_cleanup or needs_triangulation

        return {'modified': modified, 'modifiers_added': modifiers_added}

    except Exception as e:
        print(f"Error in ensure_surface_deform_compatibility: {e}")
        return {'modified': False, 'modifiers_added': modifiers_added}
    finally:
        # Restore original context and mode
        try:
            # Return to object mode first
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for selected_obj in original_selected:
                if selected_obj:
                    selected_obj.select_set(True)

            # Restore active object
            if original_active:
                bpy.context.view_layer.objects.active = original_active

            # Restore original mode if it wasn't object mode
            if original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=original_mode)
        except Exception as restore_error:
            print(f"Error restoring context: {restore_error}")
            pass


def remove_surface_deform_compatibility_modifiers(obj, modifier_names):
    """
    Remove temporary modifiers that were added for Surface Deform compatibility.

    Args:
        obj: Blender mesh object to clean up
        modifier_names: List of modifier names to remove

    Returns:
        bool: True if any modifiers were removed, False otherwise
    """

    # Check if object is valid and hasn't been deleted
    if not obj or not modifier_names:
        return False

    try:
        # Try to access obj.type to check if object still exists in Blender
        if obj.type != 'MESH':
            return False
    except ReferenceError:
        # Object has been deleted (e.g., temp preprocessing object)
        return False

    removed_count = 0

    try:
        # Ensure we're in object mode
        original_mode = bpy.context.mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Remove each modifier by name
        for mod_name in modifier_names:
            modifier = obj.modifiers.get(mod_name)
            if modifier:
                try:
                    obj.modifiers.remove(modifier)
                    removed_count += 1
                    print(f"Removed temporary modifier '{mod_name}' from '{obj.name}'")
                except Exception as remove_error:
                    print(f"Failed to remove modifier '{mod_name}': {remove_error}")

        # Restore original mode
        # Note: bpy.context.mode returns different strings than mode_set() accepts
        # PAINT_WEIGHT -> WEIGHT_PAINT, PAINT_TEXTURE -> TEXTURE_PAINT, etc.
        if original_mode != 'OBJECT':
            # Map internal mode names to mode_set() arguments
            mode_map = {
                'PAINT_WEIGHT': 'WEIGHT_PAINT',
                'PAINT_TEXTURE': 'TEXTURE_PAINT',
                'PAINT_VERTEX': 'VERTEX_PAINT',
            }
            mode_to_set = mode_map.get(original_mode, original_mode)
            bpy.ops.object.mode_set(mode=mode_to_set)

        return removed_count > 0

    except Exception as e:
        print(f"Error removing compatibility modifiers: {e}")
        return False


def get_unique_shape_key_name(target_obj, desired_name):
    """Generate a unique shape key name if one already exists"""
    if not target_obj.data.shape_keys:
        return desired_name

    existing_names = set(key.name for key in target_obj.data.shape_keys.key_blocks)

    if desired_name not in existing_names:
        return desired_name

    # Generate unique name with incremental suffix
    counter = 1
    while f"{desired_name}.{counter:03d}" in existing_names:
        counter += 1

    return f"{desired_name}.{counter:03d}"


def get_classes():
    """Get all utility classes for registration (none for mesh_utils)"""
    return []