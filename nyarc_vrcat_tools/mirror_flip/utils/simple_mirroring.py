# Simple Mirroring Utility
# Clean mirroring logic for accessory and base armature chains

import bpy
from .bone_classification import get_vrchat_opposite_bone, get_vrchat_opposite_bone_axis_aware, should_filter_base_bone, is_vrchat_base_bone


def get_simple_suffix(axis='X'):
    """Get simple suffix to ADD to bone names (never replace)"""
    suffix_map = {
        'X': '.L',  # Left (default for X-axis)
        'Y': '.B',  # Back (default for Y-axis)
        'Z': '.D'   # Down (default for Z-axis)
    }
    return suffix_map.get(axis, '.L')


def mirror_accessory_chain(bone_chain, armature_obj, axis='X'):
    """Mirror an accessory bone chain - simple suffix addition"""
    import time
    import datetime
    import traceback
    
    # Add timestamp and call stack trace
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔧 MIRROR_ACCESSORY [{timestamp}] - Called for chain '{bone_chain.root if bone_chain else 'None'}'")
    
    # Log who called this function
    stack = traceback.format_stack()
    print(f"📋 MIRROR_ACCESSORY_STACK: Called from {len(stack)} levels deep")
    for i, frame in enumerate(stack[-3:]):  # Show last 3 stack frames
        print(f"  [{i}] {frame.strip()}")
    
    if not bone_chain or not bone_chain.bones:
        return []
    
    print(f"SIMPLE_MIRRORING: Mirroring accessory chain '{bone_chain.root}' with {len(bone_chain.bones)} bones")
    
    # Enter edit mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    mirrored_bones = []
    suffix = get_simple_suffix(axis)
    
    try:
        for bone_name in bone_chain.bones:
            original_bone = armature_obj.data.edit_bones.get(bone_name)
            if not original_bone:
                print(f"SIMPLE_MIRRORING: Bone '{bone_name}' not found, skipping")
                continue
            
            # Create mirrored bone name
            mirrored_name = bone_name + suffix
            
            # Check if already exists
            if armature_obj.data.edit_bones.get(mirrored_name):
                print(f"SIMPLE_MIRRORING: Bone '{mirrored_name}' already exists, skipping")
                continue
            
            # Create new bone
            new_bone = armature_obj.data.edit_bones.new(mirrored_name)
            new_bone.head = original_bone.head.copy()
            new_bone.tail = original_bone.tail.copy()
            new_bone.roll = original_bone.roll
            
            # Mirror position across axis
            if axis == 'X':
                new_bone.head.x = -new_bone.head.x
                new_bone.tail.x = -new_bone.tail.x
            elif axis == 'Y':
                new_bone.head.y = -new_bone.head.y
                new_bone.tail.y = -new_bone.tail.y
            elif axis == 'Z':
                new_bone.head.z = -new_bone.head.z
                new_bone.tail.z = -new_bone.tail.z
            
            # Set parent relationship
            if original_bone.parent:
                parent_name = original_bone.parent.name
                
                # Check if parent is VRChat base bone (needs axis-aware handling)
                if is_vrchat_base_bone(parent_name):
                    # VRChat base bone - use axis-aware mapping
                    parent_opposite = get_vrchat_opposite_bone_axis_aware(parent_name, axis)
                    if parent_opposite:
                        # X-axis: use opposite bone
                        parent_bone = armature_obj.data.edit_bones.get(parent_opposite)
                        if parent_bone:
                            new_bone.parent = parent_bone
                            print(f"SIMPLE_MIRRORING: Parented '{mirrored_name}' to VRChat opposite '{parent_opposite}'")
                        else:
                            print(f"SIMPLE_MIRRORING: VRChat opposite '{parent_opposite}' not found")
                    else:
                        # Y/Z-axis: use original bone
                        parent_bone = armature_obj.data.edit_bones.get(parent_name)
                        if parent_bone:
                            new_bone.parent = parent_bone
                            print(f"SIMPLE_MIRRORING: Parented '{mirrored_name}' to original VRChat base '{parent_name}' ({axis}-axis)")
                        else:
                            print(f"SIMPLE_MIRRORING: Original VRChat base '{parent_name}' not found")
                else:
                    # Regular accessory parent - add suffix
                    parent_mirrored_name = parent_name + suffix
                    parent_bone = armature_obj.data.edit_bones.get(parent_mirrored_name)
                    if parent_bone:
                        new_bone.parent = parent_bone
                        print(f"SIMPLE_MIRRORING: Parented '{mirrored_name}' to accessory '{parent_mirrored_name}'")
                    else:
                        print(f"SIMPLE_MIRRORING: Accessory parent '{parent_mirrored_name}' not found for '{mirrored_name}'")
            
            mirrored_bones.append(mirrored_name)
            print(f"SIMPLE_MIRRORING: Created accessory bone '{mirrored_name}'")
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"SIMPLE_MIRRORING: Successfully mirrored {len(mirrored_bones)} accessory bones")
        return mirrored_bones
        
    except Exception as e:
        # Ensure we return to object mode on error
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        raise e


