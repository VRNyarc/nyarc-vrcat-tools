# Pose History Module - Simplified Flattening System
# Auto-saves pose transform history using flattened inheritance for mathematical consistency

import bpy
import json
import time
from datetime import datetime
from mathutils import Vector, Quaternion

# Import shape key metadata system
from .metadata_storage import VRCATMetadataStorage, get_metadata_manager, has_shape_key_pose_history
from .migration import migrate_armature_pose_history, check_migration_needed

# Import flattening system (HARD DEPENDENCY)
from ..utils.inheritance_flattening import (
    flatten_bone_transforms_for_save,
    prepare_bones_for_flattened_load,
    restore_original_inherit_scales
)

def save_pose_history_snapshot(armature, snapshot_name="Auto Snapshot", history_type="manual"):
    """
    Save current pose state using flattened inheritance system for mathematical consistency.
    
    Args:
        armature: Blender armature object
        snapshot_name: Name for this history entry
        history_type: Type of snapshot ("manual", "before_apply_rest", "auto")
    
    Returns:
        bool: Success status
    """
    try:
        print(f"POSE HISTORY SAVE: Starting flattened save for '{snapshot_name}'")
        
        # Step 1: Identify bones with non-identity transforms (what to save)
        target_bones = set()
        bones_skipped_identity = 0
        
        # Ensure we're in pose mode for analysis
        if bpy.context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        for pose_bone in armature.pose.bones:
            # Current pose transforms
            location = pose_bone.location
            rotation = pose_bone.rotation_quaternion
            scale = pose_bone.scale
            
            # Check if this bone has any non-identity transforms
            has_location_change = (abs(location.x) > 0.0001 or abs(location.y) > 0.0001 or abs(location.z) > 0.0001)
            has_rotation_change = not (abs(rotation.w - 1.0) < 0.0001 and abs(rotation.x) < 0.0001 and abs(rotation.y) < 0.0001 and abs(rotation.z) < 0.0001)
            has_scale_change = not (abs(scale.x - 1.0) < 0.0001 and abs(scale.y - 1.0) < 0.0001 and abs(scale.z - 1.0) < 0.0001)
            
            if has_location_change or has_rotation_change or has_scale_change:
                target_bones.add(pose_bone.name)
            else:
                bones_skipped_identity += 1
        
        print(f"POSE HISTORY SAVE: Found {len(target_bones)} bones with changes, skipping {bones_skipped_identity} identity bones")
        
        if not target_bones:
            print("POSE HISTORY SAVE: No bones with changes found, skipping save")
            return True  # Not an error, just nothing to save
        
        # Step 2: Use flattening module to capture inheritance-consistent transforms
        flattened_data = flatten_bone_transforms_for_save(armature, target_bones)
        
        if not flattened_data:
            print("POSE HISTORY SAVE: Flattening failed")
            return False
        
        # Step 3: Convert to INVERSE transforms to enable "Load Original" functionality
        bone_data = {}
        for bone_name, transform_data in flattened_data.items():
            # Calculate inverse transforms to undo the applied changes
            location = Vector(transform_data['location'])
            rotation = Quaternion(transform_data['rotation_quaternion'])
            scale = Vector(transform_data['scale'])
            
            # Inverse location: negate
            inverse_location = [-location.x, -location.y, -location.z]
            
            # Inverse rotation: invert quaternion
            inverse_rotation = rotation.inverted()
            inverse_rotation_list = [inverse_rotation.w, inverse_rotation.x, inverse_rotation.y, inverse_rotation.z]
            
            # Inverse scale: reciprocal (with safety check for division by zero)
            inverse_scale = [
                1.0 / scale.x if abs(scale.x) > 0.0001 else 1.0,
                1.0 / scale.y if abs(scale.y) > 0.0001 else 1.0,
                1.0 / scale.z if abs(scale.z) > 0.0001 else 1.0
            ]
            
            bone_data[bone_name] = {
                'location': inverse_location,
                'rotation_quaternion': inverse_rotation_list,
                'scale': inverse_scale
            }
        
        print(f"POSE HISTORY SAVE: Captured {len(bone_data)} inverse bone transforms for Load Original functionality")
        
        # Step 4: Create history entry with SEQUENTIAL ID (bulletproof uniqueness)
        timestamp = datetime.now().isoformat()
        
        # Get next sequential number by counting existing entries
        history_data = get_pose_history(armature)
        next_seq_num = len(history_data.get("entries", [])) + 1
        entry_id = str(next_seq_num)  # Sequential: 1, 2, 3, 4, etc. (simple numbers only)
        
        entry_data = {
            "timestamp": timestamp,
            "id": entry_id,
            "name": snapshot_name,
            "type": history_type,
            "bone_count": len(bone_data),
            "bones": bone_data,
            "flattened": True  # Mark as using flattened transforms
        }
        
        # Step 5: Save using shape key metadata system
        metadata_manager = get_metadata_manager(armature)
        success = metadata_manager.save_pose_entry(entry_data)
        
        if success:
            metadata_manager.cleanup_old_entries(20)
            print(f"POSE HISTORY SAVE: Successfully saved '{snapshot_name}' with {len(bone_data)} bones")
        
        return success
        
    except Exception as e:
        print(f"POSE HISTORY SAVE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_pose_history(armature):
    """
    Get pose history with automatic system detection and migration.
    
    Args:
        armature: Blender armature object
    
    Returns:
        dict: History data structure
    """
    try:
        # Try new shape key system first
        if has_shape_key_pose_history(armature):
            metadata_manager = get_metadata_manager(armature)
            return metadata_manager.load_pose_history()
        
        # Check if migration is needed
        if "nyarc_pose_history" in armature:
            print(f"POSE HISTORY: Migrating {armature.name} from custom properties to shape keys...")
            success, message = migrate_armature_pose_history(armature)
            
            if success:
                # Try loading from new system after migration
                metadata_manager = get_metadata_manager(armature)
                return metadata_manager.load_pose_history()
            else:
                print(f"POSE HISTORY: Migration failed: {message}, falling back to old system")
                return json.loads(armature["nyarc_pose_history"])
        
        # Return empty if no data found
        return {"version": "2.0", "entries": []}
        
    except Exception as e:
        print(f"POSE HISTORY: Error reading history: {e}")
        return {"version": "2.0", "entries": []}


def revert_to_pose_history_entry(context, armature, entry_id):
    """
    Revert armature to a specific pose history entry using simplified flattened loading.
    
    Args:
        context: Blender context
        armature: Blender armature object
        entry_id: ID of history entry to revert to
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        print(f"POSE HISTORY REVERT: Starting revert to {entry_id}")
        
        # Get history data
        history_data = get_pose_history(armature)
        
        # Find the target entry
        target_entry = None
        for entry in history_data["entries"]:
            if entry["id"] == entry_id:
                target_entry = entry
                break
        
        if not target_entry:
            return False, f"History entry {entry_id} not found"
        
        # CRITICAL FIX: Validate entry data integrity (no bone count filtering)
        expected_bones = target_entry.get("bone_count", 0)
        actual_bones = len(target_entry.get("bones", {}))
        
        print(f"POSE HISTORY: Loading Entry #{entry_id} with {expected_bones} bone transforms")
        
        # Only check for data corruption (count mismatch), not "too few" bones
        if expected_bones != actual_bones:
            print(f"POSE HISTORY WARNING: Entry {entry_id} bone count mismatch!")
            print(f"  Expected: {expected_bones}, Actual: {actual_bones}")
            print(f"  This indicates corrupted data, not user intent")
            return False, f"Entry {entry_id} appears corrupted (bone count mismatch: {expected_bones} vs {actual_bones})"
        
        # Ensure we're in pose mode
        if context.mode != 'POSE' or context.object != armature:
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
        
        # STEP 1: Clear all current pose transforms to identity
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        
        # Force scene update
        context.view_layer.update()
        
        print(f"POSE HISTORY REVERT: Cleared current pose")
        
        # STEP 2: CUMULATIVE LOADING - Apply all entries from target forward
        # Find all entries from target forward (including target)
        sorted_entries = sorted(history_data["entries"], key=lambda x: x["timestamp"])
        target_index = -1
        
        for i, entry in enumerate(sorted_entries):
            if entry["id"] == entry_id:
                target_index = i
                break
        
        if target_index == -1:
            return False, "Could not find entry in sorted list"
        
        entries_to_apply = sorted_entries[target_index:]
        entries_to_apply.reverse()  # Newest first for cumulative math
        
        print(f"POSE HISTORY REVERT: Computing cumulative transforms from {len(entries_to_apply)} entries")
        
        # Calculate cumulative transforms for all bones
        all_bone_names = set()
        for entry in entries_to_apply:
            all_bone_names.update(entry["bones"].keys())
        
        # Prepare bones for flattened loading (set inherit_scale=NONE)
        original_inherit_scales = prepare_bones_for_flattened_load(armature, all_bone_names)
        print(f"POSE HISTORY REVERT: Prepared {len(all_bone_names)} bones for flattened loading")
        
        bones_applied = 0
        
        for bone_name in all_bone_names:
            if bone_name not in armature.pose.bones:
                continue
                
            # Start with identity transforms
            cumulative_location = Vector((0.0, 0.0, 0.0))
            cumulative_rotation = Quaternion((1.0, 0.0, 0.0, 0.0))
            cumulative_scale = Vector((1.0, 1.0, 1.0))
            
            # Apply each entry's inverse transform for this bone (newest first)
            for entry in entries_to_apply:
                if bone_name in entry["bones"]:
                    bone_data = entry["bones"][bone_name]
                    
                    if all(key in bone_data for key in ['location', 'rotation_quaternion', 'scale']):
                        # Get inverse transforms from this entry
                        inv_location = Vector(bone_data['location'])
                        inv_rotation = Quaternion(bone_data['rotation_quaternion'])
                        inv_scale = Vector(bone_data['scale'])
                        
                        # CUMULATIVE MATH (same as reference):
                        # Location: Add inverse locations
                        cumulative_location += inv_location
                        
                        # Rotation: Multiply quaternions (newest first)
                        cumulative_rotation = inv_rotation @ cumulative_rotation
                        
                        # Scale: Multiply scales component-wise
                        cumulative_scale.x *= inv_scale.x
                        cumulative_scale.y *= inv_scale.y
                        cumulative_scale.z *= inv_scale.z
            
            # Apply cumulative transforms to the pose bone
            pose_bone = armature.pose.bones[bone_name]
            pose_bone.location = cumulative_location
            pose_bone.rotation_quaternion = cumulative_rotation
            pose_bone.scale = cumulative_scale
            bones_applied += 1
        
        # DON'T restore inherit_scale settings for pose history - we want to keep inherit_scale=NONE
        # for proper flattened inheritance behavior. This ensures leg bones get the correct
        # flattened scaling instead of reverting to original inherit_scale=FULL settings.
        print(f"POSE HISTORY REVERT: Keeping inherit_scale=NONE for {len(original_inherit_scales)} bones (flattened inheritance)")
        
        # Set armature to POSE position and update
        armature.data.pose_position = 'POSE'
        context.view_layer.update()
        
        message = f"Reverted to '{target_entry['name']}' - applied {bones_applied} bone transforms"
        print(f"POSE HISTORY REVERT: {message}")
        return True, message
        
    except Exception as e:
        error_msg = f"Error in pose history revert: {e}"
        print(f"POSE HISTORY REVERT ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg


def clear_all_pose_transforms(armature):
    """
    Clear all pose transforms to identity (reset to rest pose).
    
    Args:
        armature: Blender armature object
    
    Returns:
        bool: Success status
    """
    try:
        print(f"POSE RESET: Starting complete reset of {armature.name}")
        
        # Ensure we're in pose mode with correct armature active
        if bpy.context.mode != 'POSE' or bpy.context.object != armature:
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
        
        # Select all pose bones and clear transforms
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        
        # Force scene update
        bpy.context.view_layer.update()
        bpy.context.view_layer.depsgraph.update()
        
        print(f"POSE RESET: Complete reset finished for {armature.name}")
        return True
        
    except Exception as e:
        print(f"POSE RESET ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_pose_history_list(armature):
    """
    Get list of pose history entries for UI display.
    
    Args:
        armature: Blender armature object
    
    Returns:
        list: List of (id, name, timestamp, type) tuples
    """
    try:
        history_data = get_pose_history(armature)
        entries = []
        
        # Keep sequential order (Entry #1 first, Entry #2 second, etc.)
        # DO NOT re-sort by timestamp - this causes UI flipping!
        sorted_entries = history_data["entries"]  # Already sorted by ID in metadata_storage.py
        
        # Build UI list entries without debug spam
        for entry in sorted_entries:
            entries.append((
                entry["id"],
                entry["name"], 
                entry["timestamp"],
                entry.get("type", "manual")
            ))
        
        return entries
        
    except Exception as e:
        print(f"POSE HISTORY: Error getting history list: {e}")
        return []


# Export main functions for external use
__all__ = [
    'save_pose_history_snapshot',
    'get_pose_history', 
    'revert_to_pose_history_entry',
    'get_pose_history_list',
    'clear_all_pose_transforms'
]