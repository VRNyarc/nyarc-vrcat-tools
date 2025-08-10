# Target Management Operators
# Operators for managing target objects in multi-target mode

import bpy
from bpy.props import IntProperty
from bpy.types import Operator


class MESH_OT_add_target_object(Operator):
    """Add all selected mesh objects as targets for batch transfer"""
    bl_idname = "mesh.add_target_object"
    bl_label = "Add Target Objects"
    bl_description = "Add all selected mesh objects as targets for batch shape key transfer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        # Get all selected objects
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        # Filter out source object and process each selected mesh
        valid_objects = []
        skipped_objects = []
        duplicate_objects = []
        
        for obj in selected_objects:
            # Check if object is already the source
            if obj == props.shapekey_source_object:
                skipped_objects.append(obj.name)
                continue
            
            # Try to add the target
            if props.add_target_object(obj):
                valid_objects.append(obj.name)
            else:
                duplicate_objects.append(obj.name)
        
        # Report results
        if valid_objects:
            if len(valid_objects) == 1:
                self.report({'INFO'}, f"Added '{valid_objects[0]}' as target")
            else:
                self.report({'INFO'}, f"Added {len(valid_objects)} targets: {', '.join(valid_objects[:3])}")
            
            # Additional info for skipped/duplicate objects
            if skipped_objects:
                self.report({'WARNING'}, f"Skipped source object(s): {', '.join(skipped_objects)}")
            if duplicate_objects:
                self.report({'WARNING'}, f"Already in target list: {', '.join(duplicate_objects[:3])}")
                
            return {'FINISHED'}
        else:
            # No objects were added
            if skipped_objects and duplicate_objects:
                self.report({'WARNING'}, "No new targets added - objects were source or already in list")
            elif skipped_objects:
                self.report({'WARNING'}, "Cannot add source object(s) as targets")
            elif duplicate_objects:
                self.report({'WARNING'}, "All selected objects already in target list")
            else:
                self.report({'ERROR'}, "No valid objects to add")
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