# Bone Transform Saver Module
# Recreates CATS-like functionality for pose mode editing and rest pose application
# With added ability to save/load bone transform presets

import bpy
import json
import os
from bpy.props import PointerProperty, StringProperty, BoolProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup, Object, UIList
from mathutils import Vector, Quaternion, Matrix

# Import our bone name mapper and calculations module
try:
    from .bone_name_mapper import map_bone_transforms
    BONE_MAPPER_AVAILABLE = True
except ImportError:
    BONE_MAPPER_AVAILABLE = False
    print("Warning: bone_name_mapper not available, using exact matching only")

# Import our modularized calculations (OPTIONAL - if available)
try:
    from .bone_transform_calculations import (
        apply_head_tail_transform_with_mesh_deformation,
        get_armature_transforms,
        calculate_head_tail_differences,
        matrix_to_pose_transform,
        transforms_different,
        apply_armature_to_mesh_with_no_shape_keys,
        apply_armature_to_mesh_with_shape_keys
    )
    CALCULATIONS_AVAILABLE = True
except ImportError:
    CALCULATIONS_AVAILABLE = False
    print("Warning: bone_transform_calculations not available, using embedded methods")

# Import modularized UI
try:
    from .bone_transforms.ui.panels import draw_ui
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False
    print("Warning: bone_transforms.ui.panels not available, using embedded UI")

# Import VRChat compatibility module
try:
    from .bone_transforms.compatibility import check_bone_compatibility, get_compatibility_warning_message
    VRCHAT_COMPAT_AVAILABLE = True
except ImportError:
    VRCHAT_COMPAT_AVAILABLE = False
    print("Warning: bone_transforms.compatibility not available, using embedded compatibility")

# Import modularized diff export operator
try:
    from .bone_transforms.io.diff_export import ARMATURE_OT_export_armature_diff
    DIFF_EXPORT_AVAILABLE = True
except ImportError:
    DIFF_EXPORT_AVAILABLE = False
    print("Warning: armature_diff_export not available, using embedded diff export")

# Import modularized bone transform loader
try:
    from .bone_transforms.operators.loader import load_bone_transforms_internal
    LOADER_AVAILABLE = True
except ImportError:
    LOADER_AVAILABLE = False
    print("Warning: bone_transform_loader not available, using embedded loader")

# Import head/tail transform utilities
try:
    # head_tail fallback removed - precision correction system supersedes it
    HEAD_TAIL_UTILS_AVAILABLE = False
except ImportError:
    HEAD_TAIL_UTILS_AVAILABLE = False
    print("Warning: bone_head_tail_utils not available")

# Import inheritance flattening utilities (HARD DEPENDENCY)
from .bone_transforms.utils.inheritance_flattening import (
    flatten_bone_transforms_for_save,
    prepare_bones_for_flattened_load,
    restore_original_inherit_scales,
    get_bones_requiring_flatten_context
)

# Import modularized operators
try:
    from .bone_transforms.operators.apply_rest import ARMATURE_OT_apply_as_rest_pose
    APPLY_REST_POSE_AVAILABLE = True
except ImportError:
    APPLY_REST_POSE_AVAILABLE = False
    print("Warning: bone_transforms.operators.apply_rest not available")

try:
    from .bone_transforms.operators.pose_mode import ARMATURE_OT_toggle_pose_mode, ARMATURE_OT_reset_and_stop_pose_mode
    POSE_MODE_OPERATORS_AVAILABLE = True
except ImportError:
    POSE_MODE_OPERATORS_AVAILABLE = False
    print("Warning: bone_transforms.operators.pose_mode not available")

try:
    from .bone_transforms.operators.inherit_scale import ARMATURE_OT_toggle_inherit_scale
    INHERIT_SCALE_OPERATOR_AVAILABLE = True
except ImportError:
    INHERIT_SCALE_OPERATOR_AVAILABLE = False
    print("Warning: bone_transforms.operators.inherit_scale not available")

# Data structure design:
# Each preset contains:
# - name: preset name
# - bones: dict of bone_name -> {location, rotation_quaternion, scale}
# - armature_name: source armature name (for reference)
# - created_date: timestamp


