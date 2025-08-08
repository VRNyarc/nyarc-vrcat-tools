# Detection Utilities  
# Auto-detect mesh-bone relationships and dependencies

import bpy

def detect_mesh_armature_relationships():
    """Detect relationships between selected meshes and armatures"""
    relationships = {}
    
    selected_objects = bpy.context.selected_objects
    mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
    armature_objects = [obj for obj in selected_objects if obj.type == 'ARMATURE']
    
    for mesh_obj in mesh_objects:
        mesh_relationships = []
        
        # Check armature modifiers
        for modifier in mesh_obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object:
                armature_obj = modifier.object
                mesh_relationships.append({
                    'armature': armature_obj,
                    'modifier': modifier,
                    'type': 'modifier'
                })
        
        # Check parent relationships
        if mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
            mesh_relationships.append({
                'armature': mesh_obj.parent,
                'modifier': None,
                'type': 'parent'
            })
        
        if mesh_relationships:
            relationships[mesh_obj.name] = mesh_relationships
    
    return relationships

def detect_bones_affecting_mesh(mesh_obj, armature_obj):
    """Detect which bones affect a specific mesh object"""
    affecting_bones = []
    
    if not mesh_obj or mesh_obj.type != 'MESH':
        return affecting_bones
    
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return affecting_bones
    
    # Get vertex groups that match bone names
    armature_bone_names = [bone.name for bone in armature_obj.data.bones]
    mesh_vertex_groups = [vg.name for vg in mesh_obj.vertex_groups]
    print(f"DEBUG SIMPLE: Mesh '{mesh_obj.name}' has vertex groups: {mesh_vertex_groups}")
    
    for vertex_group in mesh_obj.vertex_groups:
        if vertex_group.name in armature_bone_names:
            # Check if vertex group has significant weights
            if has_significant_weights(mesh_obj, vertex_group):
                affecting_bones.append(vertex_group.name)
                print(f"DEBUG SIMPLE: Added bone '{vertex_group.name}' - has vertex group with weights")
    
    # SIMPLE APPROACH: Only add DIRECT children that are end bones (no vertex groups themselves)
    print(f"DEBUG SIMPLE: Before adding end bones, affecting_bones = {affecting_bones}")
    for bone_name in list(affecting_bones):  # Use list() to avoid modifying while iterating
        bone = armature_obj.data.bones.get(bone_name)
        if bone:
            for child in bone.children:
                # Only add child if it's likely an end bone (no children of its own)
                if child.name not in affecting_bones and len(child.children) == 0:
                    affecting_bones.append(child.name)
                    print(f"DEBUG SIMPLE: Added end bone '{child.name}' for parent '{bone_name}'")
    print(f"DEBUG SIMPLE: After adding end bones, affecting_bones = {affecting_bones}")
    
    # Remove duplicates while preserving order
    seen = set()
    affecting_bones = [bone for bone in affecting_bones if not (bone in seen or seen.add(bone))]
    
    return affecting_bones

def has_significant_weights(mesh_obj, vertex_group, threshold=0.1):
    """Check if vertex group has weights above threshold"""
    # Switch to object mode to read vertex weights safely
    original_mode = bpy.context.mode
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    try:
        mesh = mesh_obj.data
        group_index = vertex_group.index
        
        # Check if any vertex has weight above threshold
        for vertex in mesh.vertices:
            for group in vertex.groups:
                if group.group == group_index and group.weight > threshold:
                    return True
        
        return False
        
    finally:
        # Restore original mode
        if original_mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except:
                pass  # Mode switch failed, stay in object mode

def detect_primary_bones(mesh_obj, armature_obj, threshold=0.5):
    """Detect bones that have primary influence (>50% weight) on mesh"""
    primary_bones = []
    
    affecting_bones = detect_bones_affecting_mesh(mesh_obj, armature_obj)
    
    for bone_name in affecting_bones:
        vertex_group = mesh_obj.vertex_groups.get(bone_name)
        if vertex_group and has_significant_weights(mesh_obj, vertex_group, threshold):
            primary_bones.append(bone_name)
    
    return primary_bones

