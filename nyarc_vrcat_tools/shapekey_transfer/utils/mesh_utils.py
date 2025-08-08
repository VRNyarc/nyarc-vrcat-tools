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
    Prepare mesh for surface deform compatibility by cleaning problematic geometry.
    
    This function addresses common mesh topology issues that can cause 
    Surface Deform modifier binding failures, particularly with meshes that have:
    - N-gons (faces with more than 4 vertices)
    - Non-manifold edges
    - Disconnected geometry
    
    Args:
        obj: Blender mesh object to prepare
        
    Returns:
        bool: True if mesh was modified, False if no changes needed
    """
    
    if not obj or obj.type != 'MESH':
        return False
    
    # Store original mode
    original_mode = bpy.context.mode
    
    try:
        # Store current context
        original_active = bpy.context.active_object
        original_selected = bpy.context.selected_objects.copy()
        
        # Check if we can safely change modes
        if bpy.context.mode not in {'OBJECT', 'EDIT_MESH'}:
            print(f"Warning: ensure_surface_deform_compatibility called in unsupported mode: {bpy.context.mode}")
            return False
        
        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as mode_error:
                print(f"Could not switch to object mode: {mode_error}")
                return False
        
        # Setup context for this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Check if mesh needs processing
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        
        # Check if we need triangulation (any face that's not a triangle)
        needs_triangulation = any(len(face.verts) > 3 for face in bm.faces)
        
        # Check for non-manifold edges
        non_manifold_edges = [edge for edge in bm.edges if not edge.is_manifold]
        needs_cleanup = len(non_manifold_edges) > 0
        
        bm.free()
        
        if not (needs_triangulation or needs_cleanup):
            return False  # No changes needed
        
        # Use bmesh operations directly (more reliable than mesh operators)
        bm_edit = bmesh.new()
        bm_edit.from_mesh(obj.data)
        
        # Ensure face indices are valid
        bm_edit.faces.ensure_lookup_table()
        bm_edit.edges.ensure_lookup_table()
        bm_edit.verts.ensure_lookup_table()
        
        modified = False
        
        # Fix non-manifold edges by splitting them
        if needs_cleanup:
            try:
                # Split non-manifold edges
                non_manifold_verts = [v for v in bm_edit.verts if not v.is_manifold]
                if non_manifold_verts:
                    bmesh.ops.split_edges(bm_edit, edges=[e for e in bm_edit.edges if not e.is_manifold])
                    modified = True
            except Exception as cleanup_error:
                print(f"Error during bmesh non-manifold cleanup: {cleanup_error}")
        
        # Triangulate ALL non-triangle faces using bmesh
        if needs_triangulation:
            try:
                # Get all faces that aren't triangles
                faces_to_triangulate = [f for f in bm_edit.faces if len(f.verts) > 3]
                if faces_to_triangulate:
                    bmesh.ops.triangulate(bm_edit, faces=faces_to_triangulate, quad_method='BEAUTY', ngon_method='BEAUTY')
                    modified = True
            except Exception as tri_error:
                print(f"Error during bmesh triangulation: {tri_error}")
        
        # Apply changes back to mesh
        if modified:
            try:
                bm_edit.to_mesh(obj.data)
                obj.data.update()
            except Exception as update_error:
                print(f"Error updating mesh: {update_error}")
                bm_edit.free()
                return False
        
        bm_edit.free()
        
        return modified  # Return whether mesh was actually modified
        
    except Exception as e:
        print(f"Error in ensure_surface_deform_compatibility: {e}")
        return False
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