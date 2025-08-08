# Target Management Operators
# Operators for managing target objects in multi-target mode

import bpy
from bpy.props import IntProperty
from bpy.types import Operator


class MESH_OT_add_target_object(Operator):
    """Add currently selected object as a target for batch transfer"""
    bl_idname = "mesh.add_target_object"
    bl_label = "Add Target Object"
    bl_description = "Add the active object as a target for batch shape key transfer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        active_obj = context.active_object
        if not active_obj:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        
        if active_obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object is not a mesh")
            return {'CANCELLED'}
        
        # Check if object is already the source
        if active_obj == props.shapekey_source_object:
            self.report({'ERROR'}, "Cannot add source object as target")
            return {'CANCELLED'}
        
        # Try to add the target
        if props.add_target_object(active_obj):
            self.report({'INFO'}, f"Added '{active_obj.name}' as target")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"'{active_obj.name}' is already in target list")
            return {'CANCELLED'}


class MESH_OT_remove_target_object(Operator):
    """Remove a target object from the batch transfer list"""
    bl_idname = "mesh.remove_target_object"
    bl_label = "Remove Target Object"
    bl_description = "Remove this target object from the batch transfer list"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty(
        name="Index",
        description="Index of the target object to remove"
    )
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        if props.remove_target_object(self.index):
            self.report({'INFO'}, "Target object removed")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to remove target object")
            return {'CANCELLED'}


class MESH_OT_clear_target_objects(Operator):
    """Clear all target objects from the batch transfer list"""
    bl_idname = "mesh.clear_target_objects"
    bl_label = "Clear All Targets"
    bl_description = "Remove all target objects from the batch transfer list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        props.clear_target_objects()
        self.report({'INFO'}, "All target objects cleared")
        return {'FINISHED'}


def get_classes():
    """Get all target management operator classes for registration"""
    return [
        MESH_OT_add_target_object,
        MESH_OT_remove_target_object,
        MESH_OT_clear_target_objects,
    ]