# Bone Flip Operator
# Handles duplication and symmetrizing of armature bones

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, EnumProperty

from ..utils.validation import validate_bone_selection, safe_mode_switch
from ..utils.naming import get_opposite_name, detect_axis_from_selection


def _get_direction_items_for_axis(axis):
    """Get direction items based on axis"""
    if axis == 'X':
        return [
            ('LEFT_TO_RIGHT', "Left → Right", "Flip from left side to right side"),
            ('RIGHT_TO_LEFT', "Right → Left", "Flip from right side to left side")
        ]
    elif axis == 'Y':
        return [
            ('FRONT_TO_BACK', "Front → Back", "Flip from front side to back side"),
            ('BACK_TO_FRONT', "Back → Front", "Flip from back side to front side")
        ]
    elif axis == 'Z':
        return [
            ('UP_TO_DOWN', "Up → Down", "Flip from up side to down side"),
            ('DOWN_TO_UP', "Down → Up", "Flip from down side to up side")
        ]
    else:
        return [
            ('LEFT_TO_RIGHT', "Left → Right", "Flip from left side to right side"),
            ('RIGHT_TO_LEFT', "Right → Left", "Flip from right side to left side")
        ]


class ARMATURE_OT_flip_bones(Operator):
    """Duplicate and symmetrize selected bones in armature"""
    bl_idname = "armature.flip_bones"
    bl_label = "Flip Bones"
    bl_description = "Duplicate and mirror selected bones to the opposite side"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Operator properties
    auto_rename: BoolProperty(
        name="Auto-rename (.L → .R)",
        description="Automatically rename bones using .L/.R convention",
        default=True
    )
    
    apply_armature_transforms: BoolProperty(
        name="Apply Armature Transforms",
        description="Apply armature transforms before symmetrizing (recommended)",
        default=True
    )
    
    mirror_axis: EnumProperty(
        name="Mirror Axis",
        description="Axis to mirror across",
        items=[
            ('X', "X-Axis (Left ↔ Right)", "Mirror across X-axis"),
            ('Y', "Y-Axis (Front ↔ Back)", "Mirror across Y-axis"),
            ('Z', "Z-Axis (Up ↔ Down)", "Mirror across Z-axis")
        ],
        default='X'
    )
    
    manual_mode: BoolProperty(
        name="Manual Mode",
        description="Override automatic axis and direction detection",
        default=False
    )
    
    manual_direction: EnumProperty(
        name="Manual Direction",
        description="Manually specify flip direction",
        items=lambda self, context: _get_direction_items_for_axis(self.mirror_axis),
        default=0
    )
    
    overwrite_existing: BoolProperty(
        name="Overwrite Existing",
        description="Overwrite existing bones on target side",
        default=True
    )
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and 
                context.active_object.type == 'ARMATURE' and
                (context.mode == 'EDIT_ARMATURE' or context.mode == 'OBJECT'))
    
    def execute(self, context):
        armature_obj = context.active_object
        
        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}
        
        # Store original mode
        original_mode = context.mode
        
        try:
            # Apply armature transforms if requested and needed
            if self.apply_armature_transforms:
                # Switch to object mode to apply transforms
                mode_error = safe_mode_switch('OBJECT')
                if mode_error:
                    self.report({'WARNING'}, f"Could not switch to object mode: {mode_error}")
                else:
                    # Check if transforms need to be applied
                    loc, rot, scale = armature_obj.matrix_world.decompose()
                    needs_apply = (loc.length > 0.001 or 
                                 abs(rot.to_euler().x) > 0.001 or abs(rot.to_euler().y) > 0.001 or abs(rot.to_euler().z) > 0.001 or
                                 abs(scale.x - 1.0) > 0.001 or abs(scale.y - 1.0) > 0.001 or abs(scale.z - 1.0) > 0.001)
                    
                    if needs_apply:
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                        self.report({'INFO'}, "Applied armature transforms")
            
            # Switch to edit mode
            mode_error = safe_mode_switch('EDIT')
            if mode_error:
                self.report({'ERROR'}, mode_error)
                return {'CANCELLED'}
            
            # Validate bone selection
            errors, warnings = validate_bone_selection(armature_obj)
            
            if warnings:
                for warning in warnings:
                    self.report({'WARNING'}, warning)
            
            # Get selected bones
            selected_bones = [bone for bone in armature_obj.data.edit_bones if bone.select]
            
            if not selected_bones:
                self.report({'ERROR'}, "No bones selected")
                return {'CANCELLED'}
            
            # Determine axis to use
            axis_to_use = self._determine_axis(selected_bones)
            
            # Validate that we can flip these bones
            validation_result = self._validate_bones_for_flipping(selected_bones, axis_to_use)
            if not validation_result['valid']:
                self.report({'ERROR'}, validation_result['error'])
                return {'CANCELLED'}
            
            # Store bone names before operation (edit_bones references change)
            bone_names_to_flip = [bone.name for bone in selected_bones]
            
            # Perform the flip operation
            success_count = 0
            
            for bone_name in bone_names_to_flip:
                # Re-get bone reference (may have changed during operations)
                bone = armature_obj.data.edit_bones.get(bone_name)
                if not bone:
                    continue
                
                # Select only this bone
                bpy.ops.armature.select_all(action='DESELECT')
                bone.select = True
                bone.select_head = True
                bone.select_tail = True
                armature_obj.data.edit_bones.active = bone
                
                try:
                    # Duplicate the bone
                    bpy.ops.armature.duplicate()
                    
                    # Get the duplicated bone (should be active now)
                    duplicated_bone = armature_obj.data.edit_bones.active
                    
                    if duplicated_bone:
                        # Apply symmetrize to position it correctly
                        bpy.ops.armature.symmetrize()
                        
                        # Handle naming if auto-rename is enabled
                        if self.auto_rename:
                            target_name = get_opposite_name(bone_name, axis_to_use)
                            
                            # Check if target name exists and handle accordingly
                            existing_bone = armature_obj.data.edit_bones.get(target_name)
                            if existing_bone and not self.overwrite_existing:
                                # Find unique name
                                counter = 1
                                while armature_obj.data.edit_bones.get(f"{target_name}.{counter:03d}"):
                                    counter += 1
                                target_name = f"{target_name}.{counter:03d}"
                            elif existing_bone and self.overwrite_existing:
                                # Remove existing bone
                                armature_obj.data.edit_bones.remove(existing_bone)
                            
                            # Set the new name
                            duplicated_bone.name = target_name
                        
                        success_count += 1
                        self.report({'INFO'}, f"Created mirrored bone: {duplicated_bone.name}")
                
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to flip bone '{bone_name}': {str(e)}")
                    continue
            
            if success_count > 0:
                self.report({'INFO'}, f"Successfully flipped {success_count} bone(s)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to flip any bones")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Bone flip operation failed: {str(e)}")
            return {'CANCELLED'}
            
        finally:
            # Try to restore original mode
            try:
                if original_mode == 'OBJECT':
                    safe_mode_switch('OBJECT')
                elif original_mode == 'POSE':
                    safe_mode_switch('POSE')
            except:
                pass  # Mode switch failed, stay in current mode
    
    def _determine_axis(self, selected_bones):
        """Determine which axis to use for mirroring"""
        if self.manual_mode:
            return self.mirror_axis
        
        # Auto-detect axis from bone names
        bone_names = [bone.name for bone in selected_bones]
        detected_axis = detect_axis_from_selection(bone_names)
        
        self.report({'INFO'}, f"Auto-detected axis: {detected_axis}")
        return detected_axis
    
    def _validate_bones_for_flipping(self, selected_bones, axis):
        """Validate that selected bones can be flipped"""
        result = {'valid': True, 'error': ''}
        
        # Basic validation - bones exist and can be mirrored
        if not selected_bones:
            result['valid'] = False
            result['error'] = "No bones selected for flipping"
        
        # If auto-rename is disabled, check if bones have proper naming
        if not self.auto_rename:
            from ..utils.naming import detect_naming_pattern
            bones_without_naming = []
            
            for bone in selected_bones:
                current_suffix, _, _ = detect_naming_pattern(bone.name, axis)
                if not current_suffix:
                    bones_without_naming.append(bone.name)
            
            if bones_without_naming:
                result['valid'] = False
                result['error'] = f"Bones without proper naming for {axis}-axis: {', '.join(bones_without_naming)}"
        
        return result
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "mirror_axis")
        layout.prop(self, "manual_mode")
        
        if self.manual_mode:
            layout.prop(self, "manual_direction")
            
        layout.prop(self, "auto_rename")
        layout.prop(self, "overwrite_existing")
        layout.prop(self, "apply_armature_transforms")


# Registration
classes = (
    ARMATURE_OT_flip_bones,
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