def auto_detect_flip_candidates():
    """Auto-detect objects and bones that are good candidates for flipping"""
    candidates = {
        'meshes': [],
        'bones': [],
        'relationships': {}
    }
    
    # Get mesh-armature relationships
    relationships = detect_mesh_armature_relationships()
    candidates['relationships'] = relationships
    
    # Find mesh objects that might be accessories (small, asymmetric)
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    for mesh_obj in selected_meshes:
        # Check if mesh is likely an accessory
        is_accessory = is_likely_accessory(mesh_obj)
        print(f"DEBUG: Mesh '{mesh_obj.name}' is_likely_accessory: {is_accessory}")
        
        if is_accessory:
            candidates['meshes'].append(mesh_obj.name)
            print(f"DEBUG: Added mesh '{mesh_obj.name}' to candidates")
            
            # Find associated bones
            mesh_name = mesh_obj.name
            if mesh_name in relationships:
                print(f"DEBUG: Mesh '{mesh_name}' has {len(relationships[mesh_name])} relationship(s)")
                for relationship in relationships[mesh_name]:
                    armature_obj = relationship['armature']
                    
                    # Get ALL affecting bones (including children), not just primary ones
                    all_affecting_bones = detect_bones_affecting_mesh(mesh_obj, armature_obj)
                    primary_bones = detect_primary_bones(mesh_obj, armature_obj)
                    
                    print(f"DEBUG: Found {len(all_affecting_bones)} total affecting bones: {all_affecting_bones}")
                    print(f"DEBUG: Found {len(primary_bones)} primary bones: {primary_bones}")
                    
                    # Use ALL affecting bones, not just primary ones, to ensure child bones are included
                    candidates['bones'].extend(all_affecting_bones)
            else:
                print(f"DEBUG: Mesh '{mesh_name}' has no relationships")
    
    # Remove duplicates
    candidates['bones'] = list(set(candidates['bones']))
    print(f"DEBUG: Final candidates - meshes: {candidates['meshes']}, bones: {candidates['bones']}")
    
    return candidates

def is_likely_accessory(mesh_obj):
    """Heuristic to determine if mesh is likely an accessory (ring, pin, etc.)"""
    if not mesh_obj or mesh_obj.type != 'MESH':
        return False
    
    # More practical heuristics:
    # 1. Check naming patterns for accessories
    # 2. If no specific pattern, assume it's a valid mesh to mirror
    # 3. Remove restrictive vertex/size limits
    
    # Check naming patterns for accessories
    accessory_keywords = ['ring', 'pin', 'accessory', 'earring', 'watch', 'bracelet', 'necklace', 
                         'hair', 'hat', 'glasses', 'mask', 'glove', 'shoe', 'boot', 'belt']
    name_lower = mesh_obj.name.lower()
    if any(keyword in name_lower for keyword in accessory_keywords):
        return True
    
    # Check for side-specific naming (likely something that needs mirroring)
    side_keywords = ['.l', '.r', '_l', '_r', '.left', '.right', '_left', '_right']
    if any(side in name_lower for side in side_keywords):
        return True
    
    # Check object dimensions - only exclude extremely large objects (likely environment/props)
    dimensions = mesh_obj.dimensions
    max_dimension = max(dimensions)
    if max_dimension > 10.0:  # Much more generous limit - only exclude huge environment objects
        return False
    
    # Default to True - assume most selected mesh objects are valid for mirroring
    # This is much more user-friendly than the previous restrictive approach
    return True

def find_bone_chains(root_bones, armature_obj):
    """Find all child bones and bone chains for given root bones"""
    chain_bones = []
    
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return chain_bones
    
    for root_bone_name in root_bones:
        bone = armature_obj.data.bones.get(root_bone_name)
        if not bone:
            continue
            
        # Find all child bones recursively
        children = find_child_bones_recursive(bone, armature_obj)
        chain_bones.extend(children)
        
        # Also look for common bone chain patterns
        chain_bones.extend(find_bone_chain_patterns(root_bone_name, armature_obj))
    
    return chain_bones

def find_child_bones_recursive(bone, armature_obj):
    """Recursively find all child bones"""
    children = []
    
    for child in bone.children:
        children.append(child.name)
        # Recursively find grandchildren
        children.extend(find_child_bones_recursive(child, armature_obj))
    
    return children

def find_bone_chain_patterns(bone_name, armature_obj):
    """Find bones that follow common naming patterns for chains"""
    pattern_bones = []
    
    # Common patterns for bone chains
    patterns = [
        '_end',     # bone_end, bone.L_end
        '.end',     # bone.end, bone.L.end
        '_tip',     # bone_tip, bone.L_tip
        '.tip',     # bone.tip, bone.L.tip
        '_001',     # bone_001, bone.L_001
        '.001'      # bone.001, bone.L.001
    ]
    
    # Check for numbered sequences
    for i in range(1, 10):  # Check _001 to _009
        patterns.extend([f'_{i:03d}', f'.{i:03d}'])
    
    for pattern in patterns:
        # Try adding pattern to the bone name
        pattern_name = bone_name + pattern
        if armature_obj.data.bones.get(pattern_name):
            pattern_bones.append(pattern_name)
        
        # Also try inserting pattern before side suffix (.L/.R)
        from .naming import detect_naming_pattern, get_base_name
        current_suffix, _, _ = detect_naming_pattern(bone_name)
        if current_suffix:
            base_name = get_base_name(bone_name)
            pattern_with_suffix = base_name + pattern + current_suffix
            if armature_obj.data.bones.get(pattern_with_suffix):
                pattern_bones.append(pattern_with_suffix)
    
    return pattern_bones

def find_mirror_target_bone(bone_name, armature_obj):
    """Find the bone that should be the mirror target"""
    from .naming import get_opposite_name, detect_naming_pattern
    
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return None
    
    # Try to find opposite bone using naming convention
    opposite_name = get_opposite_name(bone_name)
    
    # Check if opposite bone exists
    if opposite_name in armature_obj.data.bones:
        return opposite_name
    
    # If not found, we'll need to create it
    return None