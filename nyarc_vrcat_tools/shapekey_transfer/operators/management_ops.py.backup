# Management Operators
# Operators for shape key list management and UI control

import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

from ..utils.mesh_utils import ensure_surface_deform_compatibility
from ..utils.validation import validate_mesh_for_surface_deform


class MESH_OT_update_shape_key_list(Operator):
    """Update the shape key selection list based on the source object"""
    bl_idname = "mesh.update_shapekey_list"
    bl_label = "Update Shape Key List"
    bl_description = "Refresh the shape key list from the source object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        props.update_shape_key_selections(context)
        
        key_count = len(props.shapekey_selected_keys)
        if key_count > 0:
            self.report({'INFO'}, f"Updated shape key list ({key_count} keys found)")
        else:
            self.report({'INFO'}, "No shape keys found in source object")
        
        return {'FINISHED'}


class MESH_OT_select_all_shape_keys(Operator):
    """Select or deselect all shape keys in the list"""
    bl_idname = "mesh.select_all_shapekeys"
    bl_label = "Select All Shape Keys"
    bl_description = "Select or deselect all shape keys"
    bl_options = {'REGISTER', 'UNDO'}
    
    select: BoolProperty(
        name="Select",
        description="True to select all, False to deselect all",
        default=True
    )
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        props.select_all_shape_keys(self.select)
        
        action = "Selected" if self.select else "Deselected"
        self.report({'INFO'}, f"{action} all shape keys")
        return {'FINISHED'}


class MESH_OT_prepare_mesh_compatibility(Operator):
    """Manually prepare a mesh for Surface Deform compatibility"""
    bl_idname = "mesh.prepare_mesh_compatibility"
    bl_label = "Prepare Mesh"
    bl_description = "Prepare the selected mesh for Surface Deform compatibility (triangulate N-gons, fix non-manifold edges)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        active_obj = context.active_object
        
        if not active_obj or active_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}
        
        # Validate first
        is_compatible, issues = validate_mesh_for_surface_deform(active_obj)
        
        if is_compatible:
            self.report({'INFO'}, f"Mesh '{active_obj.name}' is already compatible")
            return {'FINISHED'}
        
        # Show issues found
        self.report({'INFO'}, f"Issues found: {', '.join(issues[:3])}")
        
        # Attempt to fix
        try:
            was_modified = ensure_surface_deform_compatibility(active_obj)
            
            if was_modified:
                # Re-validate
                is_now_compatible, new_issues = validate_mesh_for_surface_deform(active_obj)
                
                if is_now_compatible:
                    self.report({'INFO'}, f"✓ Mesh '{active_obj.name}' prepared successfully")
                    return {'FINISHED'}
                else:
                    self.report({'WARNING'}, f"Partial fix: {', '.join(new_issues[:2])}")
                    return {'FINISHED'}
            else:
                self.report({'INFO'}, f"No modifications needed for '{active_obj.name}'")
                return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to prepare mesh: {str(e)[:50]}")
            return {'CANCELLED'}


def get_classes():
    """Get all management operator classes for registration"""
    return [
        MESH_OT_update_shape_key_list,
        MESH_OT_select_all_shape_keys,
        MESH_OT_prepare_mesh_compatibility,
    ]