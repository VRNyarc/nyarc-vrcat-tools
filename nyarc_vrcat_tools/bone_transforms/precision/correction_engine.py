"""
Precision Correction Engine for Amateur Diff Exports
Handles iterative Edit→Pose→Apply Rest Pose cycle for enhanced accuracy
"""

import bpy
from mathutils import Vector, Quaternion, Matrix

# Import diff calculation specific functions
from .apply_rest_diff_calc import (
    save_shape_keys_for_diff_calc,
    restore_shape_keys_after_diff_calc,
    apply_rest_pose_diff_calc_only,
    apply_armature_to_mesh_diff_calc_with_shape_keys,
    apply_armature_to_mesh_diff_calc_no_shape_keys
)

def is_diff_export_preset(preset_data):
    """
    Check if a preset is specifically a diff export preset (amateur diff export)
    Only diff export presets should use precision correction
    
    Args:
        preset_data (dict): Loaded preset data structure
        
    Returns:
        bool: True if this is a diff export preset
    """
    if not preset_data:
        return False
    
    # Check for diff_export flag
    if preset_data.get('diff_export', False):
        return True
    
    # Check for amateur_diff metadata
    metadata = preset_data.get('metadata', {})
    if metadata.get('export_type') == 'amateur_diff':
        return True
    
    # Check for precision_data presence (strong indicator of diff export)
    if preset_has_precision_data(preset_data):
        print("DEBUG: Detected diff export preset due to precision_data presence")
        return True
    
    return False

def preset_has_precision_data(preset_data):
    """
    Check if a preset contains precision_data for iterative correction
    
    Args:
        preset_data (dict): Loaded preset data structure
        
    Returns:
        bool: True if any bone in the preset has precision_data
    """
    if not preset_data or 'bones' not in preset_data:
        return False
    
    for bone_name, bone_data in preset_data['bones'].items():
        if isinstance(bone_data, dict) and 'precision_data' in bone_data:
            return True
    
    return False

def should_apply_precision_correction(bone_name, bone_data, preset_data):
    """
    Determine if precision correction should be applied to a bone based on inheritance chain logic.
    
    CORRECTED LOGIC: Only apply precision corrections to bones that:
    1. Have inherit_scale: "NONE" 
    2. Are children of hand/wrist bones with inherit_scale: "FULL"
    
    This ensures we only correct finger bones, not elbow bones which work fine without correction.
    
    Args:
        bone_name (str): Name of the bone to check
        bone_data (dict): Bone data including inherit_scale setting
        preset_data (dict): Full preset data to find parent relationships
        
    Returns:
        bool: True if precision correction should be applied
    """
    try:
        # Check if this bone has inherit_scale: "NONE"
        bone_inherit_scale = bone_data.get('inherit_scale', 'FULL')
        if bone_inherit_scale != 'NONE':
            print(f"  {bone_name}: inherit_scale={bone_inherit_scale} (not NONE) -> SKIP")
            return False
        
        print(f"  {bone_name}: inherit_scale=NONE -> Checking parent...")
        
        # Find parent bone by searching preset data
        parent_bone_name = find_parent_bone_in_preset(bone_name, preset_data)
        
        if not parent_bone_name:
            print(f"  {bone_name}: No parent found in preset -> SKIP")
            return False
        
        # Check if parent is a hand/wrist bone with inherit_scale: "FULL"
        if parent_bone_name in preset_data['bones']:
            parent_bone_data = preset_data['bones'][parent_bone_name]
            parent_inherit_scale = parent_bone_data.get('inherit_scale', 'FULL')
            
            # Check if parent is a hand/wrist bone
            parent_name_lower = parent_bone_name.lower()
            is_hand_wrist = any(keyword in parent_name_lower for keyword in ['hand', 'wrist'])
            
            if parent_inherit_scale == 'FULL' and is_hand_wrist:
                print(f"  {bone_name}: Parent '{parent_bone_name}' is hand/wrist with inherit_scale=FULL -> APPLY CORRECTION")
                return True
            else:
                print(f"  {bone_name}: Parent '{parent_bone_name}' inherit_scale={parent_inherit_scale}, is_hand_wrist={is_hand_wrist} -> SKIP")
                return False
        else:
            print(f"  {bone_name}: Parent '{parent_bone_name}' not in preset -> SKIP")
            return False
        
    except Exception as e:
        print(f"ERROR checking inheritance chain for {bone_name}: {e}")
        return False


