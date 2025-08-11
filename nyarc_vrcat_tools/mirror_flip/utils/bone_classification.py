# Bone Classification Utility
# Uses existing VRChat compatibility mappings to classify bones

from ...bone_transforms.compatibility.vrchat_bones import VRCHAT_STANDARD_BONES


def _is_meaningful_substring_match(bone_lower, standard_lower):
    """Check if substring match is meaningful and not a false positive"""
    # Avoid false positives for very short standard names
    if len(standard_lower) < 4:
        # For short names like "hip", "leg", require exact match or word boundary
        return (bone_lower == standard_lower or 
                f" {standard_lower} " in f" {bone_lower} " or
                bone_lower.startswith(f"{standard_lower} ") or
                bone_lower.endswith(f" {standard_lower}"))
    
    # For longer names, allow standard substring matching but with safeguards
    if standard_lower in bone_lower:
        # Avoid false positives where the standard name is part of a longer word
        # e.g., "root" shouldn't match "HairPin_Root" 
        start_idx = bone_lower.find(standard_lower)
        
        # Check if it's a whole word or separated by common delimiters
        before_char = bone_lower[start_idx - 1] if start_idx > 0 else ' '
        after_char = bone_lower[start_idx + len(standard_lower)] if start_idx + len(standard_lower) < len(bone_lower) else ' '
        
        # Allow match if preceded/followed by space, underscore, dot, or string boundary
        delimiters = [' ', '_', '.', '-']
        if before_char in delimiters or after_char in delimiters:
            return True
            
        # Special case: if the standard name is at the very beginning or end
        if start_idx == 0 or start_idx + len(standard_lower) == len(bone_lower):
            return True
            
        # Avoid false positive for embedded words
        return False
    
    # Check reverse (bone name in standard name) - usually safe
    if bone_lower in standard_lower:
        return True
        
    return False


def is_vrchat_base_bone(bone_name):
    """Check if bone name matches any VRChat standard bone"""
    if not bone_name:
        return False
    
    bone_lower = bone_name.lower()
    # Normalize bone name: remove spaces, underscores, dots for better matching
    bone_normalized = bone_lower.replace(' ', '').replace('_', '').replace('.', '')
    
    # Check against all VRChat standard bone categories
    for category, standard_names in VRCHAT_STANDARD_BONES.items():
        for standard_name in standard_names:
            standard_lower = standard_name.lower()
            standard_normalized = standard_lower.replace(' ', '').replace('_', '').replace('.', '')
            
            # Check for exact match
            if bone_lower == standard_lower:
                print(f"BONE_CLASSIFICATION: '{bone_name}' is VRChat base bone (exact match: {standard_name})")
                return True
            
            # Check for normalized match (e.g., "Right knee" → "rightknee" matches "rightknee")
            if bone_normalized == standard_normalized:
                print(f"BONE_CLASSIFICATION: '{bone_name}' is VRChat base bone (normalized match: {standard_name})")
                return True
            
            # Check for meaningful substring matches (avoid false positives)
            if _is_meaningful_substring_match(bone_lower, standard_lower):
                print(f"BONE_CLASSIFICATION: '{bone_name}' is VRChat base bone (substring match: {standard_name})")
                return True
    
    print(f"BONE_CLASSIFICATION: '{bone_name}' is custom/accessory bone")
    return False


def classify_bone_chain(bone_chain, axis='X'):
    """Classify a bone chain as accessory, vrchat_reparent, or base_armature attachment (axis-aware)"""
    if not bone_chain or not bone_chain.bones:
        return "unknown"
    
    root_bone = bone_chain.root
    
    # NEW LOGIC: Check if root bone is a VRChat base bone with an available opposite (axis-aware)
    if is_vrchat_base_bone(root_bone):
        root_opposite = get_vrchat_opposite_bone_axis_aware(root_bone, axis)
        if root_opposite:
            # This is a VRChat base bone that should be reparented to its opposite
            bone_chain.chain_type = "vrchat_reparent"
            print(f"BONE_CLASSIFICATION: Chain '{root_bone}' classified as VRCHAT_REPARENT (target: '{root_opposite}')")
            return "vrchat_reparent"
        else:
            # VRChat base bone but no opposite (e.g., core bones like spine)
            bone_chain.chain_type = "base_armature"
            print(f"BONE_CLASSIFICATION: Chain '{root_bone}' classified as BASE_ARMATURE (VRChat base, no opposite)")
            return "base_armature"
    else:
        # Not a VRChat base bone - regular accessory
        bone_chain.chain_type = "accessory"
        print(f"BONE_CLASSIFICATION: Chain '{root_bone}' classified as ACCESSORY")
        return "accessory"


