# Pose Mode Control Operators
# Start/Stop/Reset pose mode functionality (CATS-like)

import bpy
from bpy.types import Operator

class ARMATURE_OT_toggle_pose_mode(Operator):
    """Toggle pose mode editing (like CATS Start/Stop Pose Mode)"""
    bl_idname = "armature.toggle_pose_mode"
    bl_label = "Toggle Pose Mode"
    bl_description = "Toggle between pose mode and object mode for bone editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Check current state and toggle
            if context.mode == 'POSE' and context.object == armature and getattr(props, 'bone_editing_active', False):
                # Currently in pose mode - switch to object mode
                return self._stop_pose_mode(context, props)
            else:
                # Not in pose mode - start pose mode
                return self._start_pose_mode(context, props, armature)
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to toggle pose mode: {str(e)}")
            return {'CANCELLED'}
    
    def _start_pose_mode(self, context, props, armature):
        """Start pose mode editing"""
        # ALWAYS switch to object mode first to ensure clean state
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.update()
        
        # Double-check we're actually in object mode
        if context.mode != 'OBJECT':
            self.report({'ERROR'}, f"Failed to switch to object mode, currently in {context.mode}")
            return {'CANCELLED'}
        
        # Select the armature
        try:
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
        except Exception as select_error:
            # Alternative selection method
            try:
                for obj in context.selected_objects:
                    obj.select_set(False)
                armature.select_set(True)
                context.view_layer.objects.active = armature
            except Exception as alt_error:
                self.report({'ERROR'}, f"All selection methods failed: {alt_error}")
                return {'CANCELLED'}
        
        # Switch to pose mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # Set armature to POSE position to show current transforms
        armature.data.pose_position = 'POSE'
        
        # Store that we're in editing mode
        props.bone_editing_active = True
        
        self.report({'INFO'}, f"Started pose mode editing on {armature.name}")
        return {'FINISHED'}
    
    def _stop_pose_mode(self, context, props):
        """Stop pose mode editing"""
        # Switch back to object mode
        if context.mode == 'POSE':
            bpy.ops.object.mode_set(mode='OBJECT')
        elif context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Set armature to REST position when not in pose mode
        armature = props.bone_armature_object
        if armature:
            armature.data.pose_position = 'REST'
        
        # Mark editing as inactive
        props.bone_editing_active = False
        
        self.report({'INFO'}, "Stopped pose mode editing")
        return {'FINISHED'}


class ARMATURE_OT_reset_and_stop_pose_mode(Operator):
    """Reset current pose and stop pose mode editing"""
    bl_idname = "armature.reset_and_stop_pose_mode"
    bl_label = "Reset & Stop Pose Mode"
    bl_description = "Clear all pose transforms and exit pose mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Ensure we're in pose mode with the correct armature
            if context.mode != 'POSE' or context.object != armature:
                bpy.ops.object.select_all(action='DESELECT')
                armature.select_set(True)
                context.view_layer.objects.active = armature
                bpy.ops.object.mode_set(mode='POSE')
            
            # Clear all pose transforms
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.transforms_clear()
            
            # Now stop pose mode (which will also set to REST position)
            # Switch back to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Set armature to REST position
            armature.data.pose_position = 'REST'
            
            # Mark editing as inactive
            props.bone_editing_active = False
            
            self.report({'INFO'}, f"Reset pose and stopped pose mode editing on {armature.name}")
            return {'FINISHED'}
            
        except Exception as e:
            # Even if reset fails, mark as inactive
            props.bone_editing_active = False
            self.report({'ERROR'}, f"Failed to reset and stop pose mode: {str(e)}")
            return {'CANCELLED'}


# Registration
POSE_MODE_CLASSES = (
    ARMATURE_OT_toggle_pose_mode,
    ARMATURE_OT_reset_and_stop_pose_mode,
)

# Keep compatibility alias
classes = POSE_MODE_CLASSES

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass