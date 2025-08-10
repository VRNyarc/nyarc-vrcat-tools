# Inheritance Flattening Module
# Solves inheritance context inconsistencies by flattening transforms during save/load
#
# PROBLEM SOLVED: When bones have different inherit_scale settings across history entries,
# the same pose transform values produce different visual results. This module ensures
# visual consistency by flattening inheritance during save and enforcing NONE during load.

import bpy
from mathutils import Vector, Quaternion


def get_bones_requiring_flatten_context(armature, target_bone_names):
    """
    Get all bones that need flatten context based on inheritance chain analysis.
    Only bones in uninterrupted 'FULL' inheritance chains from scaled bones are included.
    
    Example inheritance chains:
    - Hip(scaled) → Leg(FULL) → Foot(FULL) = ALL inherit Hip scaling
    - Hip(scaled) → Leg(NONE) → Foot(FULL) = Foot does NOT inherit (chain broken)
    - Hip(scaled) → Leg(FULL) → Knee(NONE) → Foot(FULL) = Foot does NOT inherit (chain broken)
    
    Args:
        armature: Blender armature object
        target_bone_names: Set of bone names that have transforms to save/load
        
    Returns:
        set: All bone names that need inheritance flattening context
    """
    all_bones_needed = set(target_bone_names)
    
    # Get current inherit_scale settings for analysis
    inherit_scale_settings = {}
    original_mode = bpy.context.mode
    
    # Switch to edit mode to read inherit_scale
    if bpy.context.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    for edit_bone in armature.data.edit_bones:
        inherit_scale_settings[edit_bone.name] = edit_bone.inherit_scale
    
    # Restore original mode
    if original_mode == 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    elif original_mode == 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Analyze inheritance chains from each scaled bone
    for bone_name in target_bone_names:
        if bone_name in armature.pose.bones:
            pose_bone = armature.pose.bones[bone_name]
            bone_inherit_scale = inherit_scale_settings.get(bone_name, 'FULL')
            
            # Check if this bone has scaling (the inheritance source)
            scale = pose_bone.scale
            has_scale_change = not (abs(scale.x - 1.0) < 0.0001 and abs(scale.y - 1.0) < 0.0001 and abs(scale.z - 1.0) < 0.0001)
            
            # CORRECTED LOGIC: Any bone with scaling can be inherited FROM (regardless of its own inherit_scale)
            if has_scale_change:
                print(f"INHERITANCE CHAIN: Analyzing descendants of scaled bone '{bone_name}' (source inherit_scale={bone_inherit_scale})")
                # Trace all inheritance chains from this scaled bone - children decide if they inherit
                trace_inheritance_chain(pose_bone, inherit_scale_settings, all_bones_needed)
    
    return all_bones_needed


def trace_inheritance_chain(parent_bone, inherit_scale_settings, bones_needed, depth=0):
    """
    Recursively trace inheritance chains, stopping at bones with inherit_scale=NONE.
    
    Args:
        parent_bone: Current parent bone to trace from
        inherit_scale_settings: Dict of bone_name -> inherit_scale
        bones_needed: Set to add bones that need flattening context
        depth: Current recursion depth for debug output
    """
    indent = "  " * depth
    
    for child in parent_bone.children:
        child_inherit_scale = inherit_scale_settings.get(child.name, 'FULL')
        
        if child_inherit_scale == 'FULL':
            # Child inherits from parent - add to flattening context and continue chain
            bones_needed.add(child.name)
            print(f"{indent}+ Added '{child.name}' (inherit_scale=FULL, continues chain)")
            
            # Continue tracing this inheritance chain
            trace_inheritance_chain(child, inherit_scale_settings, bones_needed, depth + 1)
            
        elif child_inherit_scale == 'NONE':
            # Child breaks inheritance chain - DON'T add to context and DON'T continue chain
            print(f"{indent}+ '{child.name}' (inherit_scale=NONE, BREAKS chain - not added)")
            print(f"{indent}  └─ Chain broken: descendants of '{child.name}' won't inherit scaling")
            
        else:
            # Other inherit_scale modes (e.g., 'ALIGNED') - treat as chain continuation for safety
            bones_needed.add(child.name)
            print(f"{indent}+ Added '{child.name}' (inherit_scale={child_inherit_scale}, assumed continuation)")
            trace_inheritance_chain(child, inherit_scale_settings, bones_needed, depth + 1)