def get_vrchat_opposite_bone(bone_name):
    """Get opposite VRChat bone using the existing mappings"""
    if not bone_name:
        return None
    
    bone_lower = bone_name.lower()
    bone_normalized = bone_lower.replace(' ', '').replace('_', '').replace('.', '')
    
    print(f"🔍 GET_OPPOSITE: Looking for opposite of '{bone_name}' (normalized: '{bone_normalized}')")
    
    # Check each category for matches
    for category, standard_names in VRCHAT_STANDARD_BONES.items():
        for standard_name in standard_names:
            standard_lower = standard_name.lower()
            standard_normalized = standard_lower.replace(' ', '').replace('_', '').replace('.', '')
            
            # Check for exact, normalized, or substring match
            if (bone_lower == standard_lower or 
                bone_normalized == standard_normalized or 
                standard_lower in bone_lower):
                print(f"🔍 GET_OPPOSITE: Found match '{standard_name}' in category '{category}'")
                # Found a match, now find its opposite
                opposite = _find_opposite_in_category(bone_name, category, standard_name)
                print(f"🔍 GET_OPPOSITE: Result for '{bone_name}' → '{opposite}'")
                return opposite
    
    print(f"🔍 GET_OPPOSITE: No match found for '{bone_name}'")
    return None


def _find_opposite_in_category(bone_name, category, matched_standard):
    """Find opposite bone within the same category"""
    print(f"🔍 FIND_OPPOSITE_CAT: Category '{category}', matched '{matched_standard}'")
    
    # Map categories to their opposites
    opposite_categories = {
        'arms_left': 'arms_right',
        'arms_right': 'arms_left', 
        'legs_left': 'legs_right',
        'legs_right': 'legs_left',
        'fingers_left': 'fingers_right',
        'fingers_right': 'fingers_left',
        
        # LEG CATEGORY MAPPINGS (FIXED - was missing!)
        'upper_leg_left': 'upper_leg_right',
        'upper_leg_right': 'upper_leg_left',
        'lower_leg_left': 'lower_leg_right', 
        'lower_leg_right': 'lower_leg_left',
        'foot_left': 'foot_right',
        'foot_right': 'foot_left',
        'toe_left': 'toe_right',
        'toe_right': 'toe_left',
        
        # SHOULDER/ARM CATEGORY MAPPINGS
        'shoulder_left': 'shoulder_right',
        'shoulder_right': 'shoulder_left',
        'upper_arm_left': 'upper_arm_right',
        'upper_arm_right': 'upper_arm_left',
        'forearm_left': 'forearm_right',
        'forearm_right': 'forearm_left',
        'hand_left': 'hand_right',
        'hand_right': 'hand_left',
        
        # Detailed toe bone opposites
        'toe_little_proximal_left': 'toe_little_proximal_right',
        'toe_little_proximal_right': 'toe_little_proximal_left',
        'toe_little_intermediate_left': 'toe_little_intermediate_right',
        'toe_little_intermediate_right': 'toe_little_intermediate_left',
        'toe_little_distal_left': 'toe_little_distal_right',
        'toe_little_distal_right': 'toe_little_distal_left',
        
        'toe_ring_proximal_left': 'toe_ring_proximal_right',
        'toe_ring_proximal_right': 'toe_ring_proximal_left',
        'toe_ring_intermediate_left': 'toe_ring_intermediate_right',
        'toe_ring_intermediate_right': 'toe_ring_intermediate_left',
        'toe_ring_distal_left': 'toe_ring_distal_right',
        'toe_ring_distal_right': 'toe_ring_distal_left',
        
        'toe_middle_proximal_left': 'toe_middle_proximal_right',
        'toe_middle_proximal_right': 'toe_middle_proximal_left',
        'toe_middle_intermediate_left': 'toe_middle_intermediate_right',
        'toe_middle_intermediate_right': 'toe_middle_intermediate_left',
        'toe_middle_distal_left': 'toe_middle_distal_right',
        'toe_middle_distal_right': 'toe_middle_distal_left',
        
        'toe_index_proximal_left': 'toe_index_proximal_right',
        'toe_index_proximal_right': 'toe_index_proximal_left',
        'toe_index_intermediate_left': 'toe_index_intermediate_right',
        'toe_index_intermediate_right': 'toe_index_intermediate_left',
        'toe_index_distal_left': 'toe_index_distal_right',
        'toe_index_distal_right': 'toe_index_distal_left',
        
        'toe_thumb_proximal_left': 'toe_thumb_proximal_right',
        'toe_thumb_proximal_right': 'toe_thumb_proximal_left',
        'toe_thumb_intermediate_left': 'toe_thumb_intermediate_right',
        'toe_thumb_intermediate_right': 'toe_thumb_intermediate_left',
        'toe_thumb_distal_left': 'toe_thumb_distal_right',
        'toe_thumb_distal_right': 'toe_thumb_distal_left'
    }
    
    if category not in opposite_categories:
        # Core bones like spine, neck don't have opposites
        print(f"🔍 FIND_OPPOSITE_CAT: Category '{category}' has no opposite (core bone)")
        return None
    
    opposite_category = opposite_categories[category]
    opposite_bones = VRCHAT_STANDARD_BONES[opposite_category]
    print(f"🔍 FIND_OPPOSITE_CAT: Looking in opposite category '{opposite_category}' with {len(opposite_bones)} bones")
    
    # Find the corresponding bone in opposite category
    # Simple heuristic: find bone with similar naming pattern
    matched_lower = matched_standard.lower()
    
    for opp_bone in opposite_bones:
        opp_lower = opp_bone.lower()
        
        # Replace left/right indicators
        base_pattern = matched_lower.replace('_l', '').replace('.l', '').replace('left', '').replace('right', '')
        opp_pattern = opp_lower.replace('_r', '').replace('.r', '').replace('right', '').replace('left', '')
        
        print(f"🔍 FIND_OPPOSITE_CAT: Comparing '{matched_standard}' (base: '{base_pattern}') vs '{opp_bone}' (base: '{opp_pattern}')")
        
        if base_pattern == opp_pattern:
            # Found matching opposite, now map the original bone name format
            opposite_name = _map_bone_name_format(bone_name, matched_standard, opp_bone)
            print(f"🔍 FIND_OPPOSITE_CAT: MATCH! '{bone_name}' opposite is '{opposite_name}'")
            return opposite_name
    
    print(f"🔍 FIND_OPPOSITE_CAT: No matching opposite found in category '{opposite_category}'")
    return None


