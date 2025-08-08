# Bone Name Mapper Module
# Handles intelligent bone name mapping between different VRChat naming schemes
# Uses exact matching first, then semantic mapping for base bones only

import re
from typing import Dict, List, Tuple, Optional, Set
from ..compatibility.vrchat_bones import VRCHAT_STANDARD_BONES

# Now using VRCHAT_STANDARD_BONES from compatibility module for comprehensive bone name matching

def get_base_bone_names() -> Set[str]:
    """Get all possible base bone names from VRChat standard bones"""
    base_names = set()
    for bone_list in VRCHAT_STANDARD_BONES.values():
        base_names.update(bone_list)
    return base_names

def normalize_bone_name(bone_name: str) -> str:
    """Normalize bone name for comparison (lowercase, strip spaces)"""
    return bone_name.lower().strip().replace(' ', '_')

def find_semantic_category(bone_name: str) -> Optional[str]:
    """Find which semantic category a bone belongs to using VRChat standard bones (case-insensitive)"""
    normalized = normalize_bone_name(bone_name)
    # Only debug relevant bones (avoid spam for hair/clothing bones)
    base_keywords = ['leg', 'arm', 'shoulder', 'hip', 'spine', 'chest', 'neck', 'head', 'hand', 'foot', 'toe', 'thigh', 'shin', 'elbow', 'wrist', 'ankle', 'butt', 'glute']
    is_likely_base = any(keyword in normalized for keyword in base_keywords)
    
    if is_likely_base:
        print(f"DEBUG: Finding category for '{bone_name}' (normalized: '{normalized}')")
    
    # FIRST PASS: Check for exact matches across ALL VRChat standard bone categories (case-insensitive)
    for category, standard_names in VRCHAT_STANDARD_BONES.items():
        for standard_name in standard_names:
            standard_normalized = normalize_bone_name(standard_name)
            
            # Exact match - highest priority (case-insensitive)
            if normalized == standard_normalized:
                print(f"DEBUG: EXACT match '{bone_name}' -> category '{category}' (via '{standard_name}')")
                return category
    
    # SECOND PASS: Check for contains matches, but prioritize by specificity
    # Collect all potential matches with their specificity scores
    potential_matches = []
    
    for category, standard_names in VRCHAT_STANDARD_BONES.items():
        for standard_name in standard_names:
            standard_normalized = normalize_bone_name(standard_name)
            
            # Contains match (more restrictive now) - case-insensitive
            if len(normalized) > 3 and len(standard_normalized) > 3:  # Avoid short false matches
                if (normalized in standard_normalized or standard_normalized in normalized):
                    # CRITICAL: Ensure left/right consistency
                    bone_is_left = any(indicator in normalized for indicator in ['_l', '.l', 'left'])
                    bone_is_right = any(indicator in normalized for indicator in ['_r', '.r', 'right'])
                    category_is_left = 'left' in category
                    category_is_right = 'right' in category
                    
                    # Only match if left/right sides match
                    if ((bone_is_left and category_is_left) or 
                        (bone_is_right and category_is_right) or 
                        (not bone_is_left and not bone_is_right and not category_is_left and not category_is_right)):
                        
                        # Calculate specificity score (longer matches = more specific)
                        # Also prioritize matches where the standard name contains more specific terms
                        specificity = len(standard_normalized)
                        
                        # Bonus for more specific terms
                        specific_terms = ['lower', 'upper', 'elbow', 'knee', 'ankle', 'wrist', 'forearm', 'shin', 'thigh']
                        for term in specific_terms:
                            if term in standard_normalized:
                                specificity += 10  # Big bonus for specific terms
                        
                        potential_matches.append((category, standard_name, specificity))
    
    # Return the most specific match
    if potential_matches:
        # Sort by specificity (highest first)
        potential_matches.sort(key=lambda x: x[2], reverse=True)
        best_category, best_standard, best_score = potential_matches[0]
        print(f"DEBUG: CONTAINS match '{bone_name}' -> category '{best_category}' (via '{best_standard}', specificity={best_score})")
        
        # Debug: show other potential matches that were rejected
        if len(potential_matches) > 1:
            other_matches = [(cat, std, score) for cat, std, score in potential_matches[1:]]
            print(f"DEBUG: Rejected less specific matches: {other_matches}")
        
        return best_category
    
    if is_likely_base:
        print(f"DEBUG: NO category found for '{bone_name}'")
    return None

