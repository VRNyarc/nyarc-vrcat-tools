# Pose History Operators
# Blender operators for pose history functionality

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import json
import os
from mathutils import Vector, Quaternion

# Import pose history functions from main __init__.py
try:
    from . import revert_to_pose_history_entry, save_pose_history_snapshot, get_pose_history
    POSE_FUNCTIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import pose history functions: {e}")
    POSE_FUNCTIONS_AVAILABLE = False


class ARMATURE_OT_revert_pose_history(Operator):
    """Revert to a pose history entry (clears current pose and applies saved state)"""
    bl_idname = "armature.revert_pose_history"
    bl_label = "Revert to Pose History"
    bl_description = "Clear current pose and revert to saved pose history state"
    bl_options = {'REGISTER', 'UNDO'}
    
    entry_id: StringProperty(name="Entry ID")
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        success, message = revert_to_pose_history_entry(context, armature, self.entry_id)
        
        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


# Manual save operator removed - pose history only works with Apply Rest Pose
# This ensures proper revert-to-original functionality


class ARMATURE_OT_pose_history_education_popup(Operator):
    """Show educational popup about pose history system"""
    bl_idname = "armature.pose_history_education_popup"
    bl_label = "About Pose History"
    bl_description = "Learn about the pose history system"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.scale_y = 1.2
        
        # Title
        title_row = col.row()
        title_row.alignment = 'CENTER'
        title_row.label(text="Pose History System Enabled", icon='INFO')
        
        col.separator()
        
        # Information sections
        info_box = col.box()
        info_col = info_box.column()
        info_col.scale_y = 0.9
        
        info_col.label(text="What happens when enabled:", icon='DISCLOSURE_TRI_RIGHT')
        info_col.label(text="• Auto-saves pose state before each 'Apply as Rest Pose' operation")
        info_col.label(text="• Creates hidden metadata object: [ArmatureName]_VRCAT_PoseHistory")  
        info_col.label(text="• Enables 'Load Original Pose' and pose revert functionality")
        info_col.label(text="• Works seamlessly with your existing workflow")
        
        col.separator()
        
        tech_box = col.box()
        tech_col = tech_box.column()
        tech_col.scale_y = 0.9
        
        tech_col.label(text="Technical details:", icon='DISCLOSURE_TRI_RIGHT')
        tech_col.label(text="• Non-destructive: Doesn't modify your armature or mesh data")
        tech_col.label(text="• Storage: Uses hidden shape keys for maximum compatibility")
        tech_col.label(text="• File size: Minimal increase (~1-5KB per pose state)")
        tech_col.label(text="• Unity safe: Hidden objects maintain proper spatial behavior")
        
        col.separator()
        
        # Confirmation
        confirm_row = col.row()
        confirm_row.alignment = 'CENTER'
        confirm_row.label(text="You can disable this anytime in the Pose History section", icon='CHECKMARK')


class ARMATURE_OT_pose_history_disable_warning(Operator):
    """Show warning when disabling pose history with existing data"""
    bl_idname = "armature.pose_history_disable_warning"
    bl_label = "Pose History Disabled - Important Warning"
    bl_description = "Warning about disabling pose history with existing data"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=550)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.scale_y = 1.2
        
        # Warning title
        title_row = col.row()
        title_row.alignment = 'CENTER'
        title_row.alert = True
        title_row.label(text="⚠ Pose History Disabled - Critical Warning", icon='ERROR')
        
        col.separator()
        
        # Main warning
        warning_box = col.box()
        warning_col = warning_box.column()
        warning_col.scale_y = 0.9
        warning_col.alert = True
        
        warning_col.label(text="You have disabled pose history, but existing history data was found.", icon='CANCEL')
        warning_col.label(text="", icon='BLANK1')  # Spacing
        warning_col.label(text="CRITICAL: If you 'Apply as Rest Pose' again without re-enabling", icon='ERROR')
        warning_col.label(text="pose history, you will PERMANENTLY LOSE the ability to revert", icon='ERROR')
        warning_col.label(text="to your original pose states.", icon='ERROR')
        
        col.separator()
        
        # Solutions
        solution_box = col.box()
        solution_col = solution_box.column()
        solution_col.scale_y = 0.9
        
        solution_col.label(text="Recommended actions:", icon='LIGHT_SUN')
        solution_col.label(text="• Re-enable pose history checkbox to continue safe workflow")
        solution_col.label(text="• OR: Export current history entries as presets first")
        solution_col.label(text="• OR: Use 'Load Original Pose' to revert before final Apply Rest Pose")
        
        col.separator()
        
        # Understanding
        understand_box = col.box()
        understand_col = understand_box.column()
        understand_col.scale_y = 0.8
        
        understand_col.label(text="Why this matters:", icon='INFO')
        understand_col.label(text="Pose history only captures poses BEFORE 'Apply as Rest Pose' operations.")
        understand_col.label(text="Without history enabled, the next Apply Rest Pose will create no snapshot,")
        understand_col.label(text="making it impossible to revert to any previous pose states.")