def flatten_bone_transforms_for_save(armature, target_bone_names, statistical_bone_names=None):
    """
    Calculate flattened bone transforms mathematically without modifying the armature.
    This computes what the pose transforms would need to be if inherit_scale=NONE
    to achieve the same visual result.
    
    Args:
        armature: Blender armature object
        target_bone_names: Set of ALL bone names to capture flattened transforms for
        statistical_bone_names: Set of bone names that have actual statistical transforms (sources)
        
    Returns:
        dict: Flattened bone transform data {bone_name: {location, rotation, scale}}
    """
    try:
        print(f"FLATTEN SAVE: Mathematically flattening inheritance for {len(target_bone_names)} bones")
        
        # Ensure we're in pose mode for matrix calculations
        original_mode = bpy.context.mode
        if bpy.context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        # Force scene update to ensure accurate matrices
        bpy.context.view_layer.update()
        bpy.context.view_layer.depsgraph.update()
        
        # Read current inherit_scale settings first
        inherit_scale_settings = {}
        current_mode = bpy.context.mode
        
        # Switch to edit mode to read inherit_scale settings
        if not current_mode.startswith('EDIT'):
            try:
                bpy.ops.object.mode_set(mode='EDIT')
                for edit_bone in armature.data.edit_bones:
                    inherit_scale_settings[edit_bone.name] = edit_bone.inherit_scale
                # Switch back to original mode
                if current_mode.startswith('POSE'):
                    bpy.ops.object.mode_set(mode='POSE')
                elif current_mode.startswith('OBJECT'):
                    bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as e:
                print(f"FLATTEN SAVE: Could not read inherit_scale settings: {e}")
                # Fallback - assume all bones inherit scale
                for bone_name in target_bone_names:
                    inherit_scale_settings[bone_name] = 'FULL'
        else:
            # Already in edit mode
            for edit_bone in armature.data.edit_bones:
                inherit_scale_settings[edit_bone.name] = edit_bone.inherit_scale
        
        print(f"FLATTEN SAVE: Read inherit_scale settings for {len(inherit_scale_settings)} bones")
        
        # Get all bones that need flattening context (target bones + children)
        all_bones_to_flatten = get_bones_requiring_flatten_context(armature, target_bone_names)
        print(f"FLATTEN SAVE: Total bones requiring context: {len(all_bones_to_flatten)}")
        
        # Calculate flattened transforms mathematically
        flattened_data = {}
        
        # Use statistical_bone_names to distinguish sources from inheritance children
        if statistical_bone_names is None:
            statistical_bone_names = target_bone_names  # Fallback for backwards compatibility
        
        for bone_name in all_bones_to_flatten:
            if bone_name not in armature.pose.bones:
                continue
                
            pose_bone = armature.pose.bones[bone_name]
            
            # Get the current pose matrix (only user's changes, not rest pose)
            pose_matrix = pose_bone.matrix_basis.copy()
            
            # Determine if this bone needs inheritance flattening
            # FIXED LOGIC: Only apply inheritance if bone actually inherits (inherit_scale != 'NONE')
            is_statistical_bone = bone_name in statistical_bone_names
            
            # Get the bone's current inherit_scale setting
            bone_inherit_scale = inherit_scale_settings.get(bone_name, 'FULL')
            
            # Check if this bone is in an inheritance chain by finding scaled ancestors
            has_scaled_ancestor = False
            current_bone = pose_bone
            while current_bone.parent and not has_scaled_ancestor:
                parent = current_bone.parent
                if parent.name in statistical_bone_names:
                    has_scaled_ancestor = True
                    break
                current_bone = parent
            
            # CRITICAL FIX: Only apply inheritance if bone actually inherits scale
            should_inherit_scaling = (bone_inherit_scale != 'NONE' and has_scaled_ancestor)
            is_inheritance_child = (bone_name in all_bones_to_flatten and should_inherit_scaling)
            
            print(f"FLATTEN DEBUG: Bone '{bone_name}' - statistical: {is_statistical_bone}, inherit_scale: {bone_inherit_scale}, has_scaled_ancestor: {has_scaled_ancestor}, should_inherit: {should_inherit_scaling}")
            
            if is_inheritance_child:
                # Find the source bone (target bone) that this child inherits from
                # by tracing back through parent hierarchy to find scaled ancestor
                source_bone_name = None
                current_bone = pose_bone
                
                # Trace back through parents to find a bone with scaling (statistical bone)
                while current_bone.parent and source_bone_name is None:
                    parent = current_bone.parent
                    if parent.name in statistical_bone_names:
                        # Found scaled parent in statistical bones
                        source_bone_name = parent.name
                        break
                    current_bone = parent
                
                print(f"FLATTEN DEBUG: Child '{bone_name}' inherits from source '{source_bone_name}'")
                
                if source_bone_name and source_bone_name in armature.pose.bones:
                    # Get source bone's scaling from their pose matrix
                    source_pose_bone = armature.pose.bones[source_bone_name]
                    source_pose_matrix = source_pose_bone.matrix_basis.copy()
                    source_loc, source_rot, source_scale = source_pose_matrix.decompose()
                    print(f"FLATTEN DEBUG: Source '{source_bone_name}' matrix_basis scale: ({source_scale.x:.3f}, {source_scale.y:.3f}, {source_scale.z:.3f})")
                    
                    # Calculate the inherited scaling factor
                    current_loc, current_rot, current_scale = pose_matrix.decompose()
                    print(f"FLATTEN DEBUG: Child '{bone_name}' current scale: ({current_scale.x:.3f}, {current_scale.y:.3f}, {current_scale.z:.3f})")
                    
                    # Apply source bone's scaling to current bone's scaling to flatten inheritance
                    # Only if the bone actually inherits (inherit_scale != 'NONE')
                    if bone_inherit_scale != 'NONE':
                        flattened_scale = Vector((
                            current_scale.x * source_scale.x,
                            current_scale.y * source_scale.y, 
                            current_scale.z * source_scale.z
                        ))
                        print(f"FLATTEN DEBUG: Child '{bone_name}' (inherit_scale={bone_inherit_scale}) calculated flattened scale: ({flattened_scale.x:.3f}, {flattened_scale.y:.3f}, {flattened_scale.z:.3f})")
                    else:
                        # Bone doesn't inherit - keep current scale as-is
                        flattened_scale = current_scale
                        print(f"FLATTEN DEBUG: Child '{bone_name}' (inherit_scale=NONE) keeping original scale: ({flattened_scale.x:.3f}, {flattened_scale.y:.3f}, {flattened_scale.z:.3f})")
                    
                    # Reconstruct matrix with flattened scaling but same location/rotation
                    import mathutils
                    flattened_matrix = mathutils.Matrix.LocRotScale(current_loc, current_rot, flattened_scale)
                else:
                    print(f"FLATTEN DEBUG: No valid source bone found for '{bone_name}', using as-is")
                    flattened_matrix = pose_matrix
            else:
                # No inheritance or root bone - use pose matrix as-is
                # Also applies to bones with inherit_scale=NONE
                print(f"FLATTEN DEBUG: Bone '{bone_name}' using pose matrix as-is (no inheritance needed)")
                flattened_matrix = pose_matrix
            
            # Decompose the flattened matrix into location, rotation, scale
            location, rotation, scale = flattened_matrix.decompose()
            
            flattened_data[bone_name] = {
                'location': [location.x, location.y, location.z],
                'rotation_quaternion': [rotation.w, rotation.x, rotation.y, rotation.z],
                'scale': [scale.x, scale.y, scale.z]
            }
            
            print(f"FLATTEN SAVE: {bone_name} calculated flattened scale: ({scale.x:.3f}, {scale.y:.3f}, {scale.z:.3f})")
        
        # Restore original mode
        if original_mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        elif original_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        print(f"FLATTEN SAVE: Calculated {len(flattened_data)} flattened bone transforms mathematically")
        return flattened_data
        
    except Exception as e:
        print(f"FLATTEN SAVE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {}


def get_all_descendants(parent_bone, inherit_scale_settings, descendants_set, depth=0):
    """
    Recursively get ALL descendants of a bone, regardless of inherit_scale settings.
    This is for pose history loading where we want to force inherit_scale=NONE on
    ALL descendants to prevent any unwanted visual scaling.
    
    Args:
        parent_bone: Parent bone to get descendants from
        inherit_scale_settings: Dict of bone_name -> inherit_scale (for logging)
        descendants_set: Set to add descendant bone names to
        depth: Current recursion depth for debug output
    """
    indent = "  " * depth
    
    for child in parent_bone.children:
        child_inherit_scale = inherit_scale_settings.get(child.name, 'FULL')
        descendants_set.add(child.name)
        print(f"{indent}+ Added descendant '{child.name}' (was inherit_scale={child_inherit_scale})")
        
        # Always continue to ALL children, regardless of inherit_scale
        get_all_descendants(child, inherit_scale_settings, descendants_set, depth + 1)


def prepare_bones_for_flattened_load(armature, target_bone_names):
    """
    Prepare bones for loading flattened transforms by setting inherit_scale=NONE
    on all target bones and ALL their descendants (for pose history loading).
    
    Args:
        armature: Blender armature object  
        target_bone_names: Set of bone names that will receive flattened transforms
        
    Returns:
        dict: Original inherit_scale settings for restoration
    """
    try:
        print(f"FLATTEN LOAD: Preparing {len(target_bone_names)} bones for flattened loading")
        
        # For pose history loading, we need ALL descendants, not just inheritance chains
        # This ensures skirt, spine, lower legs, etc. all get inherit_scale=NONE
        all_bones_to_flatten = set(target_bone_names)
        
        # Get current inherit_scale settings for analysis
        inherit_scale_settings = {}
        original_mode = bpy.context.mode
        
        # Switch to edit mode to read inherit_scale
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        for edit_bone in armature.data.edit_bones:
            inherit_scale_settings[edit_bone.name] = edit_bone.inherit_scale
        
        # Switch to pose mode to access bone hierarchy
        bpy.ops.object.mode_set(mode='POSE')
        
        # Find ALL descendants of ALL target bones (not just scaled ones)
        # For preset/pose history loading, we want to prevent ANY unwanted inheritance
        for bone_name in target_bone_names:
            if bone_name in armature.pose.bones:
                pose_bone = armature.pose.bones[bone_name]
                print(f"FLATTEN LOAD: Finding ALL descendants of target bone '{bone_name}'")
                get_all_descendants(pose_bone, inherit_scale_settings, all_bones_to_flatten)
        
        print(f"FLATTEN LOAD: Total bones requiring inherit_scale=NONE: {len(all_bones_to_flatten)}")
        
        # Store original inherit_scale settings for restoration
        original_inherit_scales = {}
        
        # Switch back to edit mode to modify inherit_scale
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Set inherit_scale=NONE for ALL bones (target + descendants)
        for bone_name in all_bones_to_flatten:
            if bone_name in armature.data.edit_bones:
                edit_bone = armature.data.edit_bones[bone_name]
                original_inherit_scales[bone_name] = edit_bone.inherit_scale
                edit_bone.inherit_scale = 'NONE'
        
        print(f"FLATTEN LOAD: Set {len(original_inherit_scales)} bones to inherit_scale=NONE")
        
        # Switch to pose mode for transform loading
        bpy.ops.object.mode_set(mode='POSE')
        
        # Force scene update
        bpy.context.view_layer.update()
        bpy.context.view_layer.depsgraph.update()
        
        return original_inherit_scales
        
    except Exception as e:
        print(f"FLATTEN LOAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {}


def restore_original_inherit_scales(armature, original_inherit_scales):
    """
    Restore original inherit_scale settings after flattened loading.
    
    Args:
        armature: Blender armature object
        original_inherit_scales: Dict of bone_name -> original inherit_scale
    """
    try:
        if not original_inherit_scales:
            return
        
        print(f"FLATTEN RESTORE: Restoring inherit_scale for {len(original_inherit_scales)} bones")
        
        original_mode = bpy.context.mode
        
        # Switch to edit mode to restore inherit_scale
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        for bone_name, original_inherit_scale in original_inherit_scales.items():
            if bone_name in armature.data.edit_bones:
                edit_bone = armature.data.edit_bones[bone_name]
                edit_bone.inherit_scale = original_inherit_scale
        
        # Restore original mode
        if original_mode == 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        elif original_mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Force scene update
        bpy.context.view_layer.update()
        
        print(f"FLATTEN RESTORE: Inheritance context restored")
        
    except Exception as e:
        print(f"FLATTEN RESTORE ERROR: {e}")
        import traceback
        traceback.print_exc()


# Convenience function for systems that want to handle restoration manually
def apply_flattened_transforms(armature, flattened_data):
    """
    Apply flattened transform data to bones (assumes inherit_scale=NONE already set).
    
    Args:
        armature: Blender armature object
        flattened_data: Dict of bone transforms from flatten_bone_transforms_for_save()
    """
    try:
        print(f"FLATTEN APPLY: Applying {len(flattened_data)} flattened transforms")
        
        # Ensure we're in pose mode
        if bpy.context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        applied_count = 0
        for bone_name, transform_data in flattened_data.items():
            if bone_name in armature.pose.bones:
                pose_bone = armature.pose.bones[bone_name]
                
                # Apply flattened transforms
                pose_bone.location = Vector(transform_data['location'])
                pose_bone.rotation_quaternion = Quaternion(transform_data['rotation_quaternion'])
                pose_bone.scale = Vector(transform_data['scale'])
                
                applied_count += 1
        
        # Force scene update
        bpy.context.view_layer.update()
        
        print(f"FLATTEN APPLY: Applied transforms to {applied_count} bones")
        
    except Exception as e:
        print(f"FLATTEN APPLY ERROR: {e}")
        import traceback
        traceback.print_exc()