def apply_exact_matching(preset_bones: Dict[str, dict], armature_bones: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """
    Apply exact bone name matching (current behavior)
    Returns: (matched_bones_dict, unmatched_preset_bones)
    """
    armature_bone_set = set(armature_bones)
    matched = {}
    unmatched = []
    
    for preset_bone in preset_bones.keys():
        if preset_bone in armature_bone_set:
            matched[preset_bone] = preset_bone  # preset_bone -> armature_bone
        else:
            unmatched.append(preset_bone)
    
    return matched, unmatched

def check_base_bone_coverage(matched_bones: Dict[str, str], armature_bones: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if all essential base bones were matched exactly
    Returns: (all_base_bones_covered, missing_base_categories)
    """
    print(f"DEBUG: Checking base bone coverage - {len(matched_bones)} exact matches found")
    
    # Quick optimization: if we have very few exact matches, assume we need semantic mapping
    if len(matched_bones) < 10:
        print(f"DEBUG: Few exact matches ({len(matched_bones)}), assuming semantic mapping needed")
        return False, ["needs_semantic_check"]
    
    print(f"DEBUG: Many exact matches ({len(matched_bones)}), likely same armature - skipping semantic mapping")
    return True, []

def apply_semantic_mapping(unmatched_preset_bones: List[str], armature_bones: List[str], missing_categories: List[str]) -> Dict[str, str]:
    """
    Apply semantic mapping for unmatched preset bones to missing base bone categories
    Returns: dict of preset_bone -> armature_bone mappings
    """
    semantic_matches = {}
    print(f"DEBUG: Starting semantic mapping for {len(unmatched_preset_bones)} unmatched preset bones...")
    
    # Pre-filter armature bones to likely base bones only (major performance optimization)
    base_keywords = ['leg', 'arm', 'shoulder', 'hip', 'spine', 'chest', 'neck', 'head', 'hand', 'foot', 'toe', 'thigh', 'shin', 'elbow', 'wrist', 'ankle', 'butt', 'glute']
    likely_base_bones = [bone for bone in armature_bones 
                       if any(keyword in bone.lower() for keyword in base_keywords)]
    
    print(f"DEBUG: Filtered to {len(likely_base_bones)} likely base bones (from {len(armature_bones)} total)")
    
    # Build a cache of armature bone categories to avoid repeated calls
    armature_bone_categories = {}
    
    for preset_bone in unmatched_preset_bones:
        print(f"DEBUG: Processing preset bone '{preset_bone}'")
        preset_category = find_semantic_category(preset_bone)
        
        if not preset_category:
            print(f"DEBUG: No category found for preset bone '{preset_bone}' - skipping")
            continue
            
        print(f"DEBUG: Preset bone '{preset_bone}' -> category '{preset_category}'")
        
        # Look for armature bone in the same category (only check likely base bones)
        found_match = False
        for armature_bone in likely_base_bones:
            # Skip if we already matched this armature bone
            if armature_bone in semantic_matches.values():
                continue
                
            # Check category (use cache if available)
            if armature_bone not in armature_bone_categories:
                armature_bone_categories[armature_bone] = find_semantic_category(armature_bone)
            
            armature_category = armature_bone_categories[armature_bone]
            
            if armature_category == preset_category:
                semantic_matches[preset_bone] = armature_bone
                print(f"DEBUG: SEMANTIC MATCH: '{preset_bone}' -> '{armature_bone}' (category: {preset_category})")
                found_match = True
                break
        
        if not found_match:
            print(f"DEBUG: No armature bone found for category '{preset_category}'")
    
    print(f"DEBUG: Final semantic matches: {len(semantic_matches)} found")
    return semantic_matches

def hybrid_bone_matching(preset_bones: Dict[str, dict], armature_bones: List[str]) -> Tuple[Dict[str, str], Dict[str, str], List[str]]:
    """
    Main hybrid matching function: exact first, then semantic for missing base bones
    Returns: (exact_matches, semantic_matches, completely_unmatched)
    """
    print(f"DEBUG: === HYBRID BONE MATCHING START ===")
    print(f"DEBUG: Preset bones: {list(preset_bones.keys())}")
    print(f"DEBUG: Armature bones: {armature_bones}")
    
    # Step 1: Apply exact matching
    exact_matches, unmatched_preset = apply_exact_matching(preset_bones, armature_bones)
    print(f"DEBUG: Exact matches: {exact_matches}")
    print(f"DEBUG: Unmatched after exact: {unmatched_preset}")
    
    # Step 2: Check if all base bones are covered by exact matching
    all_base_covered, missing_categories = check_base_bone_coverage(exact_matches, armature_bones)
    print(f"DEBUG: All base bones covered: {all_base_covered}")
    print(f"DEBUG: Missing categories: {missing_categories}")
    
    # Step 3: Apply semantic mapping only if base bones are missing
    semantic_matches = {}
    if not all_base_covered:
        print(f"DEBUG: Base bones missing, applying semantic mapping...")
        semantic_matches = apply_semantic_mapping(unmatched_preset, armature_bones, missing_categories)
    else:
        print(f"DEBUG: All base bones covered by exact matching, skipping semantic mapping")
    
    # Step 4: Find completely unmatched bones
    all_matched = set(exact_matches.keys()) | set(semantic_matches.keys())
    completely_unmatched = [bone for bone in unmatched_preset if bone not in all_matched]
    
    print(f"DEBUG: === HYBRID BONE MATCHING END ===")
    print(f"DEBUG: Final results - Exact: {len(exact_matches)}, Semantic: {len(semantic_matches)}, Unmatched: {len(completely_unmatched)}")
    
    return exact_matches, semantic_matches, completely_unmatched

# Main API function for integration
def map_bone_transforms(preset_bones: Dict[str, dict], armature_bones: List[str]) -> Tuple[Dict[str, str], Dict[str, str], List[str], str]:
    """
    Map bone transforms between preset and armature using hybrid approach
    Returns: (exact_matches, semantic_matches, unmatched_bones, summary_message)
    """
    exact_matches, semantic_matches, unmatched = hybrid_bone_matching(preset_bones, armature_bones)
    
    # Generate summary message
    total_preset = len(preset_bones)
    total_exact = len(exact_matches)
    total_semantic = len(semantic_matches)
    total_unmatched = len(unmatched)
    
    summary = f"Bone matching: {total_exact} exact, {total_semantic} semantic, {total_unmatched} unmatched (of {total_preset} total)"
    
    return exact_matches, semantic_matches, unmatched, summary