class ARMATURE_OT_refresh_pose_history_ui(Operator):
    """Refresh pose history UI display"""
    bl_idname = "armature.refresh_pose_history_ui"
    bl_label = "Refresh Pose History"
    bl_description = "Force refresh the pose history UI display"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()
        
        # Force scene update
        context.view_layer.update()
        
        self.report({'INFO'}, "Pose history UI refreshed")
        return {'FINISHED'}


class ARMATURE_OT_disable_and_delete_pose_history(Operator):
    """Disable pose history and delete all stored data"""
    bl_idname = "armature.disable_and_delete_pose_history"
    bl_label = "Disable & Delete All Pose History"
    bl_description = "Turn off pose history and permanently delete all stored entries and metadata"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Step 1: Disable pose history
            props.pose_history_enabled = False
            
            # Step 2: Delete metadata object and all history data
            metadata_obj_name = f"{armature.name}_VRCAT_PoseHistory"
            metadata_obj = bpy.data.objects.get(metadata_obj_name)
            
            if metadata_obj:
                # Remove from collections first
                for collection in metadata_obj.users_collection:
                    collection.objects.unlink(metadata_obj)
                
                # Remove mesh data
                if metadata_obj.data:
                    mesh_data = metadata_obj.data
                    bpy.data.objects.remove(metadata_obj)
                    bpy.data.meshes.remove(mesh_data)
                else:
                    bpy.data.objects.remove(metadata_obj)
                
                self.report({'INFO'}, f"Pose history disabled and all data deleted for '{armature.name}'")
                print(f"POSE HISTORY: Disabled and deleted all data for armature '{armature.name}'")
            else:
                # Just disable if no metadata found
                self.report({'INFO'}, f"Pose history disabled for '{armature.name}' (no stored data found)")
                print(f"POSE HISTORY: Disabled for armature '{armature.name}' (no existing data)")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to disable and delete pose history: {str(e)}")
            print(f"POSE HISTORY ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Show confirmation dialog
        return context.window_manager.invoke_confirm(self, event)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.alert = True
        col.label(text="⚠ This will permanently delete all pose history!", icon='ERROR')
        col.separator()
        col.label(text="• Disables pose history system")
        col.label(text="• Removes all stored pose entries")
        col.label(text="• Deletes metadata object")
        col.separator()
        col.label(text="This action cannot be undone!", icon='CANCEL')


class ARMATURE_OT_export_pose_history_to_preset(Operator):
    """Export a pose history entry as a regular preset for use on other models"""
    bl_idname = "armature.export_pose_history_to_preset"
    bl_label = "Save Preset: Historical to Current Rest Pose"
    bl_description = "Creates a preset that transforms from this historical pose state back to the current rest pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    entry_id: StringProperty(name="Entry ID")
    preset_name: StringProperty(
        name="Preset Name",
        description="Name for the exported preset",
        default="History Export"
    )
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Get the history entry
            history_data = get_pose_history(armature)
            target_entry = None
            
            for entry in history_data["entries"]:
                if entry["id"] == self.entry_id:
                    target_entry = entry
                    break
            
            if not target_entry:
                self.report({'ERROR'}, f"History entry {self.entry_id} not found")
                return {'CANCELLED'}
            
            # Use CUMULATIVE LOADING logic like the Load button to get all changes up to this point
            # Find all entries from target forward (including target)
            sorted_entries = sorted(history_data["entries"], key=lambda x: x["timestamp"])
            target_index = -1
            
            for i, entry in enumerate(sorted_entries):
                if entry["id"] == self.entry_id:
                    target_index = i
                    break
            
            if target_index == -1:
                self.report({'ERROR'}, "Could not find entry in sorted list")
                return {'CANCELLED'}
            
            entries_to_apply = sorted_entries[target_index:]
            entries_to_apply.reverse()  # Newest first for cumulative math
            
            print(f"PRESET EXPORT: Computing cumulative transforms from {len(entries_to_apply)} entries")
            
            # Calculate cumulative transforms for all bones (like the Load button does)
            all_bone_names = set()
            for entry in entries_to_apply:
                all_bone_names.update(entry["bones"].keys())
            
            preset_data = {}
            bones_converted = 0
            bones_skipped_identity = 0
            
            for bone_name in all_bone_names:
                # Start with identity transforms
                cumulative_location = Vector((0.0, 0.0, 0.0))
                cumulative_rotation = Quaternion((1.0, 0.0, 0.0, 0.0))
                cumulative_scale = Vector((1.0, 1.0, 1.0))
                final_inherit_scale = 'FULL'
                
                # Apply each entry's inverse transform for this bone (newest first)
                for entry in entries_to_apply:
                    if bone_name in entry["bones"]:
                        bone_data = entry["bones"][bone_name]
                        
                        if all(key in bone_data for key in ['location', 'rotation_quaternion', 'scale']):
                            # Get inverse transforms from this entry
                            inv_location = Vector(bone_data['location'])
                            inv_rotation = Quaternion(bone_data['rotation_quaternion'])
                            inv_scale = Vector(bone_data['scale'])
                            
                            # CUMULATIVE MATH (same as Load button):
                            # Location: Add inverse locations
                            cumulative_location += inv_location
                            
                            # Rotation: Multiply quaternions (newest first)
                            cumulative_rotation = inv_rotation @ cumulative_rotation
                            
                            # Scale: Multiply scales component-wise
                            cumulative_scale.x *= inv_scale.x
                            cumulative_scale.y *= inv_scale.y
                            cumulative_scale.z *= inv_scale.z
                            
                            # Use inherit_scale NONE for flattening (same as Apply as Rest Pose)
                            if entry == target_entry:
                                final_inherit_scale = 'NONE'  # Force NONE for proper flattening like Apply as Rest Pose
                
                # Now we have the cumulative inverse transforms
                # DOUBLE-INVERT to get the final pose transforms:
                # Location: negate the cumulative inverse
                final_location = [-cumulative_location.x, -cumulative_location.y, -cumulative_location.z]
                
                # Rotation: invert the cumulative inverse quaternion
                final_rotation = cumulative_rotation.inverted()
                final_rotation_list = [final_rotation.w, final_rotation.x, final_rotation.y, final_rotation.z]
                
                # Scale: divide 1.0 by cumulative inverse scale
                final_scale = [
                    1.0 / cumulative_scale.x if abs(cumulative_scale.x) > 0.0001 else 1.0,
                    1.0 / cumulative_scale.y if abs(cumulative_scale.y) > 0.0001 else 1.0,
                    1.0 / cumulative_scale.z if abs(cumulative_scale.z) > 0.0001 else 1.0
                ]
                
                # ONLY save bones with non-identity final transforms (optimization)
                has_location_change = (abs(final_location[0]) > 0.0001 or abs(final_location[1]) > 0.0001 or abs(final_location[2]) > 0.0001)
                has_rotation_change = not (abs(final_rotation.w - 1.0) < 0.0001 and abs(final_rotation.x) < 0.0001 and abs(final_rotation.y) < 0.0001 and abs(final_rotation.z) < 0.0001)
                has_scale_change = not (abs(final_scale[0] - 1.0) < 0.0001 and abs(final_scale[1] - 1.0) < 0.0001 and abs(final_scale[2] - 1.0) < 0.0001)
                
                if has_location_change or has_rotation_change or has_scale_change:
                    # Save as regular preset format
                    preset_data[bone_name] = {
                        'location': final_location,
                        'rotation_quaternion': final_rotation_list,
                        'scale': final_scale,
                        'inherit_scale': final_inherit_scale
                    }
                    bones_converted += 1
                else:
                    bones_skipped_identity += 1
            
            print(f"PRESET EXPORT: Saved {bones_converted} bones with changes, skipped {bones_skipped_identity} identity bones")
            
            # Save to preset file
            presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
            os.makedirs(presets_dir, exist_ok=True)
            
            preset_file = os.path.join(presets_dir, f"{self.preset_name}.json")
            
            # Add metadata
            full_preset_data = {
                "name": self.preset_name,
                "created_from": "pose_history",
                "source_entry": target_entry["name"],
                "bone_count": bones_converted,
                "bones": preset_data
            }
            
            with open(preset_file, 'w') as f:
                json.dump(full_preset_data, f, indent=2)
            
            self.report({'INFO'}, f"Exported history '{target_entry['name']}' as preset '{self.preset_name}' ({bones_converted} bones)")
            print(f"PRESET EXPORT: Converted {bones_converted} bones from history to preset")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export preset: {str(e)}")
            print(f"PRESET EXPORT ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Show dialog to enter preset name
        return context.window_manager.invoke_props_dialog(self)


# Registration classes - only if functions are available
if POSE_FUNCTIONS_AVAILABLE:
    classes = (
        ARMATURE_OT_revert_pose_history,
        ARMATURE_OT_pose_history_education_popup,
        ARMATURE_OT_pose_history_disable_warning,
        ARMATURE_OT_refresh_pose_history_ui,
        ARMATURE_OT_export_pose_history_to_preset,
        ARMATURE_OT_disable_and_delete_pose_history,
    )
else:
    classes = (
        ARMATURE_OT_pose_history_education_popup,  # Always available
        ARMATURE_OT_pose_history_disable_warning,  # Always available
        ARMATURE_OT_refresh_pose_history_ui,  # Always available
        ARMATURE_OT_disable_and_delete_pose_history,  # Always available
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass