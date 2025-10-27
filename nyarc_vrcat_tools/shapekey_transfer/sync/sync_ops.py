# Shape Key Synchronization Operators
# Live preview and value synchronization functionality

import bpy
from bpy.props import StringProperty, FloatProperty
from bpy.types import Operator
from bpy.app.handlers import persistent


class MESH_OT_sync_shape_key_value(Operator):
    """Synchronize a shape key value across source and target meshes with live preview"""
    bl_idname = "mesh.sync_shape_key_value"
    bl_label = "Sync Shape Key Value"
    bl_description = "Synchronize shape key value between source and target meshes (with live preview for targets without transferred keys)"
    bl_options = {'REGISTER', 'UNDO'}
    
    shape_key_name: StringProperty(
        name="Shape Key Name",
        description="Name of the shape key to sync"
    )
    
    shape_key_value: FloatProperty(
        name="Shape Key Value",
        description="Value to set for the shape key",
        default=0.0,
        min=0.0,
        max=1.0
    )
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        if not props.shapekey_sync_enabled:
            return {'FINISHED'}
        
        source_obj = props.shapekey_source_object
        if not source_obj or not source_obj.data.shape_keys:
            return {'FINISHED'}
        
        # Sync to source object first
        if self.shape_key_name in source_obj.data.shape_keys.key_blocks:
            source_obj.data.shape_keys.key_blocks[self.shape_key_name].value = self.shape_key_value
        
        # Update the viewport immediately for source changes
        bpy.context.view_layer.update()
        
        # Get all target objects (both single, multi-target, and viewport selection)
        target_objects = []
        if props.shapekey_target_object:
            target_objects.append(props.shapekey_target_object)
        else:
            # Fallback: Check for viewport-selected mesh
            if context.selected_objects:
                for obj in context.selected_objects:
                    if obj.type == 'MESH' and obj != source_obj:
                        target_objects.append(obj)
                        break  # Only use first valid selection

        target_objects.extend(props.get_target_objects_list())
        target_objects = list(set(target_objects))  # Remove duplicates
        
        # Process each target object
        for target_obj in target_objects:
            if not target_obj:
                continue
            
            # Check if target already has this shape key (transferred)
            if (target_obj.data.shape_keys and 
                self.shape_key_name in target_obj.data.shape_keys.key_blocks):
                # Target has the shape key - sync normally
                target_obj.data.shape_keys.key_blocks[self.shape_key_name].value = self.shape_key_value
            else:
                # Target doesn't have shape key - show info that it needs to be transferred first
                # Live preview without transferred shape keys is very limited
                pass  # Could add visual indicators in UI instead
        
        return {'FINISHED'}
    


class MESH_OT_reset_shape_key_values(Operator):
    """Reset all shape key values to 0.0"""
    bl_idname = "mesh.reset_shape_key_values"
    bl_label = "Reset All Values"
    bl_description = "Reset all shape key values to 0.0"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        source_obj = props.shapekey_source_object
        if not source_obj or not source_obj.data.shape_keys:
            return {'FINISHED'}
        
        # Reset source object shape keys
        for key_block in source_obj.data.shape_keys.key_blocks:
            if key_block.name != "Basis":
                key_block.value = 0.0
        
        # Reset target objects (including viewport selection)
        target_objects = []
        if props.shapekey_target_object:
            target_objects.append(props.shapekey_target_object)
        else:
            # Fallback: Check for viewport-selected mesh
            if context.selected_objects:
                for obj in context.selected_objects:
                    if obj.type == 'MESH' and obj != source_obj:
                        target_objects.append(obj)
                        break

        target_objects.extend(props.get_target_objects_list())
        target_objects = list(set(target_objects))
        
        for target_obj in target_objects:
            if target_obj and target_obj.data.shape_keys:
                for key_block in target_obj.data.shape_keys.key_blocks:
                    if key_block.name != "Basis":
                        key_block.value = 0.0
        
        self.report({'INFO'}, "All shape key values reset to 0.0")
        return {'FINISHED'}