def mirror_base_armature_chain(bone_chain, armature_obj, mesh_obj, axis='X'):
    """Mirror a base armature attachment chain - maps to existing opposite bones"""
    import time
    import datetime
    import traceback
    
    # Add timestamp and call stack trace
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔧 MIRROR_BASE [{timestamp}] - Called for chain '{bone_chain.root if bone_chain else 'None'}'")
    
    # Log who called this function
    stack = traceback.format_stack()
    print(f"📋 MIRROR_BASE_STACK: Called from {len(stack)} levels deep")
    for i, frame in enumerate(stack[-3:]):  # Show last 3 stack frames
        print(f"  [{i}] {frame.strip()}")
    
    if not bone_chain or not bone_chain.bones:
        return []
    
    print(f"SIMPLE_MIRRORING: Mirroring base armature chain '{bone_chain.root}' with {len(bone_chain.bones)} bones")
    
    # NEW LOGIC: Check if root bone is a VRChat base bone that should be reparented (axis-aware)
    root_opposite = get_vrchat_opposite_bone_axis_aware(bone_chain.root, axis)
    if root_opposite and armature_obj.data.bones.get(root_opposite):
        print(f"🔄 VRCHAT_REPARENT: Root '{bone_chain.root}' is VRChat base bone with opposite '{root_opposite}' - using reparenting logic")
        return mirror_vrchat_base_reparent_chain(bone_chain, armature_obj, mesh_obj, axis, root_opposite)
    
    # NEW CORE BONE LOGIC: Check if root bone is a core bone (no opposite expected)
    if not root_opposite:
        from .bone_classification import is_core_bone
        if is_core_bone(bone_chain.root):
            print(f"🔧 CORE_BONE: Root '{bone_chain.root}' is core bone - using core bone mirroring logic")
            return mirror_core_bone_chain(bone_chain, armature_obj, axis)
        else:
            print(f"SIMPLE_MIRRORING: No opposite found for base bone '{bone_chain.root}', treating as accessory")
            return mirror_accessory_chain(bone_chain, armature_obj, axis)
    
    # Check if opposite exists in armature
    if not armature_obj.data.bones.get(root_opposite):
        print(f"SIMPLE_MIRRORING: Opposite bone '{root_opposite}' not found in armature, treating as accessory")
        return mirror_accessory_chain(bone_chain, armature_obj, axis)
    
    # Enter edit mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    mirrored_bones = []
    suffix = get_simple_suffix(axis)
    
    try:
        for bone_name in bone_chain.bones:
            # Skip base armature bones not in mesh vertex groups
            if should_filter_base_bone(bone_name, mesh_obj.vertex_groups):
                print(f"SIMPLE_MIRRORING: Filtering out base bone '{bone_name}' - not in mesh")
                continue
            
            original_bone = armature_obj.data.edit_bones.get(bone_name)
            if not original_bone:
                print(f"SIMPLE_MIRRORING: Bone '{bone_name}' not found, skipping")
                continue
            
            # Check if this bone is a VRChat base bone
            if is_vrchat_base_bone(bone_name):
                # VRChat base bone - use axis-aware VRChat mapping, don't add suffix
                vrchat_opposite = get_vrchat_opposite_bone_axis_aware(bone_name, axis)
                if vrchat_opposite and armature_obj.data.edit_bones.get(vrchat_opposite):
                    mirrored_name = vrchat_opposite
                    print(f"SIMPLE_MIRRORING: Using existing VRChat base bone '{mirrored_name}' for '{bone_name}'")
                    mirrored_bones.append(mirrored_name)
                    continue
                else:
                    print(f"SIMPLE_MIRRORING: No VRChat opposite found for base bone '{bone_name}', skipping")
                    continue
            else:
                # Non-VRChat bone (accessory) - add suffix
                mirrored_name = bone_name + suffix
            
            # Check if already exists
            if armature_obj.data.edit_bones.get(mirrored_name):
                print(f"SIMPLE_MIRRORING: Bone '{mirrored_name}' already exists, skipping")
                continue
            
            # Create new bone
            new_bone = armature_obj.data.edit_bones.new(mirrored_name)
            new_bone.head = original_bone.head.copy()
            new_bone.tail = original_bone.tail.copy()
            new_bone.roll = original_bone.roll
            
            # Mirror position across axis
            if axis == 'X':
                new_bone.head.x = -new_bone.head.x
                new_bone.tail.x = -new_bone.tail.x
            elif axis == 'Y':
                new_bone.head.y = -new_bone.head.y
                new_bone.tail.y = -new_bone.tail.y
            elif axis == 'Z':
                new_bone.head.z = -new_bone.head.z
                new_bone.tail.z = -new_bone.tail.z
            
            # Set parent relationship
            if original_bone.parent:
                parent_name = original_bone.parent.name
                
                # Check if parent is VRChat base bone
                if is_vrchat_base_bone(parent_name):
                    # Parent is VRChat base bone - use axis-aware VRChat mapping
                    parent_opposite = get_vrchat_opposite_bone_axis_aware(parent_name, axis)
                    if parent_opposite:
                        parent_bone = armature_obj.data.edit_bones.get(parent_opposite)
                        if parent_bone:
                            new_bone.parent = parent_bone
                            print(f"SIMPLE_MIRRORING: Parented '{mirrored_name}' to VRChat base bone '{parent_opposite}'")
                        else:
                            print(f"SIMPLE_MIRRORING: VRChat parent bone '{parent_opposite}' not found")
                    else:
                        # No opposite (Y/Z axis) - parent to original VRChat base bone
                        parent_bone = armature_obj.data.edit_bones.get(parent_name)
                        if parent_bone:
                            new_bone.parent = parent_bone
                            print(f"SIMPLE_MIRRORING: Parented '{mirrored_name}' to original VRChat base bone '{parent_name}' ({axis}-axis)")
                        else:
                            print(f"SIMPLE_MIRRORING: Original VRChat parent bone '{parent_name}' not found")
                else:
                    # Parent is accessory bone - add suffix
                    parent_mirrored_name = parent_name + suffix
                    parent_bone = armature_obj.data.edit_bones.get(parent_mirrored_name)
                    if parent_bone:
                        new_bone.parent = parent_bone
                        print(f"SIMPLE_MIRRORING: Parented '{mirrored_name}' to accessory parent '{parent_mirrored_name}'")
                    else:
                        print(f"SIMPLE_MIRRORING: Accessory parent '{parent_mirrored_name}' not found")
            
            mirrored_bones.append(mirrored_name)
            print(f"SIMPLE_MIRRORING: Created base attachment bone '{mirrored_name}'")
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"SIMPLE_MIRRORING: Successfully mirrored {len(mirrored_bones)} base armature attachment bones")
        return mirrored_bones
        
    except Exception as e:
        # Ensure we return to object mode on error
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        raise e