class BoneTransformData(PropertyGroup):
    """Individual bone transform data"""
    bone_name: StringProperty(name="Bone Name")
    location_x: bpy.props.FloatProperty(name="Location X")
    location_y: bpy.props.FloatProperty(name="Location Y") 
    location_z: bpy.props.FloatProperty(name="Location Z")
    rotation_w: bpy.props.FloatProperty(name="Rotation W")
    rotation_x: bpy.props.FloatProperty(name="Rotation X")
    rotation_y: bpy.props.FloatProperty(name="Rotation Y")
    rotation_z: bpy.props.FloatProperty(name="Rotation Z")
    scale_x: bpy.props.FloatProperty(name="Scale X")
    scale_y: bpy.props.FloatProperty(name="Scale Y")
    scale_z: bpy.props.FloatProperty(name="Scale Z")


class BoneTransformPreset(PropertyGroup):
    """Bone transform preset containing multiple bone transforms"""
    name: StringProperty(name="Preset Name", default="New Preset")
    source_armature: StringProperty(name="Source Armature")
    bone_count: bpy.props.IntProperty(name="Bone Count", default=0)




def armature_poll(self, obj):
    """Poll function to filter armature objects"""
    return obj and obj.type == 'ARMATURE'


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




class ARMATURE_OT_toggle_inherit_scale(Operator):
    """Toggle inherit scale for all bones in the armature"""
    bl_idname = "armature.toggle_inherit_scale"
    bl_label = "Toggle Inherit Scale"
    bl_description = "Toggle inherit scale between 'None' and 'Full' for all bones"
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


class ARMATURE_OT_save_bone_transforms(Operator):
    """Save current bone transforms as a preset"""
    bl_idname = "armature.save_bone_transforms"
    bl_label = "Save Bone Transforms"
    bl_description = "Save current bone transforms as a preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        if not props.bone_preset_name.strip():
            self.report({'ERROR'}, "Please enter a preset name")
            return {'CANCELLED'}
        
        # Require pose mode for saving - user should see what they're saving
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Please enter pose mode first to save transforms. Use 'Start Pose Mode' button.")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        preset_name = props.bone_preset_name.strip()
        
        # Verify armature is active in pose mode
        if context.object != armature:
            self.report({'ERROR'}, "Selected armature must be active in pose mode to save transforms")
            return {'CANCELLED'}
        
        try:
            # We're already verified to be in pose mode with correct armature above
            
            # FLATTENED INHERITANCE APPROACH: Let flattening module determine what to save
            
            # Step 1: Find bones with statistical transforms (seed bones)
            statistical_change_bones = set()
            identity_bones = 0
            
            # Ensure we're in pose mode for analysis
            if context.mode != 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            
            for pose_bone in armature.pose.bones:
                # Current pose transforms (statistical values)
                location = pose_bone.location
                rotation = pose_bone.rotation_quaternion
                scale = pose_bone.scale
                
                # Check if this bone has any non-identity statistical transforms
                has_location_change = (abs(location.x) > 0.0001 or abs(location.y) > 0.0001 or abs(location.z) > 0.0001)
                has_rotation_change = not (abs(rotation.w - 1.0) < 0.0001 and abs(rotation.x) < 0.0001 and abs(rotation.y) < 0.0001 and abs(rotation.z) < 0.0001)
                has_scale_change = not (abs(scale.x - 1.0) < 0.0001 and abs(scale.y - 1.0) < 0.0001 and abs(scale.z - 1.0) < 0.0001)
                
                # These are bones with actual statistical transforms (scaling source)
                if has_location_change or has_rotation_change or has_scale_change:
                    statistical_change_bones.add(pose_bone.name)
                else:
                    identity_bones += 1
            
            print(f"Preset Save: Found {len(statistical_change_bones)} bones with statistical changes")
            print(f"Preset Save: {identity_bones} bones have identity transforms (may inherit visual changes)")
            
            # Step 2: Let flattening module determine ALL bones to save (including inheritance)
            target_bones = get_bones_requiring_flatten_context(armature, statistical_change_bones)
            
            inheritance_bones = target_bones - statistical_change_bones
            print(f"Preset Save: Flattening module added {len(inheritance_bones)} inheritance chain bones: {list(inheritance_bones)}")
            print(f"Preset Save: Total bones to save: {len(target_bones)} (statistical + inheritance)")
            
            if not target_bones:
                self.report({'ERROR'}, "No bone transforms to save - no statistical changes or inheritance chains found")
                return {'CANCELLED'}
            
            # Use flattening module to capture inheritance-consistent transforms
            # Pass both statistical bones (sources) and all bones (targets) for proper inheritance calculation
            flattened_data = flatten_bone_transforms_for_save(armature, target_bones, statistical_change_bones)
            
            if not flattened_data:
                self.report({'ERROR'}, "Flattening module failed to capture transforms")
                return {'CANCELLED'}
            
            # Build bone data from flattened transforms
            bone_data = {}
            for bone_name, transform_data in flattened_data.items():
                bone_data[bone_name] = {
                    'location': transform_data['location'],
                    'rotation_quaternion': transform_data['rotation_quaternion'],
                    'scale': transform_data['scale']
                }
            
            bone_count = len(bone_data)
            print(f"Preset Save: Successfully flattened {bone_count} bone transforms")
            
            # Create preset data structure with flattened flag
            preset_data = {
                'name': preset_name,
                'source_armature': armature.name,
                'bone_count': bone_count,
                'bones': bone_data,
                'flattened': True,  # Indicate this uses flattened transforms
                'created_date': bpy.context.scene.frame_current  # Simple timestamp
            }
            
            # Save to file (create presets directory if needed)
            presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
            os.makedirs(presets_dir, exist_ok=True)
            
            preset_file = os.path.join(presets_dir, f"{preset_name}.json")
            
            with open(preset_file, 'w') as f:
                json.dump(preset_data, f, indent=2)
            
            self.report({'INFO'}, f"Saved preset '{preset_name}': {bone_count} bones total ({len(statistical_change_bones)} statistical + {len(inheritance_bones)} inherited)")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save bone transforms: {str(e)}")
            return {'CANCELLED'}


