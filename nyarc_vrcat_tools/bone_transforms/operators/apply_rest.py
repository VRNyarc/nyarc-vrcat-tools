# Bone Apply Rest Pose Module
# Contains the apply as rest pose operator extracted from bone_transform_saver.py

import bpy
from bpy.types import Operator

# Import pose history system
try:
    from ..pose_history import save_pose_history_snapshot
    POSE_HISTORY_AVAILABLE = True
except ImportError:
    POSE_HISTORY_AVAILABLE = False
    print("Warning: pose_history not available for apply rest pose")

# Import modularized calculations (HARD DEPENDENCY)
from ..diff_export.transforms_diff import (
    apply_armature_to_mesh_with_no_shape_keys,
    apply_armature_to_mesh_with_shape_keys
)

# Import inherit scale functions  
try:
    from .inherit_scale import update_inherit_scale_warning
    INHERIT_SCALE_AVAILABLE = True
except ImportError:
    INHERIT_SCALE_AVAILABLE = False
    print("Warning: inherit_scale module not available for apply rest pose")

# Import flattening system for inheritance cascade prevention
try:
    from ..utils.inheritance_flattening import (
        get_bones_requiring_flatten_context,
        flatten_bone_transforms_for_save
    )
    FLATTENING_AVAILABLE = True
except ImportError:
    FLATTENING_AVAILABLE = False
    print("Warning: inheritance_flattening not available for apply rest pose")


def check_all_bones_inherit_scale_none(armature_obj):
    """Check if all bones in the armature have inherit_scale set to 'NONE'"""
    if not armature_obj or not armature_obj.data.bones:
        return True, 0, 0  # No bones, consider as all none
    
    # inherit_scale is stored on edit_bones, need to temporarily switch to edit mode
    current_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    
    try:
        # Ensure we're looking at the right object and switch to edit mode
        if bpy.context.object != armature_obj:
            bpy.context.view_layer.objects.active = armature_obj
        
        if current_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        edit_bones = armature_obj.data.edit_bones
        none_count = sum(1 for bone in edit_bones if bone.inherit_scale == 'NONE')
        total_bones = len(edit_bones)
        
        all_none = (none_count == total_bones)
        
        # Switch back to original mode
        if current_mode != 'EDIT':
            if current_mode == 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            elif current_mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
                
        return all_none, none_count, total_bones
        
    except Exception as e:
        print(f"Error checking inherit_scale: {e}")
        # Switch back to original mode on error
        try:
            if current_mode == 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            elif current_mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        
        # Fallback - assume not all none to be safe
        return False, 0, len(armature_obj.data.bones) if armature_obj.data.bones else 0


def save_inherit_scale_settings(armature_obj):
    """Save current inherit_scale settings for all bones"""
    if not armature_obj or not armature_obj.data.bones:
        return {}
    
    settings = {}
    # Must read from edit_bones to get inherit_scale
    original_mode = bpy.context.mode
    
    # Ensure armature is active
    bpy.context.view_layer.objects.active = armature_obj
    bpy.context.view_layer.update()
    
    # Switch to edit mode to read inherit_scale settings
    if bpy.context.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    for edit_bone in armature_obj.data.edit_bones:
        settings[edit_bone.name] = edit_bone.inherit_scale
    
    # Restore original mode
    if original_mode == 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    elif original_mode == 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    return settings


def set_all_bones_inherit_scale_none(armature_obj):
    """Set all bones inherit_scale to 'NONE'"""
    if not armature_obj or not armature_obj.data.bones:
        return False
    
    try:
        # Store current mode
        original_mode = bpy.context.mode
        
        # Ensure armature is active
        if bpy.context.object != armature_obj:
            bpy.context.view_layer.objects.active = armature_obj
        
        # Switch to edit mode to modify inherit_scale
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Set all bones to inherit_scale = 'NONE'
        bones_changed = 0
        for edit_bone in armature_obj.data.edit_bones:
            if edit_bone.inherit_scale != 'NONE':
                edit_bone.inherit_scale = 'NONE'
                bones_changed += 1
        
        # Restore original mode
        if original_mode == 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        elif original_mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"Set {bones_changed} bones to inherit_scale=NONE")
        return True
        
    except Exception as e:
        print(f"Error setting bones to inherit_scale=NONE: {e}")
        # Try to restore original mode on error
        try:
            if original_mode == 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            elif original_mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        return False