def mirror_vrchat_base_reparent_chain(bone_chain, armature_obj, mesh_obj, axis='X', target_parent_bone=None):
    """NEW: Handle accessories parented to VRChat base bones - reparent to opposite base bone"""
    import time
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔄 VRCHAT_REPARENT [{timestamp}] - Reparenting chain '{bone_chain.root}' to '{target_parent_bone}'")
    
    if not bone_chain or not bone_chain.bones or not target_parent_bone:
        return []
    
    # Enter edit mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    mirrored_bones = []
    suffix = get_simple_suffix(axis)
    
    try:
        # Check if target parent exists
        target_parent = armature_obj.data.edit_bones.get(target_parent_bone)
        if not target_parent:
            print(f"🔄 VRCHAT_REPARENT: Target parent '{target_parent_bone}' not found!")
            return []
        
        for bone_name in bone_chain.bones:
            original_bone = armature_obj.data.edit_bones.get(bone_name)
            if not original_bone:
                print(f"🔄 VRCHAT_REPARENT: Bone '{bone_name}' not found, skipping")
                continue
            
            # SPECIAL CASE: If this bone IS the VRChat base bone, don't create it - just reference it
            if is_vrchat_base_bone(bone_name):
                vrchat_opposite = get_vrchat_opposite_bone_axis_aware(bone_name, axis)
                if vrchat_opposite and armature_obj.data.edit_bones.get(vrchat_opposite):
                    print(f"🔄 VRCHAT_REPARENT: Using existing VRChat base bone '{vrchat_opposite}' instead of creating '{bone_name}'")
                    mirrored_bones.append(vrchat_opposite)
                    continue
                else:
                    print(f"🔄 VRCHAT_REPARENT: VRChat opposite '{vrchat_opposite}' not found for '{bone_name}', skipping")
                    continue
            
            # ACCESSORY BONE: Create mirrored version with suffix
            mirrored_name = bone_name + suffix
            
            # Check if already exists
            if armature_obj.data.edit_bones.get(mirrored_name):
                print(f"🔄 VRCHAT_REPARENT: Bone '{mirrored_name}' already exists, using existing")
                mirrored_bones.append(mirrored_name)
                continue
            
            # Create new accessory bone
            new_bone = armature_obj.data.edit_bones.new(mirrored_name)
            new_bone.head = original_bone.head.copy()
            new_bone.tail = original_bone.tail.copy()
            new_bone.roll = original_bone.roll
            
            # Mirror position across axis
            if axis == 'X':
                new_bone.head.x = -new_bone.head.x
                new_bone.tail.x = -new_bone.tail.x
            elif axis == 'Y':
                new_bone.head.y = -new_bone.head.y
                new_bone.tail.y = -new_bone.tail.y
            elif axis == 'Z':
                new_bone.head.z = -new_bone.head.z
                new_bone.tail.z = -new_bone.tail.z
            
            # KEY LOGIC: Re-parent to the target VRChat base bone
            if original_bone.parent and is_vrchat_base_bone(original_bone.parent.name):
                # Parent was VRChat base bone, use the target opposite bone
                new_bone.parent = target_parent
                print(f"🔄 VRCHAT_REPARENT: Parented '{mirrored_name}' to target VRChat base bone '{target_parent_bone}'")
            elif original_bone.parent:
                # Parent was accessory bone, find its mirrored version
                parent_mirrored_name = original_bone.parent.name + suffix
                parent_bone = armature_obj.data.edit_bones.get(parent_mirrored_name)
                if parent_bone:
                    new_bone.parent = parent_bone
                    print(f"🔄 VRCHAT_REPARENT: Parented '{mirrored_name}' to accessory parent '{parent_mirrored_name}'")
                else:
                    # Fallback: parent to target base bone
                    new_bone.parent = target_parent
                    print(f"🔄 VRCHAT_REPARENT: Fallback - parented '{mirrored_name}' to target base bone '{target_parent_bone}'")
            else:
                # No parent, parent to target base bone
                new_bone.parent = target_parent
                print(f"🔄 VRCHAT_REPARENT: Root accessory - parented '{mirrored_name}' to target base bone '{target_parent_bone}'")
            
            mirrored_bones.append(mirrored_name)
            print(f"🔄 VRCHAT_REPARENT: Created reparented accessory bone '{mirrored_name}'")
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"🔄 VRCHAT_REPARENT: Successfully reparented {len(mirrored_bones)} bones to '{target_parent_bone}'")
        return mirrored_bones
        
    except Exception as e:
        # Ensure we return to object mode on error
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        raise e


