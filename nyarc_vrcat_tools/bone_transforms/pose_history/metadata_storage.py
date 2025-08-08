# Fixed Shape Key Metadata Storage - Names Only
# Stores ALL data in shape key names (no custom properties)

import bpy
import json
import base64
import binascii
import zlib
import time
import uuid
from datetime import datetime
from mathutils import Vector, Quaternion

class VRCATMetadataStorage:
    """Fixed metadata storage using only shape key names"""
    
    def __init__(self, armature):
        self.armature = armature
        self.metadata_obj = None
        self._ensure_metadata_object()
    
    def _ensure_metadata_object(self):
        """Get or create metadata storage object using armature modifier linking"""
        # STEP 1: Look for objects with armature modifier pointing to this armature
        discovered_obj = self._discover_existing_metadata()
        if discovered_obj:
            print(f"POSE HISTORY: Found existing metadata linked to armature: {discovered_obj.name}")
            self.metadata_obj = discovered_obj
            self._ensure_object_hidden(self.metadata_obj)
            return
        
        # STEP 2: Create new metadata object with random UUID name
        random_name = f"VRCAT_PoseHistory_{uuid.uuid4().hex[:12]}"
        print(f"POSE HISTORY: Creating new metadata object: {random_name}")
        self.metadata_obj = self._create_metadata_object(random_name)
    
    def _discover_existing_metadata(self):
        """
        Find pose history objects by checking for armature modifiers pointing to this armature.
        This creates a permanent link that survives export/import cycles.
        
        Returns:
            bpy.types.Object or None: Found metadata object
        """
        # Look for objects with armature modifier pointing to our armature
        for obj in bpy.data.objects:
            if "VRCAT_PoseHistory" in obj.name and obj.type == 'MESH':
                # Check if object has armature modifier pointing to our armature
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == self.armature:
                        # Verify it has pose history data
                        if self._verify_pose_history_data(obj):
                            return obj
        
        return None
    
    def _verify_pose_history_data(self, obj):
        """Verify that an object contains valid pose history data"""
        try:
            if not obj.data or not obj.data.shape_keys:
                return False
            
            # Check for pose history shape keys
            for shape_key in obj.data.shape_keys.key_blocks:
                if (shape_key.name.startswith("V_") or 
                    shape_key.name.startswith("VRCAT_")):
                    return True
            
            return False
        except:
            return False
    
    
    def _ensure_object_hidden(self, obj):
        """Ensure metadata object is properly hidden"""
        try:
            obj.hide_viewport = True      # Hide in viewport (3D view)
            obj.hide_render = True        # Hide in render
            obj.hide_select = True        # Hide from selection
            obj.hide_set(True)           # Hide in outliner
            
            # Make it very small but keep at armature location for Unity compatibility
            obj.scale = (0.001, 0.001, 0.001)
            obj.display_type = 'WIRE'
            
            # Keep at armature location (don't move far away to avoid Unity bounding box issues)
            obj.location = self.armature.location
            
            print(f"Applied hiding settings to existing metadata object: {obj.name}")
        except Exception as e:
            print(f"Warning: Could not fully hide metadata object {obj.name}: {e}")
    
    def _create_metadata_object(self, name):
        """Create minimal dummy mesh for metadata storage with armature modifier linking"""
        # Create minimal mesh (2 vertices, no faces)
        mesh = bpy.data.meshes.new(name + "_mesh")
        vertices = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.001)]  # Minimal offset
        mesh.from_pydata(vertices, [], [])  # No edges, no faces
        mesh.update()
        
        # Create object
        obj = bpy.data.objects.new(name, mesh)
        
        # Add to same collection as armature
        for collection in self.armature.users_collection:
            collection.objects.link(obj)
            break
        
        # Add armature modifier to create permanent link to armature
        # This survives export/import cycles and allows reliable discovery
        armature_modifier = obj.modifiers.new(name="ArmatureLink", type='ARMATURE')
        armature_modifier.object = self.armature
        
        # Apply hiding using the centralized function
        self._ensure_object_hidden(obj)
        
        # Identification markers (on object, not shape keys)
        obj["VRCAT_METADATA"] = True
        obj["VRCAT_VERSION"] = "2.0" 
        obj["VRCAT_STORAGE_TYPE"] = "pose_history"
        
        print(f"Created metadata object with armature modifier: {name}")
        return obj
    
    def _compress_pose_data(self, pose_data):
        """Compress pose data for storage in name - OPTIMIZED VERSION"""
        # Create ultra-compact representation - only store essential bone data
        compact_bones = {}
        for bone_name, bone_data in pose_data.get("bones", {}).items():
            # Store as tuple: [location, rotation_quat, scale, inherit_scale]
            compact_bones[bone_name] = [
                bone_data.get('location', [0,0,0]),
                bone_data.get('rotation_quaternion', [1,0,0,0]), 
                bone_data.get('scale', [1,1,1]),
                bone_data.get('inherit_scale', 'FULL')
            ]
        
        # Ultra-compact entry with single-letter keys
        compact_entry = {
            "n": pose_data.get("name", "Unknown"),
            "t": pose_data.get("type", "manual"), 
            "b": compact_bones,
            "s": pose_data.get("inherit_scale_state", {})  # Complete inherit_scale state
        }
        
        json_str = json.dumps(compact_entry, separators=(',', ':'))
        compressed = zlib.compress(json_str.encode('utf-8'))
        encoded = base64.b64encode(compressed).decode('ascii')
        return encoded
    
    def _decompress_pose_data(self, encoded_data):
        """Decompress pose data from name - ROBUST WITH VALIDATION"""
        if not encoded_data or len(encoded_data) < 4:
            return None
            
        try:
            # Validate base64 format first
            if not all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in encoded_data):
                return None
                
            # Add padding if needed
            missing_padding = len(encoded_data) % 4
            if missing_padding:
                encoded_data += '=' * (4 - missing_padding)
                
            compressed = base64.b64decode(encoded_data.encode('ascii'))
            
            # Validate compressed data length
            if len(compressed) < 10:  # Minimum reasonable compressed size
                return None
                
            json_str = zlib.decompress(compressed).decode('utf-8')
            compact_data = json.loads(json_str)
            
            # Convert back to full format if it's compact
            if "b" in compact_data and "n" in compact_data:
                # It's compact format - expand it
                full_bones = {}
                for bone_name, bone_tuple in compact_data["b"].items():
                    full_bones[bone_name] = {
                        'location': bone_tuple[0],
                        'rotation_quaternion': bone_tuple[1],
                        'scale': bone_tuple[2], 
                        'inherit_scale': bone_tuple[3]
                    }
                
                return {
                    "name": compact_data["n"],
                    "type": compact_data["t"],
                    "bones": full_bones,
                    "inherit_scale_state": compact_data.get("s", {})  # Complete inherit_scale state
                }
            else:
                # Legacy full format
                return compact_data
                
        except (binascii.Error, zlib.error, json.JSONDecodeError, Exception):
            return None
    
    def _create_shape_key_name(self, entry_data):
        """Create shape key name with ALL data embedded - sequential numbering only"""
        # Extract sequential number from entry ID (simple integer)
        entry_id_str = entry_data.get("id", "1")
        
        # Sequential format only: 1, 2, 3, 4, etc.
        try:
            entry_id_num = int(entry_id_str)
        except:
            entry_id_num = 1
        
        entry_type = entry_data.get("type", "manual")
        bone_count = entry_data.get("bone_count", 0)
        entry_name = entry_data.get("name", "Unknown")[:15]  # Pose name for identification
        
        # Parse timestamp safely
        timestamp = entry_data.get("timestamp", datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y%m%d")
            time_str = dt.strftime("%H%M%S")
        except:
            date_str = "00000000"
            time_str = "000000"
        
        # Truncate type for space
        type_map = {
            "manual": "M",
            "before_apply_rest": "B", 
            "auto": "A"
        }
        type_short = type_map.get(entry_type, "M")
        
        # Compress the bone data
        compressed_data = self._compress_pose_data(entry_data)
        
        # Create pose data shape keys + timestamp shape key
        max_name_length = 63  # Blender's actual hard limit
        
        # ULTRA-COMPACT format to prevent truncation
        # Minimal metadata: V_ID_BC_ (saves ~30 characters)
        base_name = f"V_{entry_id_num}_{bone_count}_"
        
        # Create timestamp shape key name
        timestamp = entry_data.get("timestamp", datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp_unix = int(dt.timestamp())
        except:
            timestamp_unix = int(time.time())
        
        timestamp_hex = hex(timestamp_unix)[2:]  # Remove '0x' prefix
        timestamp_key = f"{base_name}T_{timestamp_hex}"
        
        # Create pose data shape key(s)
        pose_keys = []
        if len(base_name) + len(compressed_data) + 6 <= max_name_length:  # Leave room for __P00
            # Single name can fit everything
            pose_keys.append(f"{base_name}__P00_{compressed_data}")
        else:
            # Split data across multiple shape keys
            data_per_key = max_name_length - len(base_name) - 6  # Leave room for __P## suffix
            
            for i in range(0, len(compressed_data), data_per_key):
                part_data = compressed_data[i:i+data_per_key]
                part_name = f"{base_name}__P{i//data_per_key:02d}_{part_data}"
                pose_keys.append(part_name)
        
        # Return timestamp key first, then pose data keys
        return [timestamp_key] + pose_keys
    
    def _parse_shape_key_names(self, shape_key_names):
        """Parse metadata and data from shape key name(s) with enhanced ID validation"""
        if not shape_key_names:
            return None
        
        # Separate timestamp keys from pose data keys
        timestamp_keys = [name for name in shape_key_names if "_T_" in name]
        pose_keys = [name for name in shape_key_names if "__P" in name or "_P" in name]
        
        # Extract timestamp if available
        timestamp = datetime.now().isoformat()  # Default fallback
        if timestamp_keys:
            try:
                timestamp_name = timestamp_keys[0]
                hex_part = timestamp_name.split("_T_")[1]
                timestamp_unix = int(hex_part, 16)
                timestamp = datetime.fromtimestamp(timestamp_unix).isoformat()
            except:
                # Keep default timestamp on parse error
                pass
        
        # Parse pose data keys only (timestamp already extracted)
        if len(pose_keys) == 1:
            # Single part - handle pose data key
            name = pose_keys[0]
            parts = name.split("_")
            
            if parts[0] == "V" and len(parts) >= 4:
                # Sequential format: V_ID_BC__P00_data or V_ID_BC__data
                try:
                    # Parse entry ID - sequential number only
                    entry_id = parts[1]  # Simple number: 1, 2, 3, 4, etc.
                    bone_count = int(parts[2])
                    
                    # Extract compressed data (skip __P00 part if present)
                    if "__P00" in name:
                        compressed_data = name.split("__P00_")[1]
                    else:
                        compressed_data = "_".join(parts[3:]) if len(parts) > 3 else ""
                    
                    # Default values for missing metadata
                    pose_name = "Restored Pose"
                    type_short = "M"
                    
                except (ValueError, IndexError):
                    print(f"Error parsing pose data format: {name}")
                    return None
                    
            else:
                # No other formats supported
                return None
        elif len(pose_keys) > 1:
            # Multi-part - reconstruct data
            # Sort by part number - handle both __P## and _P## formats
            def extract_part_number(name):
                try:
                    if "__P" in name:
                        return int(name.split("__P")[1].split("_")[0])
                    elif "_P" in name:
                        return int(name.split("_P")[1].split("_")[0])
                    else:
                        return 0
                except:
                    return 0
            
            sorted_names = sorted(pose_keys, key=extract_part_number)
            
            # Extract metadata from first part
            first_name = sorted_names[0]
            parts = first_name.split("_")
            
            # Handle both formats in multi-part reconstruction
            try:
                if parts[0] == "V":
                    # Sequential format only: V_ID_BC__P##_data
                    if len(parts) < 3:
                        return None
                    # Parse entry ID - sequential number only
                    entry_id = parts[1]  # Simple number: 1, 2, 3, etc.
                    bone_count = int(parts[2])
                    pose_name = "Restored Pose"
                    type_short = "M"
                else:
                    # No other formats supported
                    return None
                
                # Reconstruct compressed data from all parts
                compressed_data = ""
                for name in sorted_names:
                    # Handle both __P## and _P## formats
                    if "__P" in name:
                        # V_ID_BC__P##_data format
                        data_part = name.split("__P")[1].split("_", 1)[1]  # Get data after __P##_
                        compressed_data += data_part
                    elif "_P" in name:
                        # Old _P##_ format
                        data_part = name.split("_P")[1].split("_", 1)[1]  # Get data after _P##_
                        compressed_data += data_part
                
            except (ValueError, IndexError) as e:
                return None
        else:
            # No pose keys found
            return None
        
        # Convert type back
        type_map = {"M": "manual", "B": "before_apply_rest", "A": "auto"}
        entry_type = type_map.get(type_short, "manual")
        
        return {
            "id": entry_id,
            "type": entry_type,
            "timestamp": timestamp,
            "bone_count": bone_count,
            "compressed_data": compressed_data
        }
    
    def save_pose_entry(self, entry_data):
        """Save pose entry as shape key name(s)"""
        if not self.metadata_obj:
            print("ERROR: No metadata object available")
            return False
        
        try:
            # Make sure object is active for shape key operations
            bpy.context.view_layer.objects.active = self.metadata_obj
            self.metadata_obj.select_set(True)
            
            # Ensure mesh has shape keys
            if not self.metadata_obj.data.shape_keys:
                basis_key = self.metadata_obj.shape_key_add(name="Basis")
                print(f"Created Basis shape key")
            
            # Create shape key name(s) with embedded data
            shape_key_names = self._create_shape_key_name(entry_data)
            
            print(f"Creating {len(shape_key_names)} shape keys for entry {entry_data.get('id')}")
            
            # Create shape key(s)
            for name in shape_key_names:
                shape_key = self.metadata_obj.shape_key_add(name=name)
                print(f"Created shape key: {name[:50]}...")  # Show first 50 chars
            
            return True
            
        except Exception as e:
            print(f"Error saving pose entry: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_pose_history(self):
        """Load all pose history from shape key names"""
        if not self.metadata_obj or not self.metadata_obj.data.shape_keys:
            return {"version": "2.0", "entries": []}
        
        entries = []
        
        # Group shape keys by entry ID with collision detection
        entry_groups = {}
        id_collision_count = 0
        
        for shape_key in self.metadata_obj.data.shape_keys.key_blocks:
            # Handle both new (V_) and old (VRCAT_) formats
            if not (shape_key.name.startswith("V_") or shape_key.name.startswith("VRCAT_")):
                continue
            
            # Extract entry ID from name based on format
            try:
                if shape_key.name.startswith("V_"):
                    # Sequential format only: V_ID_BC_data or V_ID_BC_P##_data
                    parts = shape_key.name.split("_")
                    if len(parts) >= 2:
                        entry_id = parts[1]  # Sequential number: 1, 2, 3, etc.
                    else:
                        continue
                else:
                    continue  # Only support V_ format now
                    
                if entry_id not in entry_groups:
                    entry_groups[entry_id] = []
                else:
                    # Check if this is a multi-part entry (P01, P02, etc.) or timestamp vs real duplicate
                    is_multipart = "__P" in shape_key.name or "_P" in shape_key.name
                    is_timestamp = "_T_" in shape_key.name
                    if is_multipart or is_timestamp:
                        # This is normal - large pose data split across multiple shape keys or timestamp companion
                        pass
                    else:
                        # Real collision - different entries with same ID
                        id_collision_count += 1
                        print(f"🚨 REAL COLLISION: Entry ID {entry_id} has duplicate entries (not multi-part)")
                        print(f"  Adding: {shape_key.name}")
                entry_groups[entry_id].append(shape_key.name)
            except Exception as e:
                print(f"Error parsing shape key name {shape_key.name}: {e}")
                continue
        
        # Report collision detection results
        if id_collision_count > 0:
            print(f"POSE HISTORY: Found {id_collision_count} entry ID collisions - this may cause inconsistent loading!")
            print(f"POSE HISTORY: Consider refreshing pose history to fix collision issues")
        
        # Parse each entry group - handle multi-part entries correctly
        for entry_id, shape_key_names in entry_groups.items():
            # Multi-part entries are NORMAL - they contain __P01, __P02, etc.
            if len(shape_key_names) > 1:
                print(f"MULTI-PART ENTRY: Entry {entry_id} has {len(shape_key_names)} parts - this is normal for large poses")
                # DON'T discard parts - they're needed to reconstruct the full pose data
            
            metadata = self._parse_shape_key_names(shape_key_names)
            if not metadata:
                continue
            
            # Decompress pose data
            pose_data = self._decompress_pose_data(metadata["compressed_data"])
            if not pose_data:
                continue
            
            # Validate entry data - only skip if truly empty (no filtering by count)
            bone_count = len(pose_data.get("bones", {}))
            if bone_count == 0:  # Only skip if completely empty
                print(f"POSE HISTORY: Skipping entry {entry_id} - no bone data")
                continue
            
            # Create entry
            entry = {
                "id": entry_id,  # Use the sequential ID directly
                "timestamp": metadata["timestamp"],
                "type": metadata["type"],
                "bone_count": bone_count,
                "name": pose_data.get("name", f"Pose #{entry_id}"),
                "bones": pose_data.get("bones", {}),
                "inherit_scale_state": pose_data.get("inherit_scale_state", {})  # Complete inherit_scale state
            }
            
            entries.append(entry)
        
        # Sort by entry ID (sequential: 1, 2, 3, 4...) - Entry #1 first!
        # Make sorting absolutely deterministic by using entry ID as integer
        def sort_key(entry):
            try:
                return int(entry["id"])
            except (ValueError, TypeError):
                return 9999  # Put invalid IDs at the end
        
        entries.sort(key=sort_key)
        
        # Debug: Print final order to verify consistency
        entry_order = [f"#{e['id']}" for e in entries]
        print(f"POSE HISTORY: Final entry order: {entry_order}")
        
        # Return entries in guaranteed sequential order
        result = {"version": "2.0", "entries": entries}
        entry_details = [f"#{e['id']}:{e['name'][:10]}" for e in entries]
        print(f"POSE HISTORY: Returning {len(entries)} entries in order: {entry_details}")
        return result
    
    def delete_pose_entry(self, entry_id):
        """Delete pose history entry by ID""" 
        if not self.metadata_obj or not self.metadata_obj.data.shape_keys:
            return False
        
        # Find and delete all shape keys for this entry
        entry_id_str = entry_id.replace("hist_", "")
        keys_to_delete = []
        
        for shape_key in self.metadata_obj.data.shape_keys.key_blocks:
            if shape_key.name.startswith(f"VRCAT_{entry_id_str}_"):
                keys_to_delete.append(shape_key)
        
        for shape_key in keys_to_delete:
            self.metadata_obj.shape_key_remove(shape_key)
        
        print(f"Deleted {len(keys_to_delete)} shape keys for entry: {entry_id}")
        return len(keys_to_delete) > 0
    
    def cleanup_old_entries(self, max_entries=20):
        """Keep only the most recent entries"""
        history_data = self.load_pose_history()
        entries = history_data.get("entries", [])
        
        if len(entries) <= max_entries:
            return
        
        # Sort by timestamp and keep only the newest
        entries.sort(key=lambda x: x["timestamp"], reverse=True)
        entries_to_delete = entries[max_entries:]
        
        for entry in entries_to_delete:
            self.delete_pose_entry(entry["id"])
        
        print(f"Cleaned up {len(entries_to_delete)} old pose history entries")

# Updated utility functions
def get_metadata_manager(armature):
    """Get metadata manager for armature"""
    return VRCATMetadataStorage(armature)

def has_shape_key_pose_history(armature):
    """Check if armature has shape key pose history by looking for armature modifier links"""
    # Look for objects with armature modifier pointing to this armature
    for obj in bpy.data.objects:
        if "VRCAT_PoseHistory" in obj.name and obj.type == 'MESH':
            # Check if object has armature modifier pointing to our armature
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object == armature:
                    # Quick verification that it has pose data
                    if obj.data and obj.data.shape_keys:
                        for shape_key in obj.data.shape_keys.key_blocks:
                            if (shape_key.name.startswith("V_") or 
                                shape_key.name.startswith("VRCAT_")):
                                return True
    
    return False