def restore_inherit_scale_settings(armature_obj, saved_settings):
    """Restore inherit_scale settings for all bones"""
    if not armature_obj or not saved_settings:
        return
    
    original_mode = bpy.context.mode
    
    # Ensure armature is active
    bpy.context.view_layer.objects.active = armature_obj
    bpy.context.view_layer.update()
    
    # Switch to edit mode to modify inherit_scale settings
    if bpy.context.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    restored_count = 0
    for edit_bone in armature_obj.data.edit_bones:
        if edit_bone.name in saved_settings:
            edit_bone.inherit_scale = saved_settings[edit_bone.name]
            restored_count += 1
    
    # Restore original mode
    if original_mode == 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    elif original_mode == 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Restored inherit_scale settings for {restored_count} bones")


def apply_flattened_transforms_to_pose(armature_obj, flattened_data):
    """Apply flattened transform data to pose bones"""
    if not armature_obj or not flattened_data:
        return
    
    # Ensure armature is active and we're in pose mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.context.view_layer.update()
    
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    
    applied_count = 0
    for bone_name, transform_data in flattened_data.items():
        if bone_name in armature_obj.pose.bones:
            pose_bone = armature_obj.pose.bones[bone_name]
            
            # Apply flattened transforms
            pose_bone.location = transform_data['location']
            pose_bone.rotation_quaternion = transform_data['rotation_quaternion']  
            pose_bone.scale = transform_data['scale']
            applied_count += 1
    
    print(f"Applied flattened transforms to {applied_count} pose bones")


def execute_apply_rest_pose_core(context, armature, operator_self, skip_inherit_check=False):
    """Core apply rest pose logic that can be called by any operator"""
    
    # Get props at the beginning of the method to avoid scope issues
    props = getattr(context.scene, 'nyarc_tools_props', None)
    
    try:
        # Ensure armature is selected and active and in pose mode
        if context.object != armature:
            # Switch to object mode first
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Select the armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
        
        # Ensure we're in pose mode
        if context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        # AUTO-SAVE POSE HISTORY: Save current pose before applying as rest pose (IF ENABLED)
        if POSE_HISTORY_AVAILABLE and props and props.pose_history_enabled:
            snapshot_name = f"Before Apply Rest Pose - {armature.name}"
            success = save_pose_history_snapshot(armature, snapshot_name, "before_apply_rest")
            if success:
                print(f"Pose History: Auto-saved snapshot before apply rest pose")
                operator_self.report({'INFO'}, "Pose history auto-saved before applying rest pose")
            else:
                print(f"Pose History: Failed to auto-save snapshot")
        elif POSE_HISTORY_AVAILABLE and props and not props.pose_history_enabled:
            print("Pose History: Auto-save skipped (user disabled pose history)")
        else:
            print("Pose History: Auto-save not available (module not loaded)")
        
        # Get all meshes with armature modifiers pointing to this armature
        mesh_objects = []
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                any(mod.type == 'ARMATURE' and mod.object == armature for mod in obj.modifiers)):
                mesh_objects.append(obj)
        
        print(f"Found {len(mesh_objects)} meshes with armature modifiers: {[obj.name for obj in mesh_objects]}")
        
        # CRITICAL: Switch to OBJECT mode before processing meshes
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Process each mesh to apply armature deformation to shape keys
        for mesh_obj in mesh_objects:
            print(f"Processing mesh: {mesh_obj.name}")
            print(f"Has shape keys: {mesh_obj.data.shape_keys is not None}")
            if mesh_obj.data.shape_keys:
                print(f"Shape key count: {len(mesh_obj.data.shape_keys.key_blocks)}")
            if mesh_obj.data.shape_keys and mesh_obj.data.shape_keys.key_blocks:
                # The mesh has shape keys - use CATS method
                if len(mesh_obj.data.shape_keys.key_blocks) == 1:
                    # Only has basis shape key - remove it first, apply modifier, then re-add
                    print("Mesh has only basis shape key - removing temporarily")
                    basis_name = mesh_obj.data.shape_keys.key_blocks[0].name
                    
                    # Make mesh active for shape key operations
                    bpy.ops.object.select_all(action='DESELECT')
                    mesh_obj.select_set(True)
                    bpy.context.view_layer.objects.active = mesh_obj
                    
                    mesh_obj.shape_key_remove(mesh_obj.data.shape_keys.key_blocks[0])
                    print(f"Removed basis shape key: {basis_name}")
                    
                    apply_armature_to_mesh_with_no_shape_keys(armature, mesh_obj)
                    
                    # Re-add the basis shape key
                    mesh_obj.shape_key_add(name=basis_name)
                    print(f"Re-added basis shape key: {basis_name}")
                else:
                    # Multiple shape keys - complex case
                    apply_armature_to_mesh_with_shape_keys(armature, mesh_obj)
            else:
                # No shape keys - simple case
                apply_armature_to_mesh_with_no_shape_keys(armature, mesh_obj)
        
        # Switch back to pose mode and apply the pose as the new rest pose  
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)
        
        # AUTOMATIC POSE MODE STOP: Since pose has been applied permanently, stop pose mode
        print("Pose applied as rest pose - automatically stopping pose mode")
        
        # Clear all pose transforms (they're now baked into rest pose)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        
        # Set armature back to REST position to show the new rest pose
        armature.data.pose_position = 'REST'
        
        # Switch to object mode to exit pose mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Update the props to reflect that pose mode is no longer active
        if props:
            props.bone_editing_active = False
            print("Updated bone_editing_active to False")
        
        # Force UI update
        context.view_layer.update()
        
        operator_self.report({'INFO'}, f"Applied pose as rest pose for {armature.name} and stopped pose mode")
        return {'FINISHED'}
        
    except Exception as e:
        operator_self.report({'ERROR'}, f"Failed to apply as rest pose: {str(e)}")
        return {'CANCELLED'}