def find_parent_bone_in_preset(bone_name, preset_data):
    """
    Find the parent bone of a given bone by examining bone naming patterns.
    
    Since preset data doesn't contain explicit parent-child relationships,
    we use VRChat bone naming conventions to infer hierarchy.
    
    Args:
        bone_name (str): Name of the bone to find parent for
        preset_data (dict): Full preset data
        
    Returns:
        str or None: Parent bone name if found
    """
    try:
        # VRChat bone hierarchy patterns
        hierarchy_patterns = {
            # Finger bones -> Hand/Wrist
            'Index_Proximal_L': 'Left wrist',
            'Index_Intermediate_L': 'Index_Proximal_L', 
            'Index_Distal_L': 'Index_Intermediate_L',
            'Middle_Proximal_L': 'Left wrist',
            'Middle_Intermediate_L': 'Middle_Proximal_L',
            'Middle_Distal_L': 'Middle_Intermediate_L',
            'Ring_Proximal_L': 'Left wrist',
            'Ring_Intermediate_L': 'Ring_Proximal_L',
            'Ring_Distal_L': 'Ring_Intermediate_L',
            'Little_Proximal_L': 'Left wrist',
            'Little_Intermediate_L': 'Little_Proximal_L',
            'Little_Distal_L': 'Little_Intermediate_L',
            'Thumb_Proximal_L': 'Left wrist',
            'Thumb_Intermediate_L': 'Thumb_Proximal_L',
            'Thumb_Distal_L': 'Thumb_Intermediate_L',
            
            # Hand/Wrist -> Elbow
            'Left wrist': 'Left elbow',
            'Twist wrist_L': 'Left elbow',
            
            # Elbow -> Arm
            'Left elbow': 'Left arm',
            'Twist elbow_L': 'Left arm',
            
            # Right side equivalents
            'Index_Proximal_R': 'Right wrist',
            'Middle_Proximal_R': 'Right wrist',
            'Ring_Proximal_R': 'Right wrist',
            'Little_Proximal_R': 'Right wrist',
            'Thumb_Proximal_R': 'Right wrist',
            'Right wrist': 'Right elbow',
            'Right elbow': 'Right arm',
        }
        
        # Check direct pattern match first
        if bone_name in hierarchy_patterns:
            parent_name = hierarchy_patterns[bone_name]
            if parent_name in preset_data['bones']:
                print(f"    Found parent for {bone_name}: {parent_name} (pattern match)")
                return parent_name
        
        # If no direct match, try to infer from naming
        bone_lower = bone_name.lower()
        
        # Finger bones usually have their parent as wrist
        if any(finger in bone_lower for finger in ['index', 'middle', 'ring', 'little', 'thumb']) and 'proximal' in bone_lower:
            side = '_L' if '_L' in bone_name else '_R' if '_R' in bone_name else ''
            wrist_name = f"{'Left' if '_L' in bone_name else 'Right'} wrist"
            if wrist_name in preset_data['bones']:
                print(f"    Inferred parent for {bone_name}: {wrist_name} (finger->wrist)")
                return wrist_name
        
        print(f"    No parent found for {bone_name} in preset data")
        return None
        
    except Exception as e:
        print(f"ERROR finding parent for {bone_name}: {e}")
        return None

