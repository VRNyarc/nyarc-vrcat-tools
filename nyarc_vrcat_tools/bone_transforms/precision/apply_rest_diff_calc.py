"""
Apply Rest Pose for Diff Calculation - Precision Correction Only
Lightweight apply rest pose functions specifically for amateur diff export precision correction
Does NOT affect the normal apply_as_rest_pose operator used by regular workflows
"""

import bpy
from mathutils import Vector

def save_shape_keys_for_diff_calc(armature):
    """
    Save shape key data once at beginning of diff calculation precision correction
    Returns backup data for restoration at the end
    
    Args:
        armature: Target armature object
        
    Returns:
        dict: Shape key backup data for restoration
    """
    shape_key_backup = {}
    
    try:
        # Get all meshes with armature modifiers pointing to this armature
        mesh_objects = []
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                any(mod.type == 'ARMATURE' and mod.object == armature for mod in obj.modifiers)):
                mesh_objects.append(obj)
        
        # Count shape keys for summary
        total_shape_keys = 0
        meshes_with_shape_keys = 0
        
        for mesh_obj in mesh_objects:
            has_shape_keys = bool(mesh_obj.data.shape_keys and mesh_obj.data.shape_keys.key_blocks)
            
            # Store mesh info regardless of shape keys
            shape_key_backup[mesh_obj.name] = {
                'mesh_obj': mesh_obj,
                'has_shape_keys': has_shape_keys
            }
            
            if has_shape_keys:
                meshes_with_shape_keys += 1
                shape_key_count = len(mesh_obj.data.shape_keys.key_blocks)
                total_shape_keys += shape_key_count
                
                # Add shape key specific data
                shape_key_backup[mesh_obj.name].update({
                    'shape_key_data': {},
                    'active_index': mesh_obj.active_shape_key_index,
                    'show_only': mesh_obj.show_only_shape_key
                })
                
                # Save each shape key's vertex positions
                for i, shape_key in enumerate(mesh_obj.data.shape_keys.key_blocks):
                    positions = []
                    for vertex in shape_key.data:
                        positions.append(vertex.co.copy())
                    
                    shape_key_backup[mesh_obj.name]['shape_key_data'][i] = {
                        'name': shape_key.name,
                        'positions': positions
                    }
        
        print(f"[DIFF CALC] Saved {total_shape_keys} shape keys from {meshes_with_shape_keys}/{len(mesh_objects)} meshes")
        
        return shape_key_backup
        
    except Exception as e:
        print(f"[ERROR] Failed to save shape keys for diff calc: {e}")
        return {}

def restore_shape_keys_after_diff_calc(armature, shape_key_backup):
    """
    Restore shape key data once at end of diff calculation precision correction
    Applies final armature deformation to all shape keys
    
    Args:
        armature: Target armature object
        shape_key_backup: Shape key backup data from save function
    """
    try:
        if not shape_key_backup:
            print("[DIFF CALC] No shape key backup data to restore")
            return
        
        mesh_count = 0
        updated_count = 0
        error_count = 0
        total_vertex_movement = 0.0
        
        for mesh_name, backup_data in shape_key_backup.items():
            mesh_obj = backup_data['mesh_obj']
            has_shape_keys = backup_data.get('has_shape_keys', False)
            mesh_count += 1
            
            if mesh_obj:
                # Store original first vertex position for comparison
                original_pos = mesh_obj.data.vertices[0].co.copy() if len(mesh_obj.data.vertices) > 0 else None
                
                try:
                    if has_shape_keys:
                        apply_armature_to_mesh_diff_calc_with_shape_keys(armature, mesh_obj)
                    else:
                        apply_armature_to_mesh_diff_calc_no_shape_keys(armature, mesh_obj)
                    
                    # Check if vertices actually changed
                    if original_pos and len(mesh_obj.data.vertices) > 0:
                        new_pos = mesh_obj.data.vertices[0].co.copy()
                        diff = (new_pos - original_pos).length
                        total_vertex_movement += diff
                        
                        if diff > 0.0001:
                            updated_count += 1
                
                except Exception as e:
                    error_count += 1
                    print(f"[DIFF CALC] ERROR on {mesh_obj.name}: {e}")
            else:
                error_count += 1
        
        print(f"[DIFF CALC] Restored {mesh_count} meshes: {updated_count} updated, {error_count} errors, avg movement: {total_vertex_movement/max(mesh_count,1):.6f}")
        
        print("[DIFF CALC] Shape key restoration complete")
        
    except Exception as e:
        print(f"[ERROR] Failed to restore shape keys after diff calc: {e}")