def mirror_core_bone_chain(bone_chain, armature_obj, axis='X'):
    """Handle chains starting with core bones (Hips, Spine) - keep core bones, mirror accessories only"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔧 CORE_BONE [{timestamp}] - Core bone chain '{bone_chain.root}' with {len(bone_chain.bones)} bones")
    
    if not bone_chain or not bone_chain.bones:
        return []
    
    from .bone_classification import is_core_bone
    
    # Enter edit mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    mirrored_bones = []
    suffix = get_simple_suffix(axis)
    
    try:
        # Find where core bones end and accessory bones begin
        core_bones = []
        accessory_bones = []
        
        for bone_name in bone_chain.bones:
            if is_core_bone(bone_name):
                core_bones.append(bone_name)
                print(f"🔧 CORE_BONE: '{bone_name}' is core bone - keeping original")
            else:
                accessory_bones.append(bone_name)
                print(f"🔧 CORE_BONE: '{bone_name}' is accessory - will mirror")
        
        # Keep track of last core bone for parenting
        last_core_bone = core_bones[-1] if core_bones else bone_chain.root
        print(f"🔧 CORE_BONE: Last core bone is '{last_core_bone}' - accessory chain will parent to this")
        
        # Get the original core bone as reference for parenting
        original_parent = armature_obj.data.edit_bones.get(last_core_bone)
        if not original_parent:
            print(f"🔧 CORE_BONE: ERROR - Core bone '{last_core_bone}' not found!")
            return []
        
        # Mirror only the accessory bones
        for i, bone_name in enumerate(accessory_bones):
            original_bone = armature_obj.data.edit_bones.get(bone_name)
            if not original_bone:
                print(f"🔧 CORE_BONE: Bone '{bone_name}' not found, skipping")
                continue
            
            # Create mirrored bone
            mirrored_name = bone_name + suffix
            
            # Check if already exists
            if armature_obj.data.edit_bones.get(mirrored_name):
                print(f"🔧 CORE_BONE: Bone '{mirrored_name}' already exists, using existing")
                mirrored_bones.append(mirrored_name)
                continue
            
            # Create new bone
            mirrored_bone = armature_obj.data.edit_bones.new(mirrored_name)
            
            # Mirror position across the specified axis
            if axis == 'X':
                mirrored_bone.head = (-original_bone.head.x, original_bone.head.y, original_bone.head.z)
                mirrored_bone.tail = (-original_bone.tail.x, original_bone.tail.y, original_bone.tail.z)
            elif axis == 'Y':
                mirrored_bone.head = (original_bone.head.x, -original_bone.head.y, original_bone.head.z)
                mirrored_bone.tail = (original_bone.tail.x, -original_bone.tail.y, original_bone.tail.z)
            elif axis == 'Z':
                mirrored_bone.head = (original_bone.head.x, original_bone.head.y, -original_bone.head.z)
                mirrored_bone.tail = (original_bone.tail.x, original_bone.tail.y, -original_bone.tail.z)
            
            # Set parenting
            if i == 0:
                # First accessory bone parents to the last core bone
                mirrored_bone.parent = original_parent
                print(f"🔧 CORE_BONE: Parented '{mirrored_name}' to core bone '{last_core_bone}'")
            else:
                # Subsequent bones parent to previous mirrored bone
                prev_mirrored_name = accessory_bones[i-1] + suffix
                prev_mirrored = armature_obj.data.edit_bones.get(prev_mirrored_name)
                if prev_mirrored:
                    mirrored_bone.parent = prev_mirrored
                    print(f"🔧 CORE_BONE: Parented '{mirrored_name}' to '{prev_mirrored_name}'")
            
            mirrored_bones.append(mirrored_name)
            print(f"🔧 CORE_BONE: Created '{mirrored_name}'")
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"🔧 CORE_BONE: Successfully mirrored {len(mirrored_bones)} accessory bones, kept {len(core_bones)} core bones unchanged")
        return mirrored_bones
        
    except Exception as e:
        # Ensure we return to object mode on error
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        raise e


def update_vertex_groups(mesh_obj, original_bones, mirrored_bones, axis='X'):
    """Update vertex groups to reference mirrored bones"""
    import time
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔧 UPDATE_VG [{timestamp}] - Called for mesh '{mesh_obj.name}' with {len(mirrored_bones)} bones")
    
    if len(original_bones) != len(mirrored_bones):
        print(f"🔧 UPDATE_VG: Bone count mismatch - {len(original_bones)} original, {len(mirrored_bones)} mirrored")
        print(f"🔧 UPDATE_VG: This is likely VRChat reparenting - using intelligent vertex group mapping")
        return update_vertex_groups_intelligent_mapping(mesh_obj, original_bones, mirrored_bones, axis)
    
    bone_mapping = dict(zip(original_bones, mirrored_bones))
    updated_groups = []
    
    for original_bone, mirrored_bone in bone_mapping.items():
        # NEW LOGIC: Handle VRChat base bone reparenting
        if is_vrchat_base_bone(original_bone) and is_vrchat_base_bone(mirrored_bone):
            # This is a VRChat base bone → VRChat base bone mapping (e.g., RightKnee → LeftKnee)
            result = update_vrchat_base_vertex_group(mesh_obj, original_bone, mirrored_bone)
            if result:
                updated_groups.append(mirrored_bone)
            continue
        
        # ORIGINAL LOGIC: Regular accessory bone creation
        # Safety check: skip if vertex group already exists
        if mesh_obj.vertex_groups.get(mirrored_bone):
            print(f"🛡️ VG_SAFETY_CHECK: Vertex group '{mirrored_bone}' already exists on '{mesh_obj.name}' - skipping creation")
            updated_groups.append(mirrored_bone)  # Still count it as processed
            continue
        
        # Check if original bone has vertex group
        original_vg = mesh_obj.vertex_groups.get(original_bone)
        if original_vg:
            # Create vertex group for mirrored bone
            mirrored_vg = mesh_obj.vertex_groups.new(name=mirrored_bone)
            
            # Copy weights from original to mirrored
            for vertex in mesh_obj.data.vertices:
                for group in vertex.groups:
                    if group.group == original_vg.index:
                        mirrored_vg.add([vertex.index], group.weight, 'REPLACE')
            
            # REMOVE the original vertex group from mirrored mesh
            mesh_obj.vertex_groups.remove(original_vg)
            print(f"SIMPLE_MIRRORING: Removed original vertex group '{original_bone}' from mirrored mesh '{mesh_obj.name}'")
            
            updated_groups.append(mirrored_bone)
            print(f"SIMPLE_MIRRORING: Created vertex group '{mirrored_bone}' from '{original_bone}'")
    
    print(f"SIMPLE_MIRRORING: Updated {len(updated_groups)} vertex groups for '{mesh_obj.name}'")
    return updated_groups


def update_vertex_groups_intelligent_mapping(mesh_obj, original_bones, mirrored_bones, axis='X'):
    """NEW: Handle vertex group updates when bone counts don't match (VRChat reparenting)"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🧠 VG_INTELLIGENT [{timestamp}] - Mapping vertex groups intelligently for mesh '{mesh_obj.name}'")
    
    updated_groups = []
    
    # Create mapping by matching bone names
    for original_bone in original_bones:
        # Check if there's a corresponding mirrored bone
        mirrored_bone = None
        
        # Method 1: Look for exact match in mirrored bones
        if original_bone in mirrored_bones:
            mirrored_bone = original_bone
            print(f"🧠 VG_INTELLIGENT: Exact match '{original_bone}' → '{mirrored_bone}'")
        
        # Method 2: Look for VRChat base bone opposite (axis-aware)
        elif is_vrchat_base_bone(original_bone):
            vrchat_opposite = get_vrchat_opposite_bone_axis_aware(original_bone, axis)
            if vrchat_opposite and vrchat_opposite in mirrored_bones:
                mirrored_bone = vrchat_opposite
                print(f"🧠 VG_INTELLIGENT: VRChat base bone '{original_bone}' → '{mirrored_bone}'")
            else:
                # For Y/Z axes, VRChat base bones stay the same (no opposite created)
                # But they're not in mirrored_bones list since no new bone was created
                if axis != 'X':
                    mirrored_bone = original_bone
                    print(f"🧠 VG_INTELLIGENT: VRChat base bone '{original_bone}' → '{mirrored_bone}' (same bone for {axis}-axis)")
        
        # Method 3: Look for accessory bone with axis-appropriate suffix
        else:
            axis_suffix = get_simple_suffix(axis)
            suffixed_name = original_bone + axis_suffix
            if suffixed_name in mirrored_bones:
                mirrored_bone = suffixed_name
                print(f"🧠 VG_INTELLIGENT: Accessory bone '{original_bone}' → '{mirrored_bone}' (suffix: '{axis_suffix}')")
        
        # Update vertex group if mapping found
        if mirrored_bone:
            if is_vrchat_base_bone(original_bone) and is_vrchat_base_bone(mirrored_bone):
                # VRChat base bone vertex group handling
                if original_bone == mirrored_bone:
                    # Same bone (Y/Z axis) - no vertex group update needed
                    print(f"🧠 VG_INTELLIGENT: VRChat base bone '{original_bone}' maps to itself - no vertex group update needed")
                    updated_groups.append(mirrored_bone)
                else:
                    # Different bone (X axis) - swap vertex groups
                    result = update_vrchat_base_vertex_group(mesh_obj, original_bone, mirrored_bone)
                    if result:
                        updated_groups.append(mirrored_bone)
            else:
                # Regular accessory bone vertex group creation
                result = update_accessory_vertex_group(mesh_obj, original_bone, mirrored_bone)
                if result:
                    updated_groups.append(mirrored_bone)
        else:
            print(f"🧠 VG_INTELLIGENT: No mapping found for bone '{original_bone}' - skipping")
    
    print(f"🧠 VG_INTELLIGENT: Successfully updated {len(updated_groups)} vertex groups")
    return updated_groups


