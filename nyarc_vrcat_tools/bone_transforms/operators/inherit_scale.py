# Inherit Scale Toggle Operator
# Toggle inherit scale between 'None' and 'Full' for all bones

import bpy
from bpy.types import Operator

# Global warning state cache to avoid property update issues
_inherit_scale_warning_cache = {}


def update_inherit_scale_warning(armature_obj):
    """Check if armature has mixed inherit scale and update warning cache"""
    if not armature_obj:
        return
    
    try:
        # Determine which bone collection to check based on current mode
        bones_to_check = []
        mode_info = ""
        
        # Check if we're in edit mode and have edit_bones available
        if (bpy.context.mode == 'EDIT_ARMATURE' and 
            bpy.context.view_layer.objects.active == armature_obj and 
            hasattr(armature_obj.data, 'edit_bones')):
            # In edit mode, check ALL edit_bones (this is where changes are made)
            bones_to_check = list(armature_obj.data.edit_bones)
            mode_info = "(edit_bones)"
        elif (bpy.context.mode == 'POSE' and 
              bpy.context.view_layer.objects.active == armature_obj and 
              hasattr(armature_obj, 'pose') and armature_obj.pose.bones):
            # In pose mode, inherit_scale is still on data.bones, but we can access via pose.bones.bone
            pose_bones = list(armature_obj.pose.bones)
            bones_to_check = [pose_bone.bone for pose_bone in pose_bones if pose_bone.bone]
            mode_info = "(pose_bones.bone)"
        elif armature_obj.data.bones:
            # In other modes, check ALL data.bones
            bones_to_check = list(armature_obj.data.bones)
            mode_info = "(data.bones)"
        
        if not bones_to_check:
            return
            
        none_count = sum(1 for bone in bones_to_check if hasattr(bone, 'inherit_scale') and bone.inherit_scale == 'NONE')
        full_count = sum(1 for bone in bones_to_check if hasattr(bone, 'inherit_scale') and bone.inherit_scale == 'FULL')
        
        # Update warning cache - show if mixed state detected
        armature_name = armature_obj.name
        has_mixed_state = (none_count > 0 and full_count > 0)
        _inherit_scale_warning_cache[armature_name] = has_mixed_state
        
        # Matrix shearing cascade warning (reduced spam)
        if has_mixed_state and full_count > 0:
            # Only show warning once per session to avoid spam
            if not hasattr(bpy, '_vrcat_shearing_warning_shown'):
                print(f"MATRIX SHEARING WARNING: {armature_name} has {full_count} bones with inherit_scale=FULL")
                print(f"  → These can cause cascading matrix effects during 'Apply as Rest Pose'")
                print(f"  → Use 'Apply as Rest (Flattened)' to prevent pose history rollback issues")
                bpy._vrcat_shearing_warning_shown = True
        
        # DEBUG: Disabled for cleaner console output
        # print(f"DEBUG: Updated warning cache for '{armature_name}' {mode_info}: none={none_count}, full={full_count}, mixed={has_mixed_state}")
        
    except Exception as e:
        print(f"Error updating inherit scale warning: {e}")


def get_inherit_scale_warning(armature_obj):
    """Get warning state for armature from cache"""
    if not armature_obj:
        return False
    
    armature_name = armature_obj.name
    return _inherit_scale_warning_cache.get(armature_name, False)


def update_inherit_scale_warning_from_context():
    """Update warning using current context armature"""
    try:
        scene = bpy.context.scene
        props = getattr(scene, 'nyarc_tools_props', None)
        if props and props.bone_armature_object:
            update_inherit_scale_warning(props.bone_armature_object)
    except Exception as e:
        print(f"Error updating inherit scale warning from context: {e}")

class ARMATURE_OT_toggle_inherit_scale(Operator):
    """Toggle inherit scale for all bones in the armature"""
    bl_idname = "armature.toggle_inherit_scale"
    bl_label = "Toggle Inherit Scale (All Bones)"
    bl_description = "Toggle inherit scale between 'None' and 'Full' for all bones in the armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Store original state
            original_mode = context.mode
            original_active = context.view_layer.objects.active
            original_selected = context.selected_objects[:]
            
            # CRITICAL: Switch to OBJECT mode first before doing selection operations
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select and activate the armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Now switch to edit mode to access bone properties
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Check current state of first bone to determine what to toggle to
            edit_bones = armature.data.edit_bones
            if not edit_bones:
                self.report({'ERROR'}, "No bones found in armature")
                return {'CANCELLED'}
            
            # Check the current state - if most bones have 'NONE', switch to 'FULL', otherwise to 'NONE'
            none_count = sum(1 for bone in edit_bones if bone.inherit_scale == 'NONE')
            total_bones = len(edit_bones)
            
            # If more than half are 'NONE', switch to 'FULL', otherwise switch to 'NONE'
            target_scale = 'FULL' if none_count > total_bones / 2 else 'NONE'
            
            # Apply to all bones
            bones_changed = 0
            for bone in edit_bones:
                if bone.inherit_scale != target_scale:
                    bone.inherit_scale = target_scale
                    bones_changed += 1
            
            self.report({'INFO'}, f"Set inherit scale to '{target_scale}' for {bones_changed} bones")
            
            # Update warning state after changes
            update_inherit_scale_warning(armature)
            
            # Force UI redraw to show updated warning state
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to toggle inherit scale: {str(e)}")
            return {'CANCELLED'}
            
        finally:
            # Restore original state
            try:
                if context.mode != original_mode:
                    if original_mode == 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    elif original_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='POSE')
                
                # Restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    obj.select_set(True)
                context.view_layer.objects.active = original_active
            except:
                pass


class ARMATURE_OT_set_inherit_scale_all_none(Operator):
    """Set inherit scale to None for all bones"""
    bl_idname = "armature.set_inherit_scale_all_none"
    bl_label = "Set All Bones to None"
    bl_description = "Set inherit scale to 'None' for all bones in the armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Store original state
            original_mode = context.mode
            original_active = context.view_layer.objects.active
            original_selected = context.selected_objects[:]
            
            # CRITICAL: Switch to OBJECT mode first before doing selection operations
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select and activate the armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Now switch to edit mode to access bone properties
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Set all bones to NONE
            edit_bones = armature.data.edit_bones
            if not edit_bones:
                self.report({'ERROR'}, "No bones found in armature")
                return {'CANCELLED'}
            
            bones_changed = 0
            for bone in edit_bones:
                if bone.inherit_scale != 'NONE':
                    bone.inherit_scale = 'NONE'
                    bones_changed += 1
            
            self.report({'INFO'}, f"Set inherit scale to 'NONE' for {bones_changed} bones")
            
            # Update warning state after changes
            update_inherit_scale_warning(armature)
            
            # Force UI redraw to show updated warning state
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to set inherit scale: {str(e)}")
            return {'CANCELLED'}
            
        finally:
            # Restore original state
            try:
                if context.mode != original_mode:
                    if original_mode == 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    elif original_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='POSE')
                
                # Restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    obj.select_set(True)
                context.view_layer.objects.active = original_active
            except:
                pass


class ARMATURE_OT_set_inherit_scale_all_full(Operator):
    """Set inherit scale to Full for all bones"""
    bl_idname = "armature.set_inherit_scale_all_full"
    bl_label = "Set All Bones to Full"
    bl_description = "Set inherit scale to 'Full' for all bones in the armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Store original state
            original_mode = context.mode
            original_active = context.view_layer.objects.active
            original_selected = context.selected_objects[:]
            
            # CRITICAL: Switch to OBJECT mode first before doing selection operations
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select and activate the armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Now switch to edit mode to access bone properties
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Set all bones to FULL
            edit_bones = armature.data.edit_bones
            if not edit_bones:
                self.report({'ERROR'}, "No bones found in armature")
                return {'CANCELLED'}
            
            bones_changed = 0
            for bone in edit_bones:
                if bone.inherit_scale != 'FULL':
                    bone.inherit_scale = 'FULL'
                    bones_changed += 1
            
            self.report({'INFO'}, f"Set inherit scale to 'FULL' for {bones_changed} bones")
            
            # Update warning state after changes
            update_inherit_scale_warning(armature)
            
            # Force UI redraw to show updated warning state
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to set inherit scale: {str(e)}")
            return {'CANCELLED'}
            
        finally:
            # Restore original state
            try:
                if context.mode != original_mode:
                    if original_mode == 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    elif original_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='POSE')
                
                # Restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    obj.select_set(True)
                context.view_layer.objects.active = original_active
            except:
                pass


class ARMATURE_OT_set_inherit_scale_selected_none(Operator):
    """Set inherit scale to None for selected bones only"""
    bl_idname = "armature.set_inherit_scale_selected_none"
    bl_label = "Set Selected Bones to None"
    bl_description = "Set inherit scale to 'None' for currently selected bones only"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Store original state
            original_mode = context.mode
            original_active = context.view_layer.objects.active
            original_selected = context.selected_objects[:]
            
            # CRITICAL: Switch to OBJECT mode first before doing selection operations
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select and activate the armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Now switch to edit mode to access bone properties
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Get selected bones only
            edit_bones = armature.data.edit_bones
            selected_bones = [bone for bone in edit_bones if bone.select]
            
            if not selected_bones:
                self.report({'WARNING'}, "No bones selected. Please select bones first.")
                return {'CANCELLED'}
            
            # Set selected bones to NONE
            bones_changed = 0
            for bone in selected_bones:
                if bone.inherit_scale != 'NONE':
                    bone.inherit_scale = 'NONE'
                    bones_changed += 1
            
            self.report({'INFO'}, f"Set inherit scale to 'NONE' for {bones_changed} selected bones")
            
            # Update warning state after changes
            update_inherit_scale_warning(armature)
            
            # Force UI redraw to show updated warning state
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to set inherit scale for selected bones: {str(e)}")
            return {'CANCELLED'}
            
        finally:
            # Restore original state
            try:
                if context.mode != original_mode:
                    if original_mode == 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    elif original_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='POSE')
                
                # Restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    obj.select_set(True)
                context.view_layer.objects.active = original_active
            except:
                pass