class ARMATURE_OT_compatibility_warning(Operator):
    """Show compatibility warning dialog"""
    bl_idname = "armature.compatibility_warning"
    bl_label = "Bone Compatibility Warning"
    bl_description = "Warning about bone naming compatibility"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    message: StringProperty(name="Warning Message")
    preset_name: StringProperty(name="Preset Name")
    
    def execute(self, context):
        # User clicked OK, proceed with loading
        bpy.ops.armature.load_bone_transforms_confirmed(preset_name=self.preset_name)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Show warning dialog
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="⚠️ Bone Naming Compatibility Warning", icon='ERROR')
        layout.separator()
        
        # Split message into lines for better display
        lines = self.message.split('. ')
        for line in lines:
            if line.strip():
                layout.label(text=line.strip() + ('.' if not line.endswith('.') else ''))
        
        layout.separator()
        layout.label(text="Continue anyway?", icon='QUESTION')
        layout.label(text="(Some transforms may not apply correctly)")


class ARMATURE_OT_load_bone_transforms(Operator):
    """Load bone transforms from a preset"""
    bl_idname = "armature.load_bone_transforms"
    bl_label = "Load Bone Transforms"
    bl_description = "Load bone transforms from a preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: StringProperty(name="Preset Name")
    
    def execute(self, context):
        # First check compatibility and show warning if needed
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        if not self.preset_name:
            self.report({'ERROR'}, "No preset specified")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Load preset file to check compatibility
            presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
            preset_file = os.path.join(presets_dir, f"{self.preset_name}.json")
            
            if not os.path.exists(preset_file):
                self.report({'ERROR'}, f"Preset '{self.preset_name}' not found")
                return {'CANCELLED'}
            
            with open(preset_file, 'r') as f:
                preset_data = json.load(f)
            
            # Check bone compatibility if available
            if VRCHAT_COMPAT_AVAILABLE:
                armature_bones = [bone.name for bone in armature.pose.bones]
                preset_bones = list(preset_data['bones'].keys())
                
                compatibility_score, missing_categories, details = check_bone_compatibility(armature_bones, preset_bones)
                warning_message = get_compatibility_warning_message(compatibility_score, missing_categories, armature.name, self.preset_name)
                
                if warning_message:
                    # Show warning dialog
                    bpy.ops.armature.compatibility_warning('INVOKE_DEFAULT', 
                                                         message=warning_message,
                                                         preset_name=self.preset_name)
                    return {'FINISHED'}  # Dialog handles the rest
            
            # High compatibility or no compatibility checking, proceed directly
            if LOADER_AVAILABLE:
                return load_bone_transforms_internal(context, armature, preset_data, self)
            else:
                self.report({'ERROR'}, "Bone transform loader module not available")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to check compatibility: {str(e)}")
            return {'CANCELLED'}
    
    # _apply_head_tail_transform removed - precision correction system supersedes fallback approach