def _map_bone_name_format(original_name, matched_standard, opposite_standard):
    """Map the original bone name format to the opposite"""
    # If original matches the standard exactly, return opposite standard
    if original_name.lower() == matched_standard.lower():
        return opposite_standard
    
    # Try to preserve the original naming convention
    original_lower = original_name.lower()
    matched_lower = matched_standard.lower()
    
    # Handle common cases with better space/capitalization preservation
    if 'right' in original_lower and 'left' in opposite_standard.lower():
        # Handle "Right knee" → "Left knee" (preserve capitalization and spaces)
        result = original_name.replace('Right', 'Left').replace('right', 'left')
        print(f"BONE_CLASSIFICATION: Mapped '{original_name}' → '{result}' (right→left)")
        return result
    elif 'left' in original_lower and 'right' in opposite_standard.lower():
        # Handle "Left knee" → "Right knee" 
        result = original_name.replace('Left', 'Right').replace('left', 'right')
        print(f"BONE_CLASSIFICATION: Mapped '{original_name}' → '{result}' (left→right)")
        return result
    elif '.r' in original_lower and '.l' in opposite_standard.lower():
        return original_name.replace('.r', '.l').replace('.R', '.L')
    elif '.l' in original_lower and '.r' in opposite_standard.lower():
        return original_name.replace('.l', '.r').replace('.L', '.R')
    
    # NEW: Try intelligent mapping for space-separated names
    # Example: "Right knee" should map to "Left knee" not "leftknee"
    if ' ' in original_name:
        words = original_name.split()
        for i, word in enumerate(words):
            word_lower = word.lower()
            if word_lower == 'right':
                words[i] = 'Left'
            elif word_lower == 'left':
                words[i] = 'Right'
        result = ' '.join(words)
        if result != original_name:
            print(f"BONE_CLASSIFICATION: Space-mapped '{original_name}' → '{result}'")
            return result
    
    # Fallback: use the opposite standard name
    print(f"BONE_CLASSIFICATION: Fallback mapping '{original_name}' → '{opposite_standard}'")
    return opposite_standard


def should_filter_base_bone(bone_name, mesh_vertex_groups):
    """Check if base armature bone should be filtered out (not in mesh vertex groups)"""
    if not is_vrchat_base_bone(bone_name):
        return False  # Not a base bone, don't filter
    
    vertex_group_names = {vg.name for vg in mesh_vertex_groups}
    is_in_mesh = bone_name in vertex_group_names
    
    if not is_in_mesh:
        print(f"BONE_CLASSIFICATION: Filtering out base bone '{bone_name}' - not in mesh vertex groups")
        return True
    
    return False


def get_vrchat_opposite_bone_axis_aware(bone_name, axis='X'):
    """Get VRChat opposite bone only for X-axis mirroring. For Y/Z, return None (no reparenting)."""
    if axis != 'X':
        # For Y and Z axis mirroring, don't reparent to opposite bones
        print(f"🔍 AXIS_AWARE: Axis '{axis}' - no opposite reparenting for '{bone_name}'")
        return None
    
    # For X-axis, use normal opposite logic
    return get_vrchat_opposite_bone(bone_name)


def is_core_bone(bone_name):
    """Check if a bone is a VRChat core bone (hips, spine, chest, neck, head)"""
    if not bone_name:
        return False
    
    # Use existing bone classification logic to check if it's in the 'core' category
    from ...bone_transforms.compatibility.vrchat_bones import VRCHAT_STANDARD_BONES
    
    bone_lower = bone_name.lower()
    bone_normalized = bone_lower.replace(' ', '').replace('_', '').replace('.', '')
    
    # Check core category
    core_bones = VRCHAT_STANDARD_BONES.get('core', [])
    for core_bone in core_bones:
        core_lower = core_bone.lower()
        core_normalized = core_lower.replace(' ', '').replace('_', '').replace('.', '')
        
        # Exact match or meaningful substring match
        if (bone_normalized == core_normalized or 
            _is_meaningful_substring_match(bone_lower, core_lower)):
            print(f"BONE_CLASSIFICATION: '{bone_name}' is core bone (matched: '{core_bone}')")
            return True
    
    return False