def execute_flattened_apply_rest_pose(context, armature, operator_self=None):
    """
    Shared function to execute flattened apply rest pose logic.
    Can be called from any operator.
    """
    try:
        print("=== APPLY REST POSE WITH FLATTENING ===")
        
        # Get props  
        props = getattr(context.scene, 'nyarc_tools_props', None)
        
        # Ensure armature is selected and active using direct selection
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        armature.select_set(True)
        context.view_layer.objects.active = armature
        
        # Force update to ensure context is correct
        context.view_layer.update()
        
        # Ensure we're in object mode first, then switch to pose mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
            
        # Now switch to pose mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # AUTO-SAVE POSE HISTORY before flattening
        if POSE_HISTORY_AVAILABLE and props and props.pose_history_enabled:
            snapshot_name = f"Before Flattened Apply Rest - {armature.name}"
            success = save_pose_history_snapshot(armature, snapshot_name, "before_flattened_apply_rest")
            if success:
                print(f"Pose History: Auto-saved snapshot before flattened apply rest")
                if operator_self:
                    operator_self.report({'INFO'}, "Pose history auto-saved before applying rest pose")

        # STEP 1: Save original inherit_scale settings
        print("STEP 1: Saving original inherit_scale settings...")
        original_inherit_settings = save_inherit_scale_settings(armature)
        print(f"Saved inherit_scale settings for {len(original_inherit_settings)} bones")
        
        # STEP 2: Identify bones that need transforms
        print("STEP 2: Identifying bones with pose transforms...")
        target_bones = set()
        statistical_bones = set()
        
        for pose_bone in armature.pose.bones:
            location = pose_bone.location
            rotation = pose_bone.rotation_quaternion  
            scale = pose_bone.scale
            
            has_location = (abs(location.x) > 0.0001 or abs(location.y) > 0.0001 or abs(location.z) > 0.0001)
            has_rotation = not (abs(rotation.w - 1.0) < 0.0001 and abs(rotation.x) < 0.0001 and abs(rotation.y) < 0.0001 and abs(rotation.z) < 0.0001)
            has_scale = not (abs(scale.x - 1.0) < 0.0001 and abs(scale.y - 1.0) < 0.0001 and abs(scale.z - 1.0) < 0.0001)
            
            if has_location or has_rotation or has_scale:
                target_bones.add(pose_bone.name)
                if has_scale:  # Scale changes are the source of inheritance cascades
                    statistical_bones.add(pose_bone.name)
        
        print(f"Found {len(target_bones)} bones with transforms ({len(statistical_bones)} with scale changes)")
        
        if not target_bones:
            print("No transforms to apply - skipping flattening")
            if operator_self:
                operator_self.report({'INFO'}, "No pose transforms found to apply")
            return {'FINISHED'}
        
        # STEP 3: Calculate flattened transforms
        print("STEP 3: Calculating flattened transforms...")
        flattened_data = flatten_bone_transforms_for_save(armature, target_bones, statistical_bones)
        
        if not flattened_data:
            if operator_self:
                operator_self.report({'ERROR'}, "Failed to calculate flattened transforms")
            return {'CANCELLED'}
        
        print(f"Calculated flattened transforms for {len(flattened_data)} bones")
        
        # STEP 4: Set all bones to inherit_scale=NONE temporarily  
        print("STEP 4: Setting all bones to inherit_scale=NONE temporarily...")
        # Set inherit_scale manually instead of using operator
        if context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        for edit_bone in armature.data.edit_bones:
            edit_bone.inherit_scale = 'NONE'
            
        # Switch back to pose mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # STEP 5: Apply flattened transforms to pose
        print("STEP 5: Applying flattened transforms to pose...")
        apply_flattened_transforms_to_pose(armature, flattened_data)
        
        # STEP 6: Apply pose as rest pose (same logic as original)
        print("STEP 6: Applying pose as rest pose...")
        
        # Process meshes first
        mesh_objects = []
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                any(mod.type == 'ARMATURE' and mod.object == armature for mod in obj.modifiers)):
                mesh_objects.append(obj)
        
        print(f"Processing {len(mesh_objects)} meshes with armature modifiers")
        
        # Switch to object mode for mesh processing
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Process meshes (same logic as original)
        for mesh_obj in mesh_objects:
            if mesh_obj.data.shape_keys and mesh_obj.data.shape_keys.key_blocks:
                if len(mesh_obj.data.shape_keys.key_blocks) == 1:
                    # Only basis shape key
                    for obj in bpy.context.selected_objects:
                        obj.select_set(False)
                    mesh_obj.select_set(True)
                    context.view_layer.objects.active = mesh_obj
                    
                    basis_name = mesh_obj.data.shape_keys.key_blocks[0].name
                    mesh_obj.shape_key_remove(mesh_obj.data.shape_keys.key_blocks[0])
                    apply_armature_to_mesh_with_no_shape_keys(armature, mesh_obj)
                    mesh_obj.shape_key_add(name=basis_name)
                else:
                    # Multiple shape keys
                    apply_armature_to_mesh_with_shape_keys(armature, mesh_obj)
            else:
                # No shape keys
                apply_armature_to_mesh_with_no_shape_keys(armature, mesh_obj)
        
        # Switch back to pose mode and apply pose as rest
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        armature.select_set(True)
        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Select all pose bones using direct API
        for pose_bone in armature.pose.bones:
            pose_bone.bone.select = True
        
        bpy.ops.pose.armature_apply(selected=False)
        
        # Clear transforms and set to rest position
        # Clear transforms using direct API instead of operator
        for pose_bone in armature.pose.bones:
            pose_bone.location = (0, 0, 0)
            pose_bone.rotation_quaternion = (1, 0, 0, 0)
            pose_bone.scale = (1, 1, 1)
        
        armature.data.pose_position = 'REST'
        
        print("Applied pose as rest pose successfully (no cascading matrix effects)")
        
        # STEP 7: Restore original inherit_scale settings
        print("STEP 7: Restoring original inherit_scale settings...")
        restore_inherit_scale_settings(armature, original_inherit_settings)
        
        # Switch to object mode and update props
        bpy.ops.object.mode_set(mode='OBJECT')
        if props:
            props.bone_editing_active = False
        
        context.view_layer.update()
        
        print("=== FLATTENED APPLY REST POSE COMPLETED ===")
        if operator_self:
            operator_self.report({'INFO'}, f"Applied pose as rest with flattening - no matrix shearing cascades!")
        return {'FINISHED'}
        
    except Exception as e:
        print(f"ERROR in flattened apply rest pose: {str(e)}")
        # Try to restore inherit_scale settings even if something failed
        try:
            if 'original_inherit_settings' in locals():
                restore_inherit_scale_settings(armature, original_inherit_settings)
                print("Restored inherit_scale settings after error")
        except:
            pass
        
        if operator_self:
            operator_self.report({'ERROR'}, f"Failed to apply as rest pose with flattening: {str(e)}")
        return {'CANCELLED'}


class ARMATURE_OT_apply_as_rest_pose(Operator):
    """Apply current pose as rest pose (like CATS Apply as Rest Pose)"""
    bl_idname = "armature.apply_as_rest_pose"
    bl_label = "Apply as Rest Pose"
    bl_description = "Apply current pose transforms as the new rest pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        return execute_apply_rest_pose_core(context, armature, self, skip_inherit_check=False)
    
    def modal(self, context, event):
        # Handle confirmation dialog result
        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            # User confirmed - proceed with apply rest pose
            props = getattr(context.scene, 'nyarc_tools_props', None)
            if props and props.bone_armature_object:
                return self._execute_apply_rest_pose(context, props.bone_armature_object, skip_inherit_check=True)
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # User cancelled
            self.report({'INFO'}, "Apply as rest pose cancelled")
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if props and props.bone_armature_object:
            armature = props.bone_armature_object
            all_none, none_count, total_bones = check_all_bones_inherit_scale_none(armature)
            full_count = total_bones - none_count
            
            # Title 
            layout.label(text="Apply as Rest Pose Options", icon='ARMATURE_DATA')
            layout.separator()
            
            # Status info
            box = layout.box()
            box.label(text=f"Detected {full_count} bones with inherit_scale=FULL", icon='INFO')
            box.label(text="These can cause matrix shearing cascades that")
            box.label(text="may break pose history rollbacks.")
            
            layout.separator()
            
            # Options
            col = layout.column(align=True)
            col.scale_y = 1.2
            
            if FLATTENING_AVAILABLE:
                # Recommended option - flattening
                row = col.row()
                flatten_op = row.operator("armature.apply_rest_with_flattening", 
                                        text="Apply with Flattening (Recommended)", 
                                        icon='CHECKMARK')
                
                box = layout.box()
                box.label(text="Flattening prevents matrix shearing by:")
                box.label(text="  1. Temporarily flattening inheritance")
                box.label(text="  2. Applying pose as rest cleanly")  
                box.label(text="  3. Restoring inherit_scale settings")
                
                layout.separator()
                
                # Alternative options
                col.label(text="Alternative options:")
                
                row = col.row()
                row.scale_y = 0.9
                set_none_op = row.operator("armature.apply_rest_set_none_first", 
                                         text="Set All to NONE", 
                                         icon='CANCEL')
                                         
                row = col.row()
                row.scale_y = 0.9
                continue_op = row.operator("armature.apply_rest_continue_anyway", 
                                         text="Continue Anyway (Risk Cascades)", 
                                         icon='ERROR')
            else:
                # Flattening not available - show warning
                box = layout.box()
                box.label(text="Inheritance flattening system not available.", icon='ERROR')
                box.label(text="Proceeding may cause matrix cascade issues.")
                
                layout.separator()
                
                row = col.row()
                continue_op = row.operator("armature.apply_rest_continue_anyway", 
                                         text="Continue Anyway", 
                                         icon='ERROR')

    def invoke(self, context, event):
        # Check if we need to show dialog first
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        all_none, none_count, total_bones = check_all_bones_inherit_scale_none(armature)
        
        if not all_none:
            # Show popup to let user choose how to handle inherit_scale=FULL bones
            full_count = total_bones - none_count
            print(f"INHERITANCE DETECTION: Found {full_count} bones with inherit_scale=FULL")
            print(f"Showing user options popup to prevent matrix shearing cascades")
            
            # Show popup with options - this will call the appropriate method based on user choice
            return context.window_manager.invoke_popup(self, width=450)
        else:
            # All bones are 'None', proceed directly with normal method
            return execute_apply_rest_pose_core(context, armature, self, skip_inherit_check=True)
        