class ARMATURE_OT_load_bone_transforms_confirmed(Operator):
    """Load bone transforms from a preset (confirmed after warning)"""
    bl_idname = "armature.load_bone_transforms_confirmed"
    bl_label = "Load Bone Transforms (Confirmed)"
    bl_description = "Load bone transforms from a preset after compatibility warning"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    preset_name: StringProperty(name="Preset Name")
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props or not props.bone_armature_object:
            self.report({'ERROR'}, "Please select an armature first")
            return {'CANCELLED'}
        
        if not self.preset_name:
            self.report({'ERROR'}, "No preset specified")
            return {'CANCELLED'}
        
        armature = props.bone_armature_object
        
        try:
            # Load preset file
            presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
            preset_file = os.path.join(presets_dir, f"{self.preset_name}.json")
            
            if not os.path.exists(preset_file):
                self.report({'ERROR'}, f"Preset '{self.preset_name}' not found")
                return {'CANCELLED'}
            
            with open(preset_file, 'r') as f:
                preset_data = json.load(f)
            
            # Use the shared internal function
            if LOADER_AVAILABLE:
                return load_bone_transforms_internal(context, armature, preset_data, self)
            else:
                self.report({'ERROR'}, "Bone transform loader module not available")
                return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load bone transforms: {str(e)}")
            return {'CANCELLED'}
    
    # _apply_head_tail_transform removed - precision correction system supersedes fallback approach


class ARMATURE_OT_delete_bone_transforms(Operator):
    """Delete a bone transform preset"""
    bl_idname = "armature.delete_bone_transforms"
    bl_label = "Delete Preset"
    bl_description = "Delete a bone transform preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: StringProperty(name="Preset Name")
    
    def execute(self, context):
        if not self.preset_name:
            self.report({'ERROR'}, "No preset specified")
            return {'CANCELLED'}
        
        try:
            # Delete preset file
            presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
            preset_file = os.path.join(presets_dir, f"{self.preset_name}.json")
            
            if not os.path.exists(preset_file):
                self.report({'ERROR'}, f"Preset '{self.preset_name}' not found")
                return {'CANCELLED'}
            
            os.remove(preset_file)
            self.report({'INFO'}, f"Deleted preset '{self.preset_name}'")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to delete preset: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Show confirmation dialog
        return context.window_manager.invoke_confirm(self, event)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Delete preset '{self.preset_name}'?")
        layout.label(text="This action cannot be undone.")


class ARMATURE_OT_list_presets(Operator):
    """List available bone transform presets"""
    bl_idname = "armature.list_presets"
    bl_label = "Refresh Presets"
    bl_description = "Refresh the list of available presets"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # This will be called to refresh the preset list
        self.report({'INFO'}, "Preset list refreshed")
        return {'FINISHED'}




# UI drawing function is now modularized - this is just a wrapper
def draw_ui(layout, context):
    """Wrapper for modularized UI drawing function"""
    if UI_AVAILABLE:
        from .bone_transforms.ui.panels import draw_ui as ui_draw
        ui_draw(layout, context)
    else:
        layout.label(text="Bone Transform UI module not available!", icon='ERROR')


# Module registration - build classes list dynamically
_base_classes = (
    BoneTransformData,
    BoneTransformPreset,
    ARMATURE_OT_save_bone_transforms,
    ARMATURE_OT_compatibility_warning,
    ARMATURE_OT_load_bone_transforms,
    ARMATURE_OT_load_bone_transforms_confirmed,
    ARMATURE_OT_delete_bone_transforms,
    ARMATURE_OT_list_presets,
)

# Add modularized classes if available
classes = list(_base_classes)

# Add pose mode operators
if POSE_MODE_OPERATORS_AVAILABLE:
    classes.extend([ARMATURE_OT_toggle_pose_mode, ARMATURE_OT_reset_and_stop_pose_mode])

# Add inherit scale operator
if INHERIT_SCALE_OPERATOR_AVAILABLE:
    classes.append(ARMATURE_OT_toggle_inherit_scale)

# Add apply rest pose operator
if APPLY_REST_POSE_AVAILABLE:
    classes.append(ARMATURE_OT_apply_as_rest_pose)

# Add diff export operator
if DIFF_EXPORT_AVAILABLE:
    classes.append(ARMATURE_OT_export_armature_diff)

classes = tuple(classes)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)