"""
Armature Difference Calculations
Mathematical functions for comparing two armatures and calculating bone transform differences
Used specifically for armature diff export functionality
"""

import bpy
from mathutils import Vector, Matrix

def get_armature_transforms(armature):
    """Extract edit bone relative transforms and inherit_scale from an armature for structural comparison"""
    transforms = {}
    
    try:
        # Store current state
        original_active = bpy.context.view_layer.objects.active
        original_selected = bpy.context.selected_objects[:]
        original_mode = bpy.context.mode
        
        # Switch to object mode and select armature
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        
        # Get edit bone transforms (structural data)
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Extract edit bone matrices and calculate relative transforms
        for edit_bone in armature.data.edit_bones:
            # Get the edit bone's absolute matrix
            absolute_matrix = edit_bone.matrix.copy()
            
            # Calculate relative matrix (bone transform relative to its parent)
            if edit_bone.parent:
                # FIXED INHERITANCE LOGIC: Check the CHILD's inherit_scale setting, not parent's
                parent_matrix = edit_bone.parent.matrix.copy()
                
                if edit_bone.inherit_scale == 'NONE':
                    # THIS bone has inherit_scale='NONE' -> use unscaled parent matrix
                    # Extract only rotation and translation, set scale to (1,1,1)
                    parent_loc, parent_rot, parent_scale = parent_matrix.decompose()
                    
                    # Create new matrix with scale reset to (1,1,1) - use double precision
                    unscaled_parent_matrix = Matrix.LocRotScale(parent_loc, parent_rot, (1.0, 1.0, 1.0))
                    relative_matrix = unscaled_parent_matrix.inverted() @ absolute_matrix
                    
                    print(f"DEBUG DIFF: Child '{edit_bone.name}' has inherit_scale='NONE' - using unscaled parent matrix")
                else:
                    # Child has inherit_scale='FULL' or other - use full parent matrix
                    relative_matrix = parent_matrix.inverted() @ absolute_matrix
                    
                    if edit_bone.inherit_scale == 'FULL':
                        print(f"DEBUG DIFF: Child '{edit_bone.name}' has inherit_scale='FULL' - using full parent matrix from '{edit_bone.parent.name}'")
            else:
                # Root bone - use absolute matrix
                relative_matrix = absolute_matrix
            
            transforms[edit_bone.name] = {
                'relative_matrix': relative_matrix,
                'absolute_matrix': absolute_matrix,  # Keep for debugging
                'parent_name': edit_bone.parent.name if edit_bone.parent else None,
                'inherit_scale': edit_bone.inherit_scale,
                'bone_length': edit_bone.length  # Store actual bone length
            }
        
        return transforms
        
    except Exception as e:
        print(f"Error extracting transforms from {armature.name}: {e}")
        return {}
    
    finally:
        # Restore original state
        try:
            if bpy.context.mode != original_mode:
                if original_mode == 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                elif original_mode == 'POSE':
                    bpy.ops.object.mode_set(mode='POSE')
                elif original_mode == 'EDIT':
                    bpy.ops.object.mode_set(mode='EDIT')
            
            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selected:
                if obj:  # Check if object still exists
                    obj.select_set(True)
            if original_active:
                bpy.context.view_layer.objects.active = original_active
        except:
            pass

def transforms_different(transform1, transform2, tolerance=0.01, length_tolerance=0.001):
    """Check if two edit bone transforms are structurally different (relative matrix OR bone length)
    SMART inherit_scale filtering: Only consider inherit_scale changes for bones with physical changes
    """
    
    # 1. Compare relative matrices for positional/rotational changes
    matrix1 = transform1['relative_matrix']
    matrix2 = transform2['relative_matrix']
    
    max_matrix_difference = 0.0
    matrix_changed = False
    for i in range(4):
        for j in range(4):
            diff = abs(matrix1[i][j] - matrix2[i][j])
            max_matrix_difference = max(max_matrix_difference, diff)
            if diff > tolerance:
                matrix_changed = True
                break
        if matrix_changed:
            break
    
    # 2. Compare bone lengths for scaling changes
    length1 = transform1.get('bone_length', 0.0)
    length2 = transform2.get('bone_length', 0.0)
    length_difference = abs(length1 - length2)
    length_changed = length_difference > length_tolerance
    
    # 3. Check if bone has ANY physical changes
    has_physical_changes = matrix_changed or length_changed
    
    if has_physical_changes:
        parent_name = transform1.get('parent_name', 'ROOT')
        if matrix_changed:
            print(f"DEBUG: Matrix difference detected: {max_matrix_difference:.6f} > {tolerance} (parent: {parent_name})")
        if length_changed:
            print(f"DEBUG: Length difference detected: {length1:.6f} → {length2:.6f} (diff: {length_difference:.6f}) (parent: {parent_name})")
        return True
    
    # 4. SMART inherit_scale check: Only consider inherit_scale changes for bones with physical changes
    # If bone has no physical changes, ignore inherit_scale differences (prevents 355 bone export)
    inherit_scale_changed = transform1['inherit_scale'] != transform2['inherit_scale']
    if inherit_scale_changed and has_physical_changes:
        parent_name = transform1.get('parent_name', 'ROOT')
        print(f"DEBUG: inherit_scale difference WITH physical changes: {transform1['inherit_scale']} → {transform2['inherit_scale']} (parent: {parent_name})")
        return True
    elif inherit_scale_changed and not has_physical_changes:
        parent_name = transform1.get('parent_name', 'ROOT')
        print(f"DEBUG: Ignoring inherit_scale change WITHOUT physical changes for '{parent_name}' child")
        return False
    
    # Debug output for close calls
    if max_matrix_difference > tolerance * 0.1 or length_difference > length_tolerance * 0.1:
        parent_name = transform1.get('parent_name', 'ROOT')
        print(f"DEBUG: Close call - Matrix diff: {max_matrix_difference:.6f}, Length diff: {length_difference:.6f} (parent: {parent_name})")
        
    return False

def is_child_transform_inherited_only(bone_name, original_transforms, modified_transforms):
    """
    DISABLED: Complex inheritance filtering function that was causing child bone issues
    
    This function was over-engineered and fought against Blender's actual Edit Mode behavior.
    In Edit Mode, child bones are independent and don't inherit parent transforms.
    The complex logic here was incorrectly filtering out legitimate bone changes.
    
    SIMPLIFIED APPROACH: The new diff export system processes all bones with actual differences,
    letting Blender handle bone relationships naturally during preset application.
    
    This function is kept for reference but should not be used.
    
    Original description:
    Check if a child bone's transformation is purely the result of ancestor transformations
    Returns True if child should be excluded from diff export (no independent changes)
    FIXED: Added critical bone protection, scaling vs positional inheritance distinction, and better tolerances
    """
    # DISABLED: Always return False to never filter any bones
    print(f"DEBUG: is_child_transform_inherited_only() called for '{bone_name}' - DISABLED, returning False")
    return False
    if bone_name not in original_transforms or bone_name not in modified_transforms:
        return False
    
    original_transform = original_transforms[bone_name]
    modified_transform = modified_transforms[bone_name]
    
    # CRITICAL BONE PROTECTION: Never filter major structural bones
    CRITICAL_BONES = {
        'Hips', 'Hip', 'Pelvis',  # Hip bones
        'Left leg', 'Right leg', 'LeftLeg', 'RightLeg', 'L_leg', 'R_leg',  # Leg bones
        'Left knee', 'Right knee', 'LeftKnee', 'RightKnee', 'L_knee', 'R_knee',  # Knee bones
        'Left ankle', 'Right ankle', 'LeftAnkle', 'RightAnkle', 'L_ankle', 'R_ankle',  # Ankle bones
        'Left thigh', 'Right thigh', 'LeftThigh', 'RightThigh', 'L_thigh', 'R_thigh',  # Thigh bones
        'Left shin', 'Right shin', 'LeftShin', 'RightShin', 'L_shin', 'R_shin',  # Shin bones
        'Head', 'Neck', 'Spine', 'Chest', 'Torso',  # Core structural bones
        'Left arm', 'Right arm', 'LeftArm', 'RightArm', 'L_arm', 'R_arm',  # Arm bones
        'Left shoulder', 'Right shoulder', 'LeftShoulder', 'RightShoulder', 'L_shoulder', 'R_shoulder'  # Shoulder bones
    }
    
    # CRITICAL: Also check bone name contains these keywords (case-insensitive)
    CRITICAL_KEYWORDS = ['leg', 'knee', 'ankle', 'thigh', 'shin', 'hip', 'spine', 'head', 'neck', 'arm', 'shoulder']
    
    # SUPER CRITICAL: Bones that should NEVER EVER be filtered, regardless of any other logic
    NEVER_FILTER_BONES = {
        'Left leg', 'Right leg', 'Left knee', 'Right knee', 'Left ankle', 'Right ankle',
        'Hips', 'Head', 'Neck', 'Chest', 'Spine', 'Left arm', 'Right arm', 'Left shoulder', 'Right shoulder'
    }
    
    # ABSOLUTE PROTECTION: Check super critical bones first (highest priority)
    print(f"DEBUG INHERITANCE: Checking NEVER_FILTER_BONES for '{bone_name}'")
    print(f"  - NEVER_FILTER_BONES contains: {NEVER_FILTER_BONES}")
    print(f"  - bone_name in NEVER_FILTER_BONES: {bone_name in NEVER_FILTER_BONES}")
    
    if bone_name in NEVER_FILTER_BONES:
        print(f"DEBUG: Bone '{bone_name}' is NEVER_FILTER bone - ABSOLUTELY NEVER filtering")
        return False
    
    # Check for exact matches and partial matches (case-insensitive)
    bone_name_lower = bone_name.lower()
    for critical_bone in CRITICAL_BONES:
        if bone_name == critical_bone or critical_bone.lower() in bone_name_lower:
            print(f"DEBUG: Bone '{bone_name}' is protected as critical structural bone (exact match) - NEVER filtering")
            return False
    
    # Check for keyword matches
    for keyword in CRITICAL_KEYWORDS:
        if keyword in bone_name_lower:
            print(f"DEBUG: Bone '{bone_name}' is protected as critical structural bone (keyword '{keyword}') - NEVER filtering")
            return False
    
    # Debug output for bone name matching
    print(f"DEBUG: Bone '{bone_name}' passed critical bone protection checks...")
    
    # BONE LENGTH/SCALING PROTECTION: Never filter bones with significant length changes
    original_length = original_transform.get('bone_length', 0.0)
    modified_length = modified_transform.get('bone_length', 0.0)
    length_difference = abs(original_length - modified_length)
    
    print(f"DEBUG: Bone '{bone_name}' length check: {original_length:.6f} -> {modified_length:.6f} (diff: {length_difference:.6f})")
    
    if length_difference > 0.001:  # Significant length change
        length_ratio = modified_length / original_length if original_length > 0 else 1.0
        print(f"DEBUG: Bone '{bone_name}' has significant length change: {original_length:.6f} -> {modified_length:.6f} (ratio: {length_ratio:.6f}) - NEVER filtering scaling changes")
        return False
    
    # CRITICAL: Additional check using transforms_different for bone length detection
    if transforms_different(original_transform, modified_transform, tolerance=0.01, length_tolerance=0.001):
        # Check if this difference is primarily due to bone length change
        if length_difference > 0.0001:  # Even smaller length changes should be protected
            print(f"DEBUG: Bone '{bone_name}' detected as having bone length difference via transforms_different - NEVER filtering")
            return False
    
    # ADDITIONAL PROTECTION: If this bone has ANY significant transform difference, and it's a major bone type, never filter
    major_bone_indicators = ['leg', 'knee', 'ankle', 'arm', 'elbow', 'wrist', 'hip', 'spine', 'neck', 'head']
    if any(indicator in bone_name_lower for indicator in major_bone_indicators):
        # For major bones, be extra cautious about filtering
        rel_matrix_1 = original_transform['relative_matrix']
        rel_matrix_2 = modified_transform['relative_matrix']
        
        # Check for any matrix differences at all
        matrix_diff = 0.0
        for i in range(4):
            for j in range(4):
                matrix_diff = max(matrix_diff, abs(rel_matrix_1[i][j] - rel_matrix_2[i][j]))
        
        if matrix_diff > 0.001:  # Any significant matrix change
            print(f"DEBUG: Major bone '{bone_name}' has matrix difference {matrix_diff:.6f} - NEVER filtering major bones with changes")
            return False
    
    # Check if bone has a parent
    parent_name = original_transform.get('parent_name')
    if not parent_name:
        return False  # Root bones can't have inherited-only changes
    
    # Build ancestor chain that have changes
    def get_ancestors_with_changes(bone_name, orig_transforms, mod_transforms):
        """Get list of ancestors that have significant changes"""
        ancestors_with_changes = []
        current = bone_name
        
        while current:
            if current in orig_transforms and current in mod_transforms:
                orig = orig_transforms[current]
                mod = mod_transforms[current]
                
                # Check if this ancestor has changes
                if transforms_different(orig, mod, tolerance=0.01):
                    ancestors_with_changes.append(current)
                
                # Move to parent
                current = orig.get('parent_name')
            else:
                break
        
        return ancestors_with_changes
    
    # Get ancestors with changes (excluding the bone itself)
    parent_name = original_transform.get('parent_name')
    if not parent_name:
        return False
        
    ancestors_with_changes = get_ancestors_with_changes(parent_name, original_transforms, modified_transforms)
    
    if not ancestors_with_changes:
        return False  # No ancestors with changes, so child changes must be independent
    
    # INHERITANCE TYPE DETECTION: Distinguish scaling vs positional inheritance
    # Check if ancestors have primarily scaling changes vs positional changes
    ancestor_has_scaling = False
    ancestor_has_positional = False
    
    for ancestor_name in ancestors_with_changes:
        if ancestor_name in original_transforms and ancestor_name in modified_transforms:
            orig_ancestor = original_transforms[ancestor_name]
            mod_ancestor = modified_transforms[ancestor_name]
            
            # Check for length changes in ancestor (scaling)
            orig_ancestor_length = orig_ancestor.get('bone_length', 0.0)
            mod_ancestor_length = mod_ancestor.get('bone_length', 0.0)
            if abs(orig_ancestor_length - mod_ancestor_length) > 0.001:
                ancestor_has_scaling = True
            
            # Check for matrix changes in ancestor (positional/rotational)
            matrix1 = orig_ancestor['relative_matrix']
            matrix2 = mod_ancestor['relative_matrix']
            for i in range(4):
                for j in range(4):
                    if abs(matrix1[i][j] - matrix2[i][j]) > 0.01:
                        ancestor_has_positional = True
                        break
                if ancestor_has_positional:
                    break
    
    # INHERITANCE FILTERING LOGIC:
    # - If ancestor has scaling changes -> child scaling is NOT inherited (independent)
    # - Only filter true positional inheritance (ancestor position -> child position)
    if ancestor_has_scaling:
        print(f"DEBUG: Ancestor has scaling changes - child '{bone_name}' changes are independent, not inherited - NEVER filtering")
        return False
    
    # ADDITIONAL SAFETY CHECK: If this bone itself has any scaling indicators, never filter
    # Check relative matrix scaling components
    rel_matrix = modified_transform['relative_matrix']
    matrix_scale = rel_matrix.to_scale()
    if any(abs(scale - 1.0) > 0.01 for scale in [matrix_scale.x, matrix_scale.y, matrix_scale.z]):
        print(f"DEBUG: Bone '{bone_name}' has relative matrix scaling {matrix_scale} - NEVER filtering scaling changes")
        return False
    
    # Calculate cumulative transformation effect from all ancestor changes
    # Start with the child's relative matrix (unchanged)
    child_relative = original_transform['relative_matrix']
    
    # Calculate what the child's absolute matrix should be if only ancestors changed
    # Walk up the chain and apply ancestor transformations
    def calculate_expected_absolute_matrix(bone_name, orig_transforms, mod_transforms):
        """Calculate expected absolute matrix if only ancestors changed"""
        
        # Get the parent chain
        chain = []
        current = bone_name
        while current:
            if current in orig_transforms:
                chain.append(current)
                current = orig_transforms[current].get('parent_name')
            else:
                break
        
        # Start from root and multiply down
        if len(chain) <= 1:
            return orig_transforms[bone_name]['absolute_matrix']  # No parents
        
        # Calculate absolute matrix by walking down from highest ancestor
        absolute_matrix = None
        for i in reversed(range(len(chain))):
            bone = chain[i]
            relative_matrix = orig_transforms[bone]['relative_matrix']
            
            if i == len(chain) - 1:  # Root bone
                # Use modified absolute matrix for changed bones, original for unchanged
                if bone in mod_transforms and transforms_different(orig_transforms[bone], mod_transforms[bone]):
                    absolute_matrix = mod_transforms[bone]['absolute_matrix']
                else:
                    absolute_matrix = orig_transforms[bone]['absolute_matrix']
            else:
                # Child bone - multiply parent absolute * child relative
                if bone in mod_transforms and transforms_different(orig_transforms[bone], mod_transforms[bone]):
                    # This bone has independent changes - use modified relative matrix
                    absolute_matrix = absolute_matrix @ mod_transforms[bone]['relative_matrix']
                else:
                    # This bone unchanged - use original relative matrix
                    absolute_matrix = absolute_matrix @ relative_matrix
        
        return absolute_matrix
    
    expected_child_abs = calculate_expected_absolute_matrix(bone_name, original_transforms, modified_transforms)
    actual_child_abs = modified_transform['absolute_matrix']
    
    # Compare expected vs actual child absolute matrices
    max_difference = 0.0
    for i in range(4):
        for j in range(4):
            diff = abs(expected_child_abs[i][j] - actual_child_abs[i][j])
            max_difference = max(max_difference, diff)
    
    # IMPROVED TOLERANCE: Use relative tolerance based on matrix magnitude to handle floating-point precision
    matrix_magnitude = 0.0
    for i in range(4):
        for j in range(4):
            matrix_magnitude = max(matrix_magnitude, abs(actual_child_abs[i][j]))
    
    # Use relative tolerance (0.1% of matrix magnitude) with minimum absolute tolerance
    relative_tolerance = max(0.001, matrix_magnitude * 0.001)
    
    # If child's actual position matches what we'd expect from ancestor transformations only,
    # then this child has no independent changes
    is_inherited_only = max_difference < relative_tolerance
    
    # FINAL SAFETY CHECK: For knee bones specifically, be extra careful
    if 'knee' in bone_name_lower:
        print(f"DEBUG: KNEE BONE SAFETY CHECK: '{bone_name}' - max_difference: {max_difference:.6f}, tolerance: {relative_tolerance:.6f}")
        # Use a more lenient tolerance for knee bones since they often have complex inheritance relationships
        if max_difference > 0.01:  # Much more lenient for knee bones
            print(f"DEBUG: KNEE BONE '{bone_name}' has significant difference {max_difference:.6f} > 0.01 - NEVER filtering knee bones")
            return False
    
    # ENHANCED DEBUG OUTPUT
    inheritance_type = "scaling" if ancestor_has_scaling else "positional"
    if is_inherited_only:
        print(f"DEBUG: Child bone '{bone_name}' transformation is purely inherited {inheritance_type} from ancestors {ancestors_with_changes}")
        print(f"       Matrix difference: {max_difference:.6f} < tolerance: {relative_tolerance:.6f} - EXCLUDING from diff export")
    else:
        print(f"DEBUG: Child bone '{bone_name}' has independent changes beyond {inheritance_type} ancestors {ancestors_with_changes}")
        print(f"       Matrix difference: {max_difference:.6f} >= tolerance: {relative_tolerance:.6f} - INCLUDING in diff export")
    
    return is_inherited_only