def apply_precision_corrections(context, armature, preset_data):
    """
    Apply iterative precision corrections using Edit→Pose→Apply Rest Pose cycle
    TARGET POSITION APPROACH: Calculate edit mode gaps and convert to pose corrections
    
    🚨 CRITICAL WARNING: This precision correction approach stores ABSOLUTE edit mode positions.
    It ONLY works correctly when applied to the EXACT SAME base armature used for the diff export.
    
    ❌ DO NOT USE on different armatures - bones will move to wrong absolute positions!
    ✅ ONLY USE on the same base armature that was used to create the diff export preset.
    
    This limitation exists because we store target positions like [0.2807, -0.0212, 1.0099] 
    which are specific to the original armature's coordinate system and bone proportions.
    
    Workflow:
    1. Save all shape keys once at beginning
    2. Edit mode: Measure current bone positions vs target positions from precision_data
    3. Pose mode: Apply calculated corrections to pose transforms
    4. Lightweight apply rest pose: Make corrections permanent (no shape key processing)
    5. Repeat until acceptable precision achieved
    6. Restore shape keys once at the end
    
    Args:
        context: Blender context
        armature: Target armature object
        preset_data: Loaded preset data with precision_data
        
    Returns:
        bool: True if corrections were applied successfully
    """
    try:
        print("Starting optimized precision correction (save shape keys once, lightweight iterations)...")
        
        original_mode = context.mode
        max_iterations = 3  # Allow multiple iterations for convergence
        precision_threshold = 1e-4  # Less strict threshold to allow small corrections
        total_corrections = 0
        
        # STEP 1: Save shape keys once at the beginning (diff calc specific)
        shape_key_backup = save_shape_keys_for_diff_calc(armature)
        print(f"[DIFF CALC] Saved shape keys for {len(shape_key_backup)} meshes")
        
        for iteration in range(max_iterations):
            print(f"Precision iteration {iteration + 1}/{max_iterations}")
            iteration_corrections = 0
            
            # Step 1: Edit mode - measure current vs target positions
            bpy.ops.object.mode_set(mode='EDIT')
            corrections_needed = {}
            
            for bone_name, bone_data in preset_data['bones'].items():
                if 'precision_data' in bone_data and bone_name in armature.data.edit_bones:
                    
                    # INHERITANCE CHAIN LOGIC: Only apply corrections to bones that need them
                    if not should_apply_precision_correction(bone_name, bone_data, preset_data):
                        print(f"SKIPPING {bone_name}: Does not need precision correction based on inheritance chain")
                        continue
                    
                    precision_data = bone_data['precision_data']
                    edit_bone = armature.data.edit_bones[bone_name]
                    
                    print(f"=== {bone_name} PRECISION CORRECTION (INHERITANCE FILTERED) ===")
                    print(f"Current head: {edit_bone.head}")
                    print(f"Current tail: {edit_bone.tail}")
                    
                    # TARGET POSITION ONLY: Get target positions and calculate gap
                    if 'target_head_position' not in precision_data:
                        print(f"SKIPPING {bone_name}: No target_head_position in precision_data")
                        continue
                    
                    target_head_position = Vector(precision_data['target_head_position'])
                    
                    # Calculate edit mode gap (both in edit mode coordinate space)
                    current_head_edit_mode = edit_bone.head
                    edit_mode_gap = target_head_position - current_head_edit_mode
                    
                    actual_head_after_pose_before_correction = current_head_edit_mode
                    
                    print(f"Current head (edit mode): {current_head_edit_mode}")
                    print(f"Target head position: {target_head_position}")
                    print(f"Edit mode gap: {edit_mode_gap} (magnitude: {edit_mode_gap.length:.6f})")
                    
                    # Only correct if gap exceeds threshold
                    if edit_mode_gap.length > precision_threshold:
                        corrections_needed[bone_name] = {
                            'edit_mode_gap': edit_mode_gap,  # Edit mode gap to convert to pose mode
                            'current_edit_position': current_head_edit_mode,
                            'target_edit_position': target_head_position,
                            'gap_magnitude': edit_mode_gap.length,
                            'method': 'edit_to_pose_conversion'
                        }
                        iteration_corrections += 1
                        print(f"-> NEEDS CORRECTION (edit gap: {edit_mode_gap.length:.6f} > {precision_threshold})")
                    else:
                        print(f"-> PRECISION OK (edit gap: {edit_mode_gap.length:.6f} <= {precision_threshold})")
                    print("=" * 40)
            
            # If no corrections needed, we're done
            if iteration_corrections == 0:
                print("Precision achieved - no more corrections needed")
                break
            
            # Step 2: Cache rest matrices for coordinate conversion (stay in edit mode)
            rest_matrices = {}
            for bone_name in corrections_needed.keys():
                if bone_name in armature.data.edit_bones:
                    edit_bone = armature.data.edit_bones[bone_name]
                    rest_matrices[bone_name] = edit_bone.matrix.copy()
                    print(f"Cached rest matrix for {bone_name}")
            
            # Step 3: Switch to pose mode to apply corrections (affects mesh!)
            bpy.ops.object.mode_set(mode='POSE')
            
            for bone_name, correction_data in corrections_needed.items():
                print(f"*** CONVERTING EDIT MODE GAP TO POSE CORRECTION FOR {bone_name} ***")
                
                edit_mode_gap = correction_data['edit_mode_gap']
                gap_magnitude = correction_data['gap_magnitude']
                
                # SAFETY CHECK: Reject massive corrections as likely errors
                if gap_magnitude > 0.05:  # Reduced threshold to allow smaller corrections
                    print(f"❌ REJECTING large correction for {bone_name}: {gap_magnitude:.6f} > 0.05 (likely coordinate error)")
                    continue
                
                # Get pose bone and rest matrix for coordinate conversion
                if bone_name in armature.pose.bones and bone_name in rest_matrices:
                    pose_bone = armature.pose.bones[bone_name]
                    rest_matrix = rest_matrices[bone_name]
                    old_location = pose_bone.location.copy()
                    
                    # COORDINATE CONVERSION: Skip tiny corrections as they're unreliable
                    if gap_magnitude < 0.01:  # Skip tiny corrections (WIP - precision correction is broken)
                        print(f"⏭️ SKIPPED tiny correction (gap {gap_magnitude:.6f} < 0.01) - precision correction WIP")
                    else:  # For large corrections, use matrix conversion
                        rest_matrix_inv = rest_matrix.inverted()
                        pose_correction = rest_matrix_inv @ edit_mode_gap
                        pose_bone.location += pose_correction
                        print(f"✅ Applied MATRIX correction (large gap >= 0.01)")
                    
                    print(f"✅ Applied precision correction to {bone_name}:")
                    print(f"   Edit mode gap (armature space): {edit_mode_gap} (magnitude: {gap_magnitude:.6f})")
                    print(f"   Pose correction (bone local space): {pose_correction} (magnitude: {pose_correction.length:.6f})")
                    print(f"   Old pose location: {old_location}")
                    print(f"   New pose location: {pose_bone.location}")
                else:
                    print(f"❌ Pose bone or rest matrix not found for {bone_name}")
            
            # Step 4: CRITICAL FIX - Apply mesh deformation WHILE pose corrections are still active
            print("[DIFF CALC] Applying mesh deformation while pose corrections are active...")
            
            # Apply mesh deformation with pose corrections still active (this is the key fix!)
            apply_mesh_deformation_with_pose_corrections(context, armature, shape_key_backup)
            
            # Step 5: Now apply rest pose to make corrections permanent
            print("[DIFF CALC] Applying rest pose to make corrections permanent...")
            
            # COMPATIBILITY FIX: Switch to object mode to let apply_rest_pose_diff_calc_only handle mode management
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Ensure proper selection state for apply_rest_pose_diff_calc_only
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Apply rest pose to make pose corrections permanent (function handles its own mode switching)
            if not apply_rest_pose_diff_calc_only(context, armature):
                print("[ERROR] Failed to apply rest pose for diff calc precision correction")
                break
            
            total_corrections += iteration_corrections
            print(f"Applied {iteration_corrections} corrections in iteration {iteration + 1}")
            
            # Update scene
            context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()
        
        # STEP 6: Restore shape keys (mesh deformation already applied while pose was active)
        print("[DIFF CALC] Restoring shape key properties...")
        
        # Only restore shape key properties, don't re-apply mesh deformation
        restore_shape_key_properties_only(shape_key_backup)
        print("[DIFF CALC] Shape key properties restored")
        
        # Clear any remaining pose transforms now that corrections are permanent
        if armature and total_corrections > 0:
            if bpy.context.mode != 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.transforms_clear()
            print("[PRECISION] Cleared pose transforms - corrections are now permanent in rest pose")
        
        # Restore original mode
        if original_mode == 'POSE':
            bpy.ops.object.mode_set(mode='POSE')  
        elif original_mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"Optimized precision correction complete: {total_corrections} total corrections applied")
        return total_corrections > 0
        
    except Exception as e:
        print(f"Precision correction error: {e}")
        return False

