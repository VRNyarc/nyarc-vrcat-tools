# Mesh Flip Operator
# Handles duplication and mirroring of mesh objects

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, EnumProperty

from ..utils.validation import validate_selected_objects, safe_mode_switch
from ..utils.naming import get_opposite_name, increment_name


class OBJECT_OT_flip_mesh(Operator):
    """Duplicate and mirror selected mesh objects across the X-axis"""
    bl_idname = "object.flip_mesh"
    bl_label = "Flip Mesh"
    bl_description = "Duplicate and mirror selected mesh objects to the opposite side"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Operator properties
    apply_transforms: BoolProperty(
        name="Apply Transforms",
        description="Apply location, rotation, and scale after mirroring",
        default=True
    )
    
    auto_rename: BoolProperty(
        name="Auto-rename",
        description="Automatically rename using .L/.R convention",
        default=True
    )
    
    keep_original_selected: BoolProperty(
        name="Keep Original Selected",
        description="Keep original objects selected after operation",
        default=False
    )
    
    mirror_axis: EnumProperty(
        name="Mirror Axis",
        description="Axis to mirror across",
        items=[
            ('X', "X-Axis", "Mirror across X-axis (left/right)"),
            ('Y', "Y-Axis", "Mirror across Y-axis (front/back)"),
            ('Z', "Z-Axis", "Mirror across Z-axis (up/down)")
        ],
        default='X'
    )
    
    manual_mode: BoolProperty(
        name="Manual Mode",
        description="Use manual direction override",
        default=False
    )
    
    manual_direction: EnumProperty(
        name="Manual Direction",
        description="Manual direction for mirroring",
        items=[
            ('RIGHT_TO_LEFT', "Right → Left", "Mirror from right side to left side"),
            ('LEFT_TO_RIGHT', "Left → Right", "Mirror from left side to right side"),
            ('FRONT_TO_BACK', "Front → Back", "Mirror from front to back"),
            ('BACK_TO_FRONT', "Back → Front", "Mirror from back to front"),
            ('UP_TO_DOWN', "Up → Down", "Mirror from up to down"),
            ('DOWN_TO_UP', "Down → Up", "Mirror from down to up")
        ],
        default='RIGHT_TO_LEFT'
    )
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT' and 
                context.selected_objects and
                any(obj.type == 'MESH' for obj in context.selected_objects))
    
    def execute(self, context):
        # Validate input
        errors, warnings = validate_selected_objects()
        
        if errors:
            for error in errors:
                self.report({'ERROR'}, error)
            return {'CANCELLED'}
        
        if warnings:
            for warning in warnings:
                self.report({'WARNING'}, warning)
        
        # Ensure we're in object mode
        mode_error = safe_mode_switch('OBJECT')
        if mode_error:
            self.report({'ERROR'}, mode_error)
            return {'CANCELLED'}
        
        # Get selected mesh objects
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_meshes:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        # Store original selection
        original_selection = context.selected_objects.copy()
        original_active = context.active_object
        
        # Track created objects
        created_objects = []
        
        try:
            for mesh_obj in selected_meshes:
                # Select only this mesh
                bpy.ops.object.select_all(action='DESELECT')
                mesh_obj.select_set(True)
                context.view_layer.objects.active = mesh_obj
                
                # Store original name
                original_name = mesh_obj.name
                
                # Duplicate the mesh
                bpy.ops.object.duplicate(linked=False)
                duplicated_obj = context.active_object
                created_objects.append(duplicated_obj)
                
                # Mirror the duplicated object
                constraint_axis = (
                    self.mirror_axis == 'X',
                    self.mirror_axis == 'Y', 
                    self.mirror_axis == 'Z'
                )
                
                bpy.ops.transform.mirror(
                    constraint_axis=constraint_axis,
                    orient_type='GLOBAL'
                )
                
                # Apply transforms if requested
                if self.apply_transforms:
                    bpy.ops.object.transform_apply(
                        location=True,
                        rotation=True,
                        scale=True
                    )
                
                # Handle naming with manual direction override
                if self.auto_rename:
                    # Check if manual direction should override default naming
                    if self.manual_mode and self.manual_direction:
                        new_name = self._get_manual_direction_name(original_name, self.mirror_axis, self.manual_direction)
                    else:
                        new_name = get_opposite_name(original_name, self.mirror_axis)
                    
                    # Check if name already exists
                    if new_name in bpy.data.objects:
                        new_name = increment_name(new_name)
                    duplicated_obj.name = new_name
                else:
                    # Use Blender's default naming (adds .001)
                    pass
                
                self.report({'INFO'}, f"Created mirrored mesh: {duplicated_obj.name}")
            
            # Handle selection after operation
            if not self.keep_original_selected:
                # Select only the new objects
                bpy.ops.object.select_all(action='DESELECT')
                for obj in created_objects:
                    obj.select_set(True)
                if created_objects:
                    context.view_layer.objects.active = created_objects[0]
            else:
                # Keep original selection and add new objects
                for obj in original_selection:
                    if obj:  # Check if object still exists
                        obj.select_set(True)
                for obj in created_objects:
                    obj.select_set(True)
                
                # Set active object
                if original_active and original_active in bpy.data.objects:
                    context.view_layer.objects.active = original_active
            
            self.report({'INFO'}, f"Successfully flipped {len(selected_meshes)} mesh object(s)")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to flip mesh objects: {str(e)}")
            
            # Try to clean up created objects on error
            for obj in created_objects:
                if obj and obj.name in bpy.data.objects:
                    try:
                        bpy.data.objects.remove(obj, do_unlink=True)
                    except:
                        pass
            
            return {'CANCELLED'}
    
    def _get_manual_direction_name(self, name, axis, direction):
        """Get name based on manual direction override"""
        from ..utils.naming import get_base_name
        
        # Get base name without any existing suffix
        base_name = get_base_name(name, axis)
        
        # Determine target suffix based on manual direction
        if direction == 'RIGHT_TO_LEFT':
            if axis == 'X':
                return base_name + '.L'
            elif axis == 'Y':
                return base_name + '.B'
            elif axis == 'Z':
                return base_name + '.D'
        elif direction == 'LEFT_TO_RIGHT':
            if axis == 'X':
                return base_name + '.R'
            elif axis == 'Y':
                return base_name + '.F'
            elif axis == 'Z':
                return base_name + '.U'
        elif direction == 'FRONT_TO_BACK':
            return base_name + '.B'
        elif direction == 'BACK_TO_FRONT':
            return base_name + '.F'
        elif direction == 'UP_TO_DOWN':
            return base_name + '.D'
        elif direction == 'DOWN_TO_UP':
            return base_name + '.U'
        
        # Fallback to default behavior
        from ..utils.naming import get_opposite_name
        return get_opposite_name(name, axis)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "mirror_axis")
        layout.prop(self, "apply_transforms")
        layout.prop(self, "auto_rename")
        layout.prop(self, "keep_original_selected")


# Registration
classes = (
    OBJECT_OT_flip_mesh,
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