def calculate_head_tail_differences(original_transforms, modified_transforms):
    """
    Calculate differences between two armatures and convert to standard pose transform format
    This ensures compatibility with the standard preset loader
    SIMPLIFIED: No complex inheritance filtering - exports all bones with actual differences
    Returns: (diff_data, bones_with_differences)
    """
    # Import the conversion function from transforms module
    try:
        from .transforms_diff import convert_head_tail_to_pose_transforms_filtered
        TRANSFORMS_AVAILABLE = True
    except ImportError:
        print("WARNING: transforms module not available, using fallback method")
        TRANSFORMS_AVAILABLE = False
    
    if TRANSFORMS_AVAILABLE:
        # Use the simplified conversion function to get standard pose format (updated parameter names)
        diff_data = convert_head_tail_to_pose_transforms_filtered(original_transforms, modified_transforms)
        bones_with_differences = len(diff_data)
        
        print(f"DEBUG: Converted {bones_with_differences} bones to standard pose transform format (simplified approach)")
        return diff_data, bones_with_differences
    else:
        # Fallback to simple legacy method if transforms module unavailable
        return calculate_head_tail_differences_legacy(original_transforms, modified_transforms)

def calculate_head_tail_differences_legacy(original_transforms, modified_transforms):
    """
    Legacy method: Calculate direct head/tail position differences between two armatures
    Returns: (diff_data, bones_with_differences)
    """
    diff_data = {}
    bones_with_differences = 0
    
    # First pass: identify bones with actual structural changes
    bones_with_structural_changes = {}
    
    # Compare edit bone matrices for each bone that exists in both armatures
    for bone_name in modified_transforms:
        if bone_name not in original_transforms:
            continue  # Skip bones that don't exist in original
        
        original_transform = original_transforms[bone_name]
        modified_transform = modified_transforms[bone_name]
        
        # Check if edit bone matrices are structurally different
        transform_changed = transforms_different(original_transform, modified_transform)
        
        if transform_changed:
            bones_with_structural_changes[bone_name] = {
                'original': original_transform,
                'modified': modified_transform
            }
    
    # Second pass: calculate direct head/tail differences for proper bone length changes
    for bone_name, transform_data in bones_with_structural_changes.items():
        original_transform = transform_data['original']
        modified_transform = transform_data['modified']
        
        # DIRECT HEAD/TAIL APPROACH: Store the actual head/tail position changes
        # This is more accurate than trying to convert to pose transforms
        
        orig_abs_matrix = original_transform['absolute_matrix']
        mod_abs_matrix = modified_transform['absolute_matrix']
        
        # Extract head and tail positions from absolute matrices
        orig_head = orig_abs_matrix.translation
        orig_tail = orig_abs_matrix @ Vector((0, orig_abs_matrix.to_scale().y, 0, 1))
        orig_tail = orig_tail.xyz  # Convert to 3D vector
        
        mod_head = mod_abs_matrix.translation  
        mod_tail = mod_abs_matrix @ Vector((0, mod_abs_matrix.to_scale().y, 0, 1))
        mod_tail = mod_tail.xyz  # Convert to 3D vector
        
        # Calculate head and tail differences
        head_diff = mod_head - orig_head
        tail_diff = mod_tail - orig_tail
        
        # Store as direct head/tail modifications instead of pose transforms
        diff_data[bone_name] = {
            'method': 'head_tail_direct',
            'head_difference': [head_diff.x, head_diff.y, head_diff.z],
            'tail_difference': [tail_diff.x, tail_diff.y, tail_diff.z],
            'inherit_scale': modified_transform['inherit_scale'],
            'original_length': (orig_tail - orig_head).length,
            'modified_length': (mod_tail - mod_head).length
        }
        bones_with_differences += 1
        
        parent_name = original_transform.get('parent_name', 'ROOT')
        print(f"DEBUG: Found HEAD/TAIL difference in bone '{bone_name}' (parent: {parent_name})")
        print(f"  Head diff: [{head_diff.x:.6f}, {head_diff.y:.6f}, {head_diff.z:.6f}]")
        print(f"  Tail diff: [{tail_diff.x:.6f}, {tail_diff.y:.6f}, {tail_diff.z:.6f}]")
        print(f"  Length: {(orig_tail - orig_head).length:.6f} → {(mod_tail - mod_head).length:.6f}")
        
        # FALLBACK: If head/tail approach fails, use pose transforms
        if (head_diff.length < 0.0001 and tail_diff.length < 0.0001):
            print(f"DEBUG: Head/tail differences too small, skipping '{bone_name}' (no meaningful change)")
            # Remove from diff_data if changes are negligible
            del diff_data[bone_name]
            bones_with_differences -= 1
    
    return diff_data, bones_with_differences