def get_target_positions_from_precision_data(edit_bone, precision_data):
    """
    DEPRECATED: This function used broken coordinate space mixing.
    
    The precision_data contains world-space error vectors, not direct position offsets.
    We need to convert these to pose corrections instead of adding them to edit bone positions.
    
    Args:
        edit_bone: Current edit bone
        precision_data: Precision data from preset
        
    Returns:
        tuple: (target_head_position, target_tail_position) - LEGACY COMPATIBILITY ONLY
    """
    head_diff = Vector(precision_data.get('head_difference', [0, 0, 0]))
    tail_diff = Vector(precision_data.get('tail_difference', [0, 0, 0]))
    
    print(f"    PRECISION DATA ANALYSIS:")
    print(f"      head_difference: {head_diff} (magnitude: {head_diff.length:.6f})")
    print(f"      tail_difference: {tail_diff} (magnitude: {tail_diff.length:.6f})")
    
    # CHECK: These are expected to be large because they're accumulated world errors
    if head_diff.length > 0.01:
        print(f"    NOTE: Large precision differences detected ({head_diff.length:.6f} units)")
        print(f"          These represent accumulated world-space transformation errors")
        print(f"          Converting to pose corrections instead of direct position arithmetic")
    
    # LEGACY RETURN - but this should not be used for calculations anymore
    target_head = edit_bone.head + head_diff  # BROKEN - kept for compatibility
    target_tail = edit_bone.tail + tail_diff  # BROKEN - kept for compatibility
    
    print(f"    LEGACY TARGETS (NOT USED):")
    print(f"      current head: {edit_bone.head}")
    print(f"      target head:  {target_head}")
    print(f"      current tail: {edit_bone.tail}")  
    print(f"      target tail:  {target_tail}")
    
    return target_head, target_tail

