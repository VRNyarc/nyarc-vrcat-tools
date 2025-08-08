# Chain Analysis Utility
# Clean, robust bone chain discovery and building

import bpy


def has_significant_weights(mesh_obj, vertex_group, threshold=0.1):
    """Check if vertex group has weights above threshold"""
    original_mode = bpy.context.mode
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    try:
        mesh = mesh_obj.data
        group_index = vertex_group.index
        
        for vertex in mesh.vertices:
            for group in vertex.groups:
                if group.group == group_index and group.weight > threshold:
                    return True
        return False
        
    finally:
        if original_mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except:
                pass


def walk_up_to_root(bone, mesh_vertex_groups):
    """Walk up bone hierarchy until we hit a bone NOT in vertex groups"""
    vertex_group_names = {vg.name for vg in mesh_vertex_groups}
    
    current_bone = bone
    last_mesh_bone = bone
    
    # Walk up until we find a bone not in vertex groups
    while current_bone:
        if current_bone.name in vertex_group_names:
            last_mesh_bone = current_bone
            current_bone = current_bone.parent
        else:
            break
    
    return last_mesh_bone


def collect_all_children(bone):
    """Recursively collect all child bone names"""
    children = []
    
    for child in bone.children:
        children.append(child.name)
        children.extend(collect_all_children(child))
    
    return children


def collect_relevant_children(bone, vertex_group_names):
    """Recursively collect only children that have vertex groups OR are end bones of relevant chains"""
    relevant_children = []
    
    for child in bone.children:
        child_name = child.name
        
        # Check if this child bone has a vertex group in the mesh
        if child_name in vertex_group_names:
            # This bone affects the mesh - include it and all its children
            relevant_children.append(child_name)
            relevant_children.extend(collect_relevant_children(child, vertex_group_names))
            print(f"CHAIN_ANALYSIS: Including bone '{child_name}' - has vertex group")
        
        # Check if this is an end bone (structural bone needed even without vertex group)
        elif is_end_bone(child, bone, vertex_group_names):
            relevant_children.append(child_name)
            # Still check children in case there are more end bones
            relevant_children.extend(collect_relevant_children(child, vertex_group_names))
            print(f"CHAIN_ANALYSIS: Including bone '{child_name}' - end bone")
        
        else:
            # This bone doesn't have a vertex group - check if any of its descendants do
            descendant_relevant = collect_relevant_children(child, vertex_group_names)
            if descendant_relevant:
                # Some descendants are relevant, so include this bone as a structural bone
                relevant_children.append(child_name)
                relevant_children.extend(descendant_relevant)
                print(f"CHAIN_ANALYSIS: Including bone '{child_name}' - structural bone for relevant descendants")
            else:
                # No descendants are relevant - exclude this entire branch
                print(f"CHAIN_ANALYSIS: Excluding bone '{child_name}' - no vertex group and no relevant descendants")
    
    return relevant_children


def is_end_bone(child_bone, parent_bone, vertex_group_names):
    """Check if a bone is an end bone that should be included even without vertex groups"""
    child_name = child_bone.name
    parent_name = parent_bone.name
    
    # Method 1: Named end bones - but ONLY if direct parent is relevant to mesh
    if child_name.endswith('_end'):
        if parent_name in vertex_group_names:
            print(f"CHAIN_ANALYSIS: Including end bone '{child_name}' - parent '{parent_name}' has vertex group")
            return True
        else:
            print(f"CHAIN_ANALYSIS: Skipping end bone '{child_name}' - parent '{parent_name}' has no vertex group")
            return False
    
    # Method 2: Leaf bones (no children) of bones that have vertex groups
    if len(child_bone.children) == 0 and parent_name in vertex_group_names:
        return True
    
    # Method 3: Single child with no vertex group of a bone that has vertex group (common pattern)
    if (len(parent_bone.children) == 1 and 
        len(child_bone.children) == 0 and 
        parent_name in vertex_group_names):
        return True
    
    return False