def update_vrchat_base_vertex_group(mesh_obj, original_base_bone, target_base_bone):
    """NEW: Handle VRChat base bone vertex group swapping (e.g., RightKnee → LeftKnee)"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"🔄 VG_VRCHAT_SWAP [{timestamp}] - Swapping '{original_base_bone}' → '{target_base_bone}' on mesh '{mesh_obj.name}'")
    
    # Check if original vertex group exists
    original_vg = mesh_obj.vertex_groups.get(original_base_bone)
    if not original_vg:
        print(f"🔄 VG_VRCHAT_SWAP: Original vertex group '{original_base_bone}' not found on mesh '{mesh_obj.name}'")
        return False
    
    # Check if target vertex group already exists
    target_vg = mesh_obj.vertex_groups.get(target_base_bone)
    if target_vg:
        print(f"🔄 VG_VRCHAT_SWAP: Target vertex group '{target_base_bone}' already exists on mesh '{mesh_obj.name}' - transferring weights")
        
        # Transfer weights from original to target
        for vertex in mesh_obj.data.vertices:
            for group in vertex.groups:
                if group.group == original_vg.index:
                    target_vg.add([vertex.index], group.weight, 'REPLACE')
        
        # Remove original vertex group
        mesh_obj.vertex_groups.remove(original_vg)
        print(f"🔄 VG_VRCHAT_SWAP: Transferred weights from '{original_base_bone}' to existing '{target_base_bone}' and removed original")
        return True
    else:
        # Rename original vertex group to target name
        original_vg.name = target_base_bone
        print(f"🔄 VG_VRCHAT_SWAP: Renamed vertex group '{original_base_bone}' → '{target_base_bone}' on mesh '{mesh_obj.name}'")
        return True


def update_accessory_vertex_group(mesh_obj, original_bone, mirrored_bone):
    """NEW: Handle accessory bone vertex group creation with .L suffix"""
    print(f"🔧 VG_ACCESSORY: Creating vertex group '{mirrored_bone}' from '{original_bone}' on mesh '{mesh_obj.name}'")
    
    # Check if mirrored vertex group already exists
    if mesh_obj.vertex_groups.get(mirrored_bone):
        print(f"🔧 VG_ACCESSORY: Vertex group '{mirrored_bone}' already exists - skipping")
        return True
    
    # Check if original vertex group exists
    original_vg = mesh_obj.vertex_groups.get(original_bone)
    if not original_vg:
        print(f"🔧 VG_ACCESSORY: Original vertex group '{original_bone}' not found - skipping")
        return False
    
    # Create new vertex group for mirrored bone
    mirrored_vg = mesh_obj.vertex_groups.new(name=mirrored_bone)
    
    # Copy weights from original to mirrored
    for vertex in mesh_obj.data.vertices:
        for group in vertex.groups:
            if group.group == original_vg.index:
                mirrored_vg.add([vertex.index], group.weight, 'REPLACE')
    
    # Remove original vertex group
    mesh_obj.vertex_groups.remove(original_vg)
    print(f"🔧 VG_ACCESSORY: Created vertex group '{mirrored_bone}' and removed original '{original_bone}'")
    return True