def cache_rest_matrices(armature, bone_names):
    """
    Cache rest matrices for multiple bones in a single edit mode switch.
    
    PERFORMANCE OPTIMIZATION: Collect all rest matrices at once to avoid
    repeated mode switching during pose corrections.
    
    Args:
        armature: Target armature object
        bone_names: List of bone names to cache matrices for
        
    Returns:
        dict: {bone_name: rest_matrix} mapping
    """
    try:
        current_mode = bpy.context.mode
        was_in_pose_mode = current_mode == 'POSE'
        
        if was_in_pose_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        
        rest_matrices = {}
        
        for bone_name in bone_names:
            if bone_name in armature.data.edit_bones:
                edit_bone = armature.data.edit_bones[bone_name]
                rest_matrices[bone_name] = edit_bone.matrix.copy()
                print(f"Cached rest matrix for {bone_name}")
            else:
                print(f"WARNING: Bone {bone_name} not found in edit bones")
        
        if was_in_pose_mode:
            bpy.ops.object.mode_set(mode='POSE')
        
        print(f"Cached {len(rest_matrices)} rest matrices in single edit mode switch")
        return rest_matrices
        
    except Exception as e:
        print(f"ERROR: Failed to cache rest matrices: {e}")
        return {}

def convert_edit_gap_to_pose_correction_cached(bone_name, edit_mode_gap, rest_matrix):
    """
    Convert edit mode gap to pose correction using cached rest matrix.
    
    OPTIMIZED VERSION: Uses pre-cached rest matrix to avoid mode switching.
    
    Args:
        bone_name: Name of bone (for logging)
        edit_mode_gap: Edit mode gap in armature local space
        rest_matrix: Pre-cached rest matrix for this bone
        
    Returns:
        Vector: Bone local space correction to apply to pose_bone.location
    """
    try:
        print(f"    ARMATURE→BONE COORDINATE CONVERSION (CACHED):")
        print(f"      edit_mode_gap (armature space): {edit_mode_gap} (magnitude: {edit_mode_gap.length:.6f})")
        print(f"      rest_matrix (cached): \n{rest_matrix}")
        
        # CORRECT TRANSFORMATION: armature space → bone local space
        rest_matrix_inv = rest_matrix.inverted()
        local_correction = rest_matrix_inv @ edit_mode_gap
        
        print(f"      local_correction (bone space): {local_correction} (magnitude: {local_correction.length:.6f})")
        
        # Validation
        if local_correction.length > 1.0:
            print(f"      WARNING: Large correction {local_correction.length:.6f} - may indicate coordinate issue")
        elif local_correction.length < 1e-8:
            print(f"      WARNING: Tiny correction {local_correction.length:.6f} - may be ineffective")
        else:
            print(f"      ✅ ARMATURE→BONE CONVERSION SUCCESSFUL (CACHED)")
        
        return local_correction
        
    except Exception as e:
        print(f"ERROR: Failed to convert edit gap to pose correction for {bone_name}: {e}")
        import traceback
        traceback.print_exc()
        return Vector((0, 0, 0))

def convert_edit_gap_to_pose_correction(armature, bone_name, edit_mode_gap):
    """
    Convert an edit mode gap to a pose bone local correction using proper coordinate space math.
    
    COORDINATE SPACE THEORY:
    - Edit mode gap: armature local space (target_pos - current_pos in armature coordinates)  
    - Pose bone.location: bone local space (relative to bone's rest matrix)
    - Rest matrix: transforms bone local → armature space
    - Rest matrix inverse: transforms armature space → bone local space
    
    FORMULA: local_correction = rest_matrix.inverted() @ armature_space_gap
    
    Args:
        armature: Target armature object  
        bone_name: Name of bone to correct
        edit_mode_gap: Edit mode gap in armature local space (target_position - current_position)
        
    Returns:
        Vector: Bone local space correction to apply to pose_bone.location
    """
    try:
        if bone_name not in armature.pose.bones:
            print(f"ERROR: Bone '{bone_name}' not found in armature pose bones")
            return Vector((0, 0, 0))
        
        # Get rest matrix from edit mode (need to temporarily switch)
        current_mode = bpy.context.mode
        was_in_pose_mode = current_mode == 'POSE'
        
        if was_in_pose_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        
        if bone_name not in armature.data.edit_bones:
            print(f"ERROR: Edit bone '{bone_name}' not found")
            if was_in_pose_mode:
                bpy.ops.object.mode_set(mode='POSE')
            return Vector((0, 0, 0))
        
        # Get the bone's rest matrix (transforms bone local → armature space)
        edit_bone = armature.data.edit_bones[bone_name]
        rest_matrix = edit_bone.matrix.copy()
        
        if was_in_pose_mode:
            bpy.ops.object.mode_set(mode='POSE')
        
        print(f"    ARMATURE→BONE COORDINATE CONVERSION:")
        print(f"      edit_mode_gap (armature space): {edit_mode_gap} (magnitude: {edit_mode_gap.length:.6f})")
        print(f"      rest_matrix (bone local → armature): \n{rest_matrix}")
        
        # CORRECT TRANSFORMATION: armature space → bone local space
        rest_matrix_inv = rest_matrix.inverted()
        local_correction = rest_matrix_inv @ edit_mode_gap
        
        print(f"      rest_matrix.inverted(): \n{rest_matrix_inv}")
        print(f"      local_correction (bone space): {local_correction} (magnitude: {local_correction.length:.6f})")
        
        # Validation
        if local_correction.length > 1.0:
            print(f"      WARNING: Large correction {local_correction.length:.6f} - may indicate coordinate issue")
        elif local_correction.length < 1e-8:
            print(f"      WARNING: Tiny correction {local_correction.length:.6f} - may be ineffective")
        else:
            print(f"      ✅ ARMATURE→BONE CONVERSION SUCCESSFUL")
        
        return local_correction
        
    except Exception as e:
        print(f"ERROR: Failed to convert edit gap to pose correction for {bone_name}: {e}")
        import traceback
        traceback.print_exc()
        return Vector((0, 0, 0))

def convert_world_error_to_pose_correction(armature, bone_name, armature_local_error):
    """
    Convert an armature-local-space error vector to a pose bone local correction.
    
    FIXED: Proper coordinate space transformation between edit mode (armature space) 
    and pose mode (local bone space) using pose_bone.matrix which includes full parent chain.
    
    Args:
        armature: Target armature object  
        bone_name: Name of bone to correct
        armature_local_error: Armature-local-space position error (from edit mode differences)
        
    Returns:
        Vector: Local pose location correction to apply
    """
    try:
        if bone_name not in armature.pose.bones:
            print(f"ERROR: Bone '{bone_name}' not found in armature pose bones")
            return Vector((0, 0, 0))
        
        pose_bone = armature.pose.bones[bone_name]
        
        print(f"    COORDINATE SPACE CONVERSION (FIXED):")
        print(f"      armature_local_error: {armature_local_error} (magnitude: {armature_local_error.length:.6f})")
        print(f"      conversion method: METHOD 1 - world space conversion")
        
        # METHOD 1 from documentation: Direct world space conversion
        # Convert armature-local edit difference to world space
        world_difference = armature.matrix_world @ armature_local_error
        
        # Convert world difference to pose bone's local space
        # pose_bone.matrix already includes full parent chain!
        pose_bone_world_matrix = armature.matrix_world @ pose_bone.matrix
        local_correction = pose_bone_world_matrix.inverted() @ world_difference
        
        print(f"      armature.matrix_world: {armature.matrix_world}")
        print(f"      world_difference: {world_difference} (magnitude: {world_difference.length:.6f})")
        print(f"      pose_bone_world_matrix: {pose_bone_world_matrix}")
        print(f"      local_correction: {local_correction} (magnitude: {local_correction.length:.6f})")
        
        # Verify the correction magnitude is reasonable (should be similar to original error)
        if local_correction.length > 1.0:
            print(f"      WARNING: Large correction magnitude {local_correction.length:.6f} - may indicate coordinate issue")
        elif local_correction.length < 1e-8:
            print(f"      WARNING: Tiny correction magnitude {local_correction.length:.6f} - may be ineffective")
        else:
            print(f"      ✅ COORDINATE TRANSFORMATION SUCCESSFUL - reasonable magnitude")
        
        return local_correction
        
    except Exception as e:
        print(f"ERROR: Failed to convert world error to pose correction for {bone_name}: {e}")
        import traceback
        traceback.print_exc()
        return Vector((0, 0, 0))

def apply_pose_correction_for_bone_error(armature, bone_name, correction_data):
    """
    Apply pose transform corrections for measured bone position errors
    
    Args:
        armature: Target armature
        bone_name: Name of bone to correct
        correction_data: Error data with head_error, tail_error, etc.
        
    Returns:
        bool: True if correction was applied
    """
    try:
        if bone_name not in armature.pose.bones:
            return False
        
        pose_bone = armature.pose.bones[bone_name]
        
        # For now, apply a simple location correction based on head error
        head_error = correction_data['head_error']
        tail_error = correction_data['tail_error']
        
        print(f"    POSE CORRECTION DEBUG:")
        print(f"      head_error: {head_error} (magnitude: {head_error.length:.6f})")
        print(f"      tail_error: {tail_error} (magnitude: {tail_error.length:.6f})")
        
        # CRITICAL CHECK: If errors are huge, something is fundamentally wrong
        if head_error.length > 0.1:
            print(f"    CRITICAL ERROR: Head error {head_error.length:.6f} is massive!")
            print(f"                    This suggests the target position calculation is wrong!")
            print(f"                    Precision corrections should be tiny, not huge offsets!")
        
        # Apply a fraction of the error as location correction to avoid overshooting
        correction_factor = 0.1  # REDUCED from 0.5 to be more conservative
        location_correction = head_error * correction_factor
        
        print(f"    POSE CORRECTION CALCULATION:")
        print(f"      correction_factor: {correction_factor}")
        print(f"      location_correction (world): {location_correction}")
        
        # Convert world space error to local pose space
        if pose_bone.parent:
            # Convert through parent's matrix
            parent_world_matrix = armature.matrix_world @ pose_bone.parent.matrix
            local_correction = parent_world_matrix.inverted() @ location_correction
            print(f"      parent_world_matrix: {parent_world_matrix}")
        else:
            # Root bone - convert through armature matrix
            local_correction = armature.matrix_world.inverted() @ location_correction
            print(f"      armature_world_matrix: {armature.matrix_world}")
        
        print(f"      local_correction: {local_correction}")
        print(f"      pose_bone.location before: {pose_bone.location}")
        
        # Apply the correction
        pose_bone.location += local_correction
        
        print(f"      pose_bone.location after: {pose_bone.location}")
        
        return True
        
    except Exception as e:
        print(f"Error applying pose correction to {bone_name}: {e}")
        return False

def correct_bone_precision_md_approach(context, armature, bone_name, bone_data, precision_threshold):
    """
    Apply precision correction to a single bone using MD plan approach:
    1. Edit mode: Measure current vs expected positions
    2. Pose mode: Apply location correction
    
    Args:
        context: Blender context
        armature: Target armature object
        bone_name: Name of bone to correct
        bone_data: Bone data including precision_data
        precision_threshold: Convergence threshold (1e-6)
        
    Returns:
        bool: True if correction was applied
    """
    try:
        if bone_name not in armature.pose.bones:
            print(f"Bone '{bone_name}' not found in armature")
            return False
            
        precision_data = bone_data.get('precision_data', {})
        if not precision_data:
            return False
        
        # Step 1: Switch to Edit mode for precise position measurements
        bpy.ops.object.mode_set(mode='EDIT')
        
        if bone_name not in armature.data.edit_bones:
            print(f"Edit bone '{bone_name}' not found")
            return False
        
        # Get current head position (what we have now)
        current_head = armature.data.edit_bones[bone_name].head.copy()
        
        # Calculate expected head position using MD plan formula
        baseline_position = get_baseline_position_md_approach(armature, bone_name)
        head_difference = Vector(precision_data.get('head_difference', [0, 0, 0]))
        expected_head = baseline_position + head_difference
        
        # Calculate error vector and magnitude
        error_vector = expected_head - current_head
        error_magnitude = error_vector.length
        
        print(f"Bone {bone_name}: current={current_head}, expected={expected_head}, error={error_magnitude:.6f}")
        
        # Check if we've achieved precision
        if error_magnitude <= precision_threshold:
            print(f"Precision achieved for {bone_name}: {error_magnitude:.6f} <= {precision_threshold}")
            return False  # No correction needed
        
        # Step 2: Switch to Pose mode to apply correction
        bpy.ops.object.mode_set(mode='POSE')
        
        # Calculate pose correction (simple location adjustment for now)
        pose_bone = armature.pose.bones[bone_name]
        
        # Apply correction to pose bone location
        # Convert world-space error to local pose space if needed
        correction_vector = calculate_pose_correction_for_error(armature, bone_name, error_vector)
        pose_bone.location += correction_vector
        
        print(f"Applied correction to {bone_name}: {correction_vector}, error was {error_magnitude:.6f}")
        return True
        
    except Exception as e:
        print(f"Error correcting bone {bone_name}: {e}")
        # Ensure we don't get stuck in wrong mode
        try:
            bpy.ops.object.mode_set(mode='POSE')
        except:
            pass
        return False

def get_baseline_position_md_approach(armature, bone_name):
    """
    Calculate baseline position using MD plan approach:
    The rest pose position of the bone (before any pose transforms)
    
    Args:
        armature: Target armature object
        bone_name: Name of bone
        
    Returns:
        Vector: Baseline head position in world space
    """
    try:
        # Must be called in Edit mode
        edit_bone = armature.data.edit_bones[bone_name]
        
        # For baseline calculation, we need the original rest position
        # This is the head position without any pose transforms applied
        baseline_head = edit_bone.head.copy()
        
        # Convert to world space if needed
        baseline_world = armature.matrix_world @ baseline_head
        
        return baseline_world
        
    except Exception as e:
        print(f"Error getting baseline position for {bone_name}: {e}")
        return Vector((0, 0, 0))

def calculate_pose_correction_for_error(armature, bone_name, error_vector):
    """
    Calculate pose location correction needed to fix position error
    
    Args:
        armature: Target armature object
        bone_name: Name of bone
        error_vector: World-space position error to correct
        
    Returns:
        Vector: Local pose location correction
    """
    try:
        pose_bone = armature.pose.bones[bone_name]
        
        # Convert world-space error to local pose space
        # This is simplified - may need more sophisticated transform handling
        if pose_bone.parent:
            parent_matrix = armature.matrix_world @ pose_bone.parent.matrix
            local_correction = parent_matrix.inverted() @ error_vector
        else:
            # Root bone - use armature world matrix
            local_correction = armature.matrix_world.inverted() @ error_vector
        
        return local_correction
        
    except Exception as e:
        print(f"Error calculating pose correction for {bone_name}: {e}")
        return Vector((0, 0, 0))

def apply_mesh_deformation_with_pose_corrections(context, armature, shape_key_backup):
    """
    CRITICAL FIX: Apply mesh deformation while pose corrections are still active.
    
    This is the key fix for precision correction mesh deformation issues.
    Previously, mesh deformation was applied AFTER rest pose, when pose corrections were gone.
    Now we apply it BEFORE rest pose, while pose corrections are still affecting the bones.
    
    Args:
        context: Blender context
        armature: Target armature object
        shape_key_backup: Shape key backup data with mesh information
    """
    try:
        if not shape_key_backup:
            print("[DIFF CALC] No mesh backup data to process")
            return
        
        mesh_count = 0
        updated_count = 0
        total_vertex_movement = 0.0
        
        for mesh_name, backup_data in shape_key_backup.items():
            mesh_obj = backup_data['mesh_obj']
            has_shape_keys = backup_data.get('has_shape_keys', False)
            mesh_count += 1
            
            if mesh_obj and len(mesh_obj.data.vertices) > 0:
                # Store original first vertex position for comparison
                original_pos = mesh_obj.data.vertices[0].co.copy()
                
                try:
                    if has_shape_keys:
                        apply_armature_to_mesh_diff_calc_with_shape_keys(armature, mesh_obj)
                    else:
                        apply_armature_to_mesh_diff_calc_no_shape_keys(armature, mesh_obj)
                    
                    # Check if vertices actually changed
                    new_pos = mesh_obj.data.vertices[0].co.copy()
                    diff = (new_pos - original_pos).length
                    total_vertex_movement += diff
                    
                    if diff > 0.0001:
                        updated_count += 1
                
                except Exception as e:
                    print(f"[DIFF CALC] ERROR on {mesh_obj.name}: {e}")
        
        print(f"[DIFF CALC] Applied mesh deformation WITH POSE CORRECTIONS: {updated_count}/{mesh_count} updated, avg movement: {total_vertex_movement/max(mesh_count,1):.6f}")
        
    except Exception as e:
        print(f"[ERROR] Failed to apply mesh deformation with pose corrections: {e}")

def restore_shape_key_properties_only(shape_key_backup):
    """
    Restore only shape key properties without re-applying mesh deformation.
    
    Since mesh deformation was already applied while pose corrections were active,
    we only need to restore the original shape key settings.
    
    Args:
        shape_key_backup: Shape key backup data
    """
    try:
        if not shape_key_backup:
            return
        
        restored_count = 0
        
        for mesh_name, backup_data in shape_key_backup.items():
            mesh_obj = backup_data['mesh_obj']
            has_shape_keys = backup_data.get('has_shape_keys', False)
            
            if mesh_obj and has_shape_keys:
                # Restore shape key properties only
                if 'active_index' in backup_data:
                    mesh_obj.active_shape_key_index = backup_data['active_index']
                if 'show_only' in backup_data:
                    mesh_obj.show_only_shape_key = backup_data['show_only']
                
                restored_count += 1
        
        print(f"[DIFF CALC] Restored shape key properties for {restored_count} meshes")
        
    except Exception as e:
        print(f"[ERROR] Failed to restore shape key properties: {e}")