class ARMATURE_OT_set_inherit_scale_selected_full(Operator):
    """Set inherit scale to Full for selected bones only"""
    bl_idname = "armature.set_inherit_scale_selected_full"
    bl_label = "Set Selected Bones to Full"
    bl_description = "Set inherit scale to 'Full' for currently selected bones only"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Store original state
            original_mode = context.mode
            original_active = context.view_layer.objects.active
            original_selected = context.selected_objects[:]
            
            # CRITICAL: Switch to OBJECT mode first before doing selection operations
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select and activate the armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Now switch to edit mode to access bone properties
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Get selected bones only
            edit_bones = armature.data.edit_bones
            selected_bones = [bone for bone in edit_bones if bone.select]
            
            if not selected_bones:
                self.report({'WARNING'}, "No bones selected. Please select bones first.")
                return {'CANCELLED'}
            
            # Set selected bones to FULL
            bones_changed = 0
            for bone in selected_bones:
                if bone.inherit_scale != 'FULL':
                    bone.inherit_scale = 'FULL'
                    bones_changed += 1
            
            self.report({'INFO'}, f"Set inherit scale to 'FULL' for {bones_changed} selected bones")
            
            # Update warning state after changes
            update_inherit_scale_warning(armature)
            
            # Force UI redraw to show updated warning state
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to set inherit scale for selected bones: {str(e)}")
            return {'CANCELLED'}
            
        finally:
            # Restore original state
            try:
                if context.mode != original_mode:
                    if original_mode == 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    elif original_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='POSE')
                
                # Restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    obj.select_set(True)
                context.view_layer.objects.active = original_active
            except:
                pass


class ARMATURE_OT_toggle_inherit_scale_selected(Operator):
    """Toggle inherit scale for selected bones only (DEPRECATED - kept for compatibility)"""
    bl_idname = "armature.toggle_inherit_scale_selected"
    bl_label = "Toggle Inherit Scale (Selected Bones)"
    bl_description = "Toggle inherit scale between 'None' and 'Full' for currently selected bones only"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Store original state
            original_mode = context.mode
            original_active = context.view_layer.objects.active
            original_selected = context.selected_objects[:]
            
            # CRITICAL: Switch to OBJECT mode first before doing selection operations
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select and activate the armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Now switch to edit mode to access bone properties
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Get selected bones only
            edit_bones = armature.data.edit_bones
            selected_bones = [bone for bone in edit_bones if bone.select]
            
            if not selected_bones:
                self.report({'WARNING'}, "No bones selected. Please select bones first.")
                return {'CANCELLED'}
            
            # Check the current state of selected bones - if most have 'NONE', switch to 'FULL', otherwise to 'NONE'
            none_count = sum(1 for bone in selected_bones if bone.inherit_scale == 'NONE')
            total_selected = len(selected_bones)
            
            # If more than half are 'NONE', switch to 'FULL', otherwise switch to 'NONE'
            target_scale = 'FULL' if none_count > total_selected / 2 else 'NONE'
            
            # Apply to selected bones only
            bones_changed = 0
            for bone in selected_bones:
                if bone.inherit_scale != target_scale:
                    bone.inherit_scale = target_scale
                    bones_changed += 1
            
            self.report({'INFO'}, f"Set inherit scale to '{target_scale}' for {bones_changed} selected bones")
            
            # Update warning state after changes
            update_inherit_scale_warning(armature)
            
            # Force UI redraw to show updated warning state
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to toggle inherit scale for selected bones: {str(e)}")
            return {'CANCELLED'}
            
        finally:
            # Restore original state
            try:
                if context.mode != original_mode:
                    if original_mode == 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    elif original_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='POSE')
                
                # Restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    obj.select_set(True)
                context.view_layer.objects.active = original_active
            except:
                pass


# Registration
INHERIT_SCALE_CLASSES = (
    ARMATURE_OT_toggle_inherit_scale,
    ARMATURE_OT_set_inherit_scale_all_none,
    ARMATURE_OT_set_inherit_scale_all_full,
    ARMATURE_OT_set_inherit_scale_selected_none,
    ARMATURE_OT_set_inherit_scale_selected_full,
    ARMATURE_OT_toggle_inherit_scale_selected,  # Keep for compatibility
)

# Keep compatibility alias
classes = INHERIT_SCALE_CLASSES

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass