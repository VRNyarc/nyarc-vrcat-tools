# Migration System for Pose History
# Converts custom property storage to shape key metadata storage

import bpy
import json
from .metadata_storage import VRCATMetadataStorage

def migrate_armature_pose_history(armature):
    """Migrate armature from custom property to shape key storage"""
    
    # Check if armature has old custom property data
    if "nyarc_pose_history" not in armature:
        return False, "No custom property pose history found"
    
    try:
        # Load existing data
        old_data = json.loads(armature["nyarc_pose_history"])
        entries = old_data.get("entries", [])
        
        if not entries:
            return False, "No pose history entries found"
        
        # Create metadata manager
        metadata_manager = VRCATMetadataStorage(armature)
        
        # Migrate each entry
        migrated_count = 0
        for entry in entries:
            # Prepare entry data for new system
            entry_data = {
                "name": entry.get("name", "Migrated Entry"),
                "bones": entry.get("bones", {})
            }
            
            success = metadata_manager.save_pose_entry(entry)
            if success:
                migrated_count += 1
            else:
                print(f"Failed to migrate entry: {entry.get('name', 'Unknown')}")
        
        # Create backup of old data
        armature["nyarc_pose_history_backup"] = armature["nyarc_pose_history"]
        
        # Remove old custom property (commented out for safety during testing)
        # del armature["nyarc_pose_history"]
        
        print(f"Migrated {migrated_count}/{len(entries)} pose history entries for {armature.name}")
        return True, f"Successfully migrated {migrated_count} entries"
        
    except Exception as e:
        error_msg = f"Migration failed: {e}"
        print(error_msg)
        return False, error_msg

def migrate_all_armatures():
    """Migrate all armatures in current scene"""
    migrated_armatures = []
    failed_armatures = []
    
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and "nyarc_pose_history" in obj:
            success, message = migrate_armature_pose_history(obj)
            if success:
                migrated_armatures.append(obj.name)
            else:
                failed_armatures.append((obj.name, message))
    
    print(f"Migration complete: {len(migrated_armatures)} successful, {len(failed_armatures)} failed")
    return migrated_armatures, failed_armatures

def check_migration_needed():
    """Check if any armatures need migration"""
    needs_migration = []
    
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and "nyarc_pose_history" in obj:
            # Check if already has new system
            metadata_name = f"{obj.name}_VRCAT_PoseHistory"
            if metadata_name not in bpy.data.objects:
                needs_migration.append(obj.name)
    
    return needs_migration

def auto_migrate_on_load():
    """Automatically migrate pose history when addon loads"""
    needs_migration = check_migration_needed()
    
    if needs_migration:
        print(f"Auto-migrating {len(needs_migration)} armatures to new pose history system...")
        migrated, failed = migrate_all_armatures()
        
        if migrated:
            print(f"Successfully migrated: {', '.join(migrated)}")
        if failed:
            print(f"Failed to migrate: {', '.join([f[0] for f in failed])}")
        
        return len(migrated), len(failed)
    
    return 0, 0