def apply_rest_pose_diff_calc_only(context, armature):
    """
    Lightweight apply rest pose EXCLUSIVELY for diff calculation precision correction
    Does NOT process shape keys - just applies pose to armature rest pose
    
    IMPORTANT: This function is ONLY for amateur diff export precision correction.
    Regular users should use the normal apply_as_rest_pose operator.
    
    Args:
        context: Blender context
        armature: Target armature object
        
    Returns:
        bool: True if successful
    """
    try:
        print("[DIFF CALC] Applying lightweight rest pose (diff calculation only - no shape key processing)")
        
        # CONTEXT FIX: Ensure we're in Object mode first before selection operations
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Ensure armature is selected and active
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        context.view_layer.objects.active = armature
        
        # Now switch to pose mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # Apply pose to rest pose using core Blender operation
        bpy.ops.pose.select_all(action='SELECT')
        result = bpy.ops.pose.armature_apply(selected=False)
        
        if result != {'FINISHED'}:
            print("[ERROR] pose.armature_apply failed in diff calc")
            return False
        
        # DON'T clear transforms during iterative precision correction
        # The caller will clear transforms when fully done
        print("[DIFF CALC] Pose applied to rest pose (transforms preserved for next iteration)")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Lightweight apply rest pose failed in diff calc: {e}")
        return False

def apply_armature_to_mesh_diff_calc_with_shape_keys(armature, mesh_obj):
    """
    Apply armature deformation to mesh with shape keys - diff calculation version
    This is called only at the END of precision correction to finalize shape keys
    
    Args:
        armature: Target armature object
        mesh_obj: Mesh object with shape keys
    """
    try:
        print(f"[DIFF CALC] Applying final armature deformation to {mesh_obj.name} with shape keys")
        
        # SHAPE KEY FIX: Import and call the method properly without operator instantiation
        import numpy as np
        
        # Store current active object and selection
        original_active = bpy.context.view_layer.objects.active
        original_selected = bpy.context.selected_objects[:]
        
        try:
            # CONTEXT FIX: Ensure we're in Object mode first
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Make mesh active (using direct selection instead of ops)
            for obj in bpy.context.selected_objects:
                obj.select_set(False) 
            mesh_obj.select_set(True)
            bpy.context.view_layer.objects.active = mesh_obj
            # Save current state
            old_active_shape_key_index = mesh_obj.active_shape_key_index
            old_show_only_shape_key = mesh_obj.show_only_shape_key
            
            # Enable shape key pinning
            mesh_obj.show_only_shape_key = True
            
            # Store and temporarily disable shape key properties
            me = mesh_obj.data
            shape_key_vertex_groups = []
            shape_key_mutes = []
            key_blocks = me.shape_keys.key_blocks
            
            for shape_key in key_blocks:
                shape_key_vertex_groups.append(shape_key.vertex_group)
                shape_key.vertex_group = ''
                shape_key_mutes.append(shape_key.mute)
                shape_key.mute = False
            
            # Disable all existing modifiers temporarily
            mods_to_reenable_viewport = []
            for mod in mesh_obj.modifiers:
                if mod.show_viewport:
                    mod.show_viewport = False
                    mods_to_reenable_viewport.append(mod)
            
            # Add temporary armature modifier
            armature_mod = mesh_obj.modifiers.new('TempPoseToRest', 'ARMATURE')
            armature_mod.object = armature
            
            # Prepare for evaluation
            co_length = len(me.vertices) * 3
            eval_verts_cos_array = np.empty(co_length, dtype=np.single)
            depsgraph = None
            evaluated_mesh_obj = None
            
            def get_eval_cos_array():
                nonlocal depsgraph, evaluated_mesh_obj
                if depsgraph is None or evaluated_mesh_obj is None:
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    evaluated_mesh_obj = mesh_obj.evaluated_get(depsgraph)
                else:
                    depsgraph.update()
                evaluated_mesh_obj.data.vertices.foreach_get('co', eval_verts_cos_array)
                return eval_verts_cos_array
            
            # Apply armature deformation to each shape key
            processed_shape_keys = 0
            for i, shape_key in enumerate(key_blocks):
                # Set active shape key (with pinning, this shows only this shape key)
                mesh_obj.active_shape_key_index = i
                
                # Get evaluated vertex positions (shape key + armature deformation)
                evaluated_cos = get_eval_cos_array()
                
                # Update shape key with evaluated positions
                shape_key.data.foreach_set('co', evaluated_cos)
                
                # For basis shape key, also update mesh vertices
                if i == 0:
                    mesh_obj.data.vertices.foreach_set('co', evaluated_cos)
                
                processed_shape_keys += 1
            
            # Restore original state
            for mod in mods_to_reenable_viewport:
                mod.show_viewport = True
            mesh_obj.modifiers.remove(armature_mod)
            
            for shape_key, vertex_group, mute in zip(key_blocks, shape_key_vertex_groups, shape_key_mutes):
                shape_key.vertex_group = vertex_group
                shape_key.mute = mute
                
            mesh_obj.active_shape_key_index = old_active_shape_key_index
            mesh_obj.show_only_shape_key = old_show_only_shape_key
            
        finally:
            # Restore original selection (using direct selection)
            for obj in bpy.context.selected_objects:
                obj.select_set(False)
            for obj in original_selected:
                if obj:  # Check if object still exists
                    obj.select_set(True)
            if original_active:
                bpy.context.view_layer.objects.active = original_active
        
        # Summary logged in caller
        
    except Exception as e:
        print(f"[ERROR] Failed to apply armature to mesh in diff calc: {e}")