def find_root_bones(mesh_obj, armature_obj):
    """Find all root bones by walking up from vertex groups"""
    if not mesh_obj or mesh_obj.type != 'MESH':
        return []
    
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return []
    
    root_bones = set()
    
    # Check each vertex group that has significant weights
    for vertex_group in mesh_obj.vertex_groups:
        if has_significant_weights(mesh_obj, vertex_group):
            bone = armature_obj.data.bones.get(vertex_group.name)
            if bone:
                # Walk up to find the root
                root_bone = walk_up_to_root(bone, mesh_obj.vertex_groups)
                root_bones.add(root_bone.name)
                print(f"CHAIN_ANALYSIS: Vertex group '{vertex_group.name}' → root '{root_bone.name}'")
    
    result = list(root_bones)
    print(f"CHAIN_ANALYSIS: Found {len(result)} root bones: {result}")
    return result


def build_chain_from_root(root_bone_name, armature_obj, mesh_obj):
    """Build filtered bone chain from root - only bones relevant to the mesh"""
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return []
    
    root_bone = armature_obj.data.bones.get(root_bone_name)
    if not root_bone:
        return []
    
    # Get vertex group names for filtering
    vertex_group_names = {vg.name for vg in mesh_obj.vertex_groups}
    
    # Start with root
    chain = [root_bone_name]
    
    # Add only relevant children (filtered)
    relevant_children = collect_relevant_children(root_bone, vertex_group_names)
    chain.extend(relevant_children)
    
    print(f"CHAIN_ANALYSIS: Filtered chain from '{root_bone_name}': {chain}")
    print(f"CHAIN_ANALYSIS: (Excluded bones without vertex groups in mesh '{mesh_obj.name}')")
    return chain


class BoneChain:
    """Simple data structure for bone chains"""
    
    def __init__(self, root_name, bones, mesh_name):
        self.root = root_name
        self.bones = bones
        self.mesh_name = mesh_name
        self.chain_type = None  # Will be set by classification
    
    def __repr__(self):
        return f"BoneChain(root='{self.root}', bones={len(self.bones)}, type={self.chain_type})"


def analyze_mesh_chains(mesh_obj, armature_obj):
    """Complete chain analysis for a mesh"""
    import time
    import datetime
    import traceback
    
    # Add timestamp and call stack trace
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔍 CHAIN_ANALYSIS [{timestamp}] - Called for mesh '{mesh_obj.name if mesh_obj else 'None'}' with armature '{armature_obj.name if armature_obj else 'None'}'")
    
    # Log who called this function
    stack = traceback.format_stack()
    print(f"📋 CHAIN_ANALYSIS_STACK: Called from {len(stack)} levels deep")
    for i, frame in enumerate(stack[-3:]):  # Show last 3 stack frames
        print(f"  [{i}] {frame.strip()}")
    
    if not mesh_obj or not armature_obj:
        return []
    
    print(f"CHAIN_ANALYSIS: Analyzing mesh '{mesh_obj.name}' with armature '{armature_obj.name}'")
    
    # Find all root bones
    root_bones = find_root_bones(mesh_obj, armature_obj)
    
    # Build chains from each root
    chains = []
    for root_name in root_bones:
        chain_bones = build_chain_from_root(root_name, armature_obj, mesh_obj)
        if chain_bones:
            chain = BoneChain(root_name, chain_bones, mesh_obj.name)
            chains.append(chain)
    
    print(f"CHAIN_ANALYSIS: Found {len(chains)} chains for mesh '{mesh_obj.name}'")
    return chains


def get_mesh_armature_pairs(selected_objects):
    """Get mesh-armature pairs from selection"""
    pairs = []
    meshes = [obj for obj in selected_objects if obj.type == 'MESH']
    
    for mesh_obj in meshes:
        # Find armature via modifier
        armature_obj = None
        for modifier in mesh_obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object:
                armature_obj = modifier.object
                break
        
        # Find armature via parent
        if not armature_obj and mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
            armature_obj = mesh_obj.parent
        
        if armature_obj:
            pairs.append((mesh_obj, armature_obj))
            print(f"CHAIN_ANALYSIS: Mesh '{mesh_obj.name}' → Armature '{armature_obj.name}'")
        else:
            print(f"CHAIN_ANALYSIS: No armature found for mesh '{mesh_obj.name}'")
    
    return pairs