class ARMATURE_OT_apply_rest_continue_anyway(Operator):
    """Continue with apply as rest pose without changing inherit scale settings"""
    bl_idname = "armature.apply_rest_continue_anyway"
    bl_label = "Continue Anyway"
    bl_description = "Apply as rest pose without changing inherit scale settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Call the main apply rest pose logic, bypassing the inherit scale check
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        # Call the standalone function directly
        return execute_apply_rest_pose_core(context, armature, self, skip_inherit_check=True)


class ARMATURE_OT_apply_rest_set_none_first(Operator):
    """Set all bones to inherit scale None, then apply as rest pose"""
    bl_idname = "armature.apply_rest_set_none_first"
    bl_label = "Set All to None First"
    bl_description = "Set all bones inherit scale to 'None', then apply as rest pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # First set all bones to None
        bpy.ops.armature.set_inherit_scale_all_none()
        
        # Then apply as rest pose
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        # Call the standalone function directly
        return execute_apply_rest_pose_core(context, armature, self, skip_inherit_check=True)


class ARMATURE_OT_apply_rest_with_flattening(Operator):
    """Apply pose as rest with temporary inheritance flattening to prevent matrix shearing cascades"""
    bl_idname = "armature.apply_rest_with_flattening"
    bl_label = "Apply as Rest (Flattened)"
    bl_description = "Temporarily flatten inheritance, apply pose as rest, then restore inheritance settings to prevent matrix shearing cascades"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not FLATTENING_AVAILABLE:
            self.report({'ERROR'}, "Inheritance flattening system not available")
            return {'CANCELLED'}
            
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        # Call the shared flattened function
        return execute_flattened_apply_rest_pose(context, armature, self)


class ARMATURE_OT_apply_rest_continue_anyway(Operator):
    """Continue with apply as rest pose without changing inherit scale settings"""
    bl_idname = "armature.apply_rest_continue_anyway"
    bl_label = "Continue Anyway"
    bl_description = "Apply as rest pose without changing inherit scale settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Call the main apply rest pose logic, bypassing the inherit scale check
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        # Call the standalone function directly
        return execute_apply_rest_pose_core(context, armature, self, skip_inherit_check=True)


class ARMATURE_OT_apply_rest_set_none_first(Operator):
    """Set all bones to inherit scale None (does not apply rest pose)"""
    bl_idname = "armature.apply_rest_set_none_first"
    bl_label = "Set All to None"
    bl_description = "Set all bones inherit scale to 'None' (does not apply rest pose)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        # Set all bones to inherit_scale = 'NONE' ONLY - do not apply rest pose
        if not set_all_bones_inherit_scale_none(armature):
            self.report({'ERROR'}, "Failed to set bones to inherit_scale=None")
            return {'CANCELLED'}
        
        self.report({'INFO'}, "Set all bones to inherit_scale=None. You can now apply rest pose safely.")
        return {'FINISHED'}


class ARMATURE_OT_apply_rest_with_flattening(Operator):
    """Apply pose as rest with temporary inheritance flattening to prevent matrix shearing cascades"""
    bl_idname = "armature.apply_rest_with_flattening"
    bl_label = "Apply as Rest (Flattened)"
    bl_description = "Temporarily flatten inheritance, apply pose as rest, then restore inheritance settings to prevent matrix shearing cascades"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        # Call the shared flattened function
        return execute_flattened_apply_rest_pose(context, armature, self)


# Registration
classes = (
    ARMATURE_OT_apply_as_rest_pose,
    ARMATURE_OT_apply_rest_continue_anyway,
    ARMATURE_OT_apply_rest_set_none_first,
    ARMATURE_OT_apply_rest_with_flattening,
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