def apply_armature_to_mesh_diff_calc_no_shape_keys(armature, mesh_obj):
    """
    Apply armature deformation to mesh without shape keys - diff calculation version
    This is called only at the END of precision correction to finalize mesh
    
    Updates mesh vertices to match the new bone rest positions after precision correction.
    
    Args:
        armature: Target armature object
        mesh_obj: Mesh object without shape keys
    """
    try:
        import numpy as np
        
        # Store current active object and selection
        original_active = bpy.context.view_layer.objects.active
        original_selected = bpy.context.selected_objects[:]
        
        try:
            # CONTEXT FIX: Ensure we're in Object mode first
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Make mesh active (using direct selection instead of ops)
            for obj in bpy.context.selected_objects:
                obj.select_set(False) 
            mesh_obj.select_set(True)
            bpy.context.view_layer.objects.active = mesh_obj
            print(f"[DIFF CALC] DEBUG: Set active object to {mesh_obj.name}, mode: {bpy.context.mode}")
            
            # Disable all existing modifiers temporarily
            mods_to_reenable_viewport = []
            for mod in mesh_obj.modifiers:
                if mod.show_viewport:
                    mod.show_viewport = False
                    mods_to_reenable_viewport.append(mod)
            
            # Add temporary armature modifier
            armature_mod = mesh_obj.modifiers.new('TempPoseToRest', 'ARMATURE')
            armature_mod.object = armature
            
            # Get evaluated vertex positions (with armature deformation)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated_mesh_obj = mesh_obj.evaluated_get(depsgraph)
            
            co_length = len(mesh_obj.data.vertices) * 3
            eval_verts_cos_array = np.empty(co_length, dtype=np.single)
            evaluated_mesh_obj.data.vertices.foreach_get('co', eval_verts_cos_array)
            
            # Update original mesh vertices with evaluated positions
            mesh_obj.data.vertices.foreach_set('co', eval_verts_cos_array)
            mesh_obj.data.update()
            
            # Remove temporary modifier
            mesh_obj.modifiers.remove(armature_mod)
            
            # Restore original modifiers
            for mod in mods_to_reenable_viewport:
                mod.show_viewport = True
            
        finally:
            # Restore original selection (using direct selection)
            for obj in bpy.context.selected_objects:
                obj.select_set(False)
            for obj in original_selected:
                if obj:  # Check if object still exists
                    obj.select_set(True)
            if original_active:
                bpy.context.view_layer.objects.active = original_active
        
        # Summary logged in caller
        
    except Exception as e:
        print(f"[ERROR] Failed to apply armature to mesh in diff calc: {e}")