def calculate_head_tail_differences_legacy_filtered(original_transforms, modified_transforms):
    """
    Legacy method with inheritance filtering: Calculate direct head/tail position differences between two armatures
    FIXED: Now filters out child bones that only inherit parent transformations
    Returns: (diff_data, bones_with_differences)
    """
    diff_data = {}
    bones_with_differences = 0
    
    # First pass: identify bones with actual structural changes
    bones_with_structural_changes = {}
    
    # Compare edit bone matrices for each bone that exists in both armatures
    for bone_name in modified_transforms:
        if bone_name not in original_transforms:
            continue  # Skip bones that don't exist in original
        
        original_transform = original_transforms[bone_name]
        modified_transform = modified_transforms[bone_name]
        
        # Check if edit bone matrices are structurally different
        transform_changed = transforms_different(original_transform, modified_transform)
        
        if transform_changed:
            # INHERITANCE FILTER: Check if this change is purely inherited from parent
            if is_child_transform_inherited_only(bone_name, original_transforms, modified_transforms):
                print(f"DEBUG: Skipping bone '{bone_name}' - changes are purely inherited from parent")
                continue  # Skip this bone - it's only inheriting parent's transformation
            
            bones_with_structural_changes[bone_name] = {
                'original': original_transform,
                'modified': modified_transform
            }
    
    # Second pass: calculate direct head/tail differences for bones with independent changes
    for bone_name, transform_data in bones_with_structural_changes.items():
        original_transform = transform_data['original']
        modified_transform = transform_data['modified']
        
        # DIRECT HEAD/TAIL APPROACH: Store the actual head/tail position changes
        # This is more accurate than trying to convert to pose transforms
        
        orig_abs_matrix = original_transform['absolute_matrix']
        mod_abs_matrix = modified_transform['absolute_matrix']
        
        # Extract head and tail positions from absolute matrices
        orig_head = orig_abs_matrix.translation
        orig_tail = orig_abs_matrix @ Vector((0, orig_abs_matrix.to_scale().y, 0, 1))
        orig_tail = orig_tail.xyz  # Convert to 3D vector
        
        mod_head = mod_abs_matrix.translation  
        mod_tail = mod_abs_matrix @ Vector((0, mod_abs_matrix.to_scale().y, 0, 1))
        mod_tail = mod_tail.xyz  # Convert to 3D vector
        
        # Calculate head and tail differences
        head_diff = mod_head - orig_head
        tail_diff = mod_tail - orig_tail
        
        # Store as direct head/tail modifications instead of pose transforms
        diff_data[bone_name] = {
            'method': 'head_tail_direct',
            'head_difference': [head_diff.x, head_diff.y, head_diff.z],
            'tail_difference': [tail_diff.x, tail_diff.y, tail_diff.z],
            'inherit_scale': modified_transform['inherit_scale'],
            'original_length': (orig_tail - orig_head).length,
            'modified_length': (mod_tail - mod_head).length
        }
        bones_with_differences += 1
        
        parent_name = original_transform.get('parent_name', 'ROOT')
        print(f"DEBUG: Found INDEPENDENT HEAD/TAIL difference in bone '{bone_name}' (parent: {parent_name})")
        print(f"  Head diff: [{head_diff.x:.6f}, {head_diff.y:.6f}, {head_diff.z:.6f}]")
        print(f"  Tail diff: [{tail_diff.x:.6f}, {tail_diff.y:.6f}, {tail_diff.z:.6f}]")
        print(f"  Length: {(orig_tail - orig_head).length:.6f} → {(mod_tail - mod_head).length:.6f}")
        
        # FALLBACK: If head/tail approach fails, use pose transforms
        if (head_diff.length < 0.0001 and tail_diff.length < 0.0001):
            print(f"DEBUG: Head/tail differences too small, skipping '{bone_name}' (no meaningful change)")
            # Remove from diff_data if changes are negligible
            del diff_data[bone_name]
            bones_with_differences -= 1
    
    print(f"DEBUG: Legacy filtered method exported {bones_with_differences} bones with independent changes")
    return diff_data, bones_with_differences