class MESH_OT_clear_live_preview_modifiers(Operator):
    """Clear all temporary preview modifiers from target objects"""
    bl_idname = "mesh.clear_live_preview_modifiers"  
    bl_label = "Clear Preview Modifiers"
    bl_description = "Remove any temporary modifiers created during shape key preview"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        # Get all target objects (including viewport selection)
        target_objects = []
        if props.shapekey_target_object:
            target_objects.append(props.shapekey_target_object)
        else:
            # Fallback: Check for viewport-selected mesh
            if context.selected_objects:
                source_obj = props.shapekey_source_object
                for obj in context.selected_objects:
                    if obj.type == 'MESH' and obj != source_obj:
                        target_objects.append(obj)
                        break

        target_objects.extend(props.get_target_objects_list())
        target_objects = list(set(target_objects))
        
        cleared_count = 0
        for target_obj in target_objects:
            if not target_obj:
                continue
            
            # Find and remove preview-related modifiers
            modifiers_to_remove = []
            for modifier in target_obj.modifiers:
                if (modifier.name.startswith("LivePreview_") or 
                    modifier.name.startswith("PreviewBase_") or
                    modifier.name.startswith("SurfaceDeform_")):
                    modifiers_to_remove.append(modifier)
            
            for modifier in modifiers_to_remove:
                target_obj.modifiers.remove(modifier)
                cleared_count += 1
        
        if cleared_count > 0:
            self.report({'INFO'}, f"Cleared {cleared_count} preview modifier(s)")
        else:
            self.report({'INFO'}, "No preview modifiers found")
        
        return {'FINISHED'}


# Global variables to track previous shape key states
_previous_shape_key_values = {}
_sync_enabled = False


@persistent
def shape_key_sync_handler(scene):
    """Handler that runs on scene updates to sync shape key changes"""
    global _previous_shape_key_values, _sync_enabled
    
    try:
        props = getattr(scene, 'nyarc_tools_props', None)
        if not props or not props.shapekey_sync_enabled:
            _sync_enabled = False
            return
        
        _sync_enabled = True
        source_obj = props.shapekey_source_object
        if not source_obj or not source_obj.data.shape_keys:
            return
        
        # Get target objects (including viewport selection fallback)
        target_objects = []
        if props.shapekey_target_object:
            target_objects.append(props.shapekey_target_object)
        else:
            # Fallback: Check for viewport-selected mesh (matching transfer operator logic)
            import bpy
            if bpy.context.selected_objects:
                for obj in bpy.context.selected_objects:
                    if obj.type == 'MESH' and obj != source_obj:
                        target_objects.append(obj)
                        break  # Only use first valid selection

        target_objects.extend(props.get_target_objects_list())
        target_objects = list(set(target_objects))
        
        if not target_objects:
            return
        
        # Check for shape key value changes
        current_values = {}
        for key_block in source_obj.data.shape_keys.key_blocks:
            if key_block.name != "Basis":
                current_values[key_block.name] = key_block.value
        
        # Compare with previous values and sync changes
        for key_name, current_value in current_values.items():
            previous_value = _previous_shape_key_values.get(key_name, 0.0)
            
            # If value changed, sync to targets
            if abs(current_value - previous_value) > 0.001:  # Small threshold for float comparison
                for target_obj in target_objects:
                    if (target_obj and target_obj.data.shape_keys and 
                        key_name in target_obj.data.shape_keys.key_blocks):
                        target_obj.data.shape_keys.key_blocks[key_name].value = current_value
        
        # Update tracked values
        _previous_shape_key_values = current_values.copy()
        
    except Exception as e:
        # Silent fail to avoid disrupting Blender
        pass


class MESH_OT_toggle_live_sync(Operator):
    """Toggle live shape key synchronization on/off"""
    bl_idname = "mesh.toggle_live_sync"
    bl_label = "Toggle Live Sync"
    bl_description = "Enable/disable automatic shape key synchronization between source and targets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        # Toggle sync enabled state
        props.shapekey_sync_enabled = not props.shapekey_sync_enabled
        
        if props.shapekey_sync_enabled:
            # Add handler if not already present
            if shape_key_sync_handler not in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.append(shape_key_sync_handler)
            self.report({'INFO'}, "Live sync enabled")
        else:
            # Remove handler
            if shape_key_sync_handler in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(shape_key_sync_handler)
            self.report({'INFO'}, "Live sync disabled")
        
        return {'FINISHED'}


def register_handlers():
    """Register shape key sync handlers"""
    if shape_key_sync_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(shape_key_sync_handler)


def unregister_handlers():
    """Unregister shape key sync handlers"""
    if shape_key_sync_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(shape_key_sync_handler)


def get_classes():
    """Get all sync operator classes for registration"""
    return [
        MESH_OT_sync_shape_key_value,
        MESH_OT_reset_shape_key_values,
        MESH_OT_clear_live_preview_modifiers,
        MESH_OT_toggle_live_sync,
    ]