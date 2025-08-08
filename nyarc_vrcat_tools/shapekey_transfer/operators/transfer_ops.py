# Core Shape Key Transfer Operators
# Main transfer functionality and core operations

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

from ..utils.mesh_utils import sanitize_display_name, ensure_surface_deform_compatibility, get_unique_shape_key_name
from ..utils.validation import validate_mesh_for_surface_deform


def transfer_shape_key_direct(operator, source_obj, target_obj, shape_key_name, override_existing=False, skip_existing=False):
    """Direct shape key transfer function that can be called without operator instantiation"""
    modifier_name = None
    original_values = {}
    original_mode = None
    original_active = None
    original_selected = []
    
    try:
        # Store original context
        original_mode = bpy.context.mode
        original_active = bpy.context.active_object
        original_selected = bpy.context.selected_objects.copy()
        
        # Ensure we're in Object mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Validate objects and shape key
        if not source_obj.data.shape_keys:
            operator.report({'ERROR'}, "Source object has no shape keys")
            return False
        
        if shape_key_name not in source_obj.data.shape_keys.key_blocks:
            operator.report({'ERROR'}, f"Shape key '{shape_key_name}' not found")
            return False
        
        # Check if target already has this shape key
        target_has_shape_key = (target_obj.data.shape_keys and 
                              target_obj.data.shape_keys.key_blocks and
                              shape_key_name in target_obj.data.shape_keys.key_blocks)
        
        if target_has_shape_key:
            if skip_existing:
                operator.report({'INFO'}, f"Skipping '{shape_key_name}' - already exists on '{target_obj.name}'")
                return "SKIPPED"
            elif override_existing:
                # Remove existing shape key
                target_shape_key = target_obj.data.shape_keys.key_blocks[shape_key_name]
                target_obj.shape_key_remove(target_shape_key)
                operator.report({'INFO'}, f"Overriding existing shape key '{shape_key_name}' on '{target_obj.name}'")
            # If neither skip nor override, continue with normal behavior (create unique name)
        
        shape_keys = source_obj.data.shape_keys.key_blocks
        
        # Store and reset all shape key values - bind in rest state
        for key in shape_keys:
            original_values[key.name] = key.value
            key.value = 0.0
        
        # Update to ensure source is in rest state for binding
        bpy.context.view_layer.update()
        
        # Add Surface Deform modifier to target
        modifier_name = f"SurfaceDeform_{shape_key_name}"
        surface_deform = target_obj.modifiers.new(name=modifier_name, type='SURFACE_DEFORM')
        surface_deform.target = source_obj
        
        # Set active and selected objects for binding
        bpy.context.view_layer.objects.active = target_obj
        target_obj.select_set(True)
        source_obj.select_set(False)
        
        # Bind the Surface Deform modifier
        operator.report({'INFO'}, f"Binding Surface Deform - Source: {source_obj.name}, Target: {target_obj.name}")
        
        try:
            if bpy.app.version >= (3, 2, 0):
                with bpy.context.temp_override(object=target_obj):
                    bpy.ops.object.surfacedeform_bind(modifier=modifier_name)
            else:
                bpy.ops.object.surfacedeform_bind(modifier=modifier_name)
                
            bpy.context.view_layer.update()
                
        except Exception as e:
            operator.report({'ERROR'}, f"Surface Deform binding failed: {str(e)}")
            target_obj.modifiers.remove(surface_deform)
            return False
        
        # Switch to source mesh to set shape key
        bpy.context.view_layer.objects.active = source_obj
        source_obj.select_set(True)
        target_obj.select_set(False)
        
        # Set the target shape key to 1.0
        shape_keys[shape_key_name].value = 1.0
        bpy.context.view_layer.update()
        
        # Switch back to target mesh for application
        bpy.context.view_layer.objects.active = target_obj
        target_obj.select_set(True)
        source_obj.select_set(False)
        
        # Apply as shape key
        try:
            bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier_name)
            operator.report({'INFO'}, "Modifier applied as shape key successfully")
            
            # Rename the created shape key
            if target_obj.data.shape_keys and target_obj.data.shape_keys.key_blocks:
                new_shape_key = target_obj.data.shape_keys.key_blocks[-1]
                
                if override_existing:
                    # When overriding, use the exact original name
                    final_name = shape_key_name
                    new_shape_key.name = final_name
                else:
                    # Normal behavior - get unique name if needed
                    final_name = get_unique_shape_key_name(target_obj, shape_key_name)
                    new_shape_key.name = final_name
                    
                    if final_name != shape_key_name:
                        operator.report({'INFO'}, f"Shape key created as '{final_name}' (original name was taken)")
                        
        except Exception as e:
            operator.report({'ERROR'}, f"Modifier apply as shape key failed: {str(e)}")
            return False
        
        # Restore original shape key values
        for key_name, value in original_values.items():
            if key_name in shape_keys:
                shape_keys[key_name].value = value
        
        bpy.context.view_layer.update()
        return True
            
    except Exception as e:
        operator.report({'ERROR'}, f"Transfer failed: {str(e)[:50]}")
        return False
    finally:
        # Restore original shape key values
        if original_values:
            for key_name, value in original_values.items():
                if key_name in source_obj.data.shape_keys.key_blocks:
                    source_obj.data.shape_keys.key_blocks[key_name].value = value
        
        # Clean up modifier if it still exists
        if modifier_name and modifier_name in target_obj.modifiers:
            target_obj.modifiers.remove(target_obj.modifiers[modifier_name])
        
        # Restore original context completely
        try:
            # Ensure we're in object mode first
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for selected_obj in original_selected:
                if selected_obj:
                    selected_obj.select_set(True)
            
            # Restore active object
            if original_active:
                bpy.context.view_layer.objects.active = original_active
            
            # Restore original mode if it wasn't object mode
            if original_mode and original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=original_mode)
        except Exception as restore_error:
            print(f"Error restoring context in transfer: {restore_error}")
            pass


class MESH_OT_transfer_shape_key(Operator):
    """Transfer a single shape key from source to target mesh using Surface Deform modifier"""
    bl_idname = "mesh.transfer_shape_key"
    bl_label = "Transfer Shape Key"
    bl_description = "Transfer the selected shape key using Surface Deform modifier (with automatic mesh compatibility)"
    bl_options = {'REGISTER', 'UNDO'}
    
    override_existing: BoolProperty(
        name="Override Existing",
        description="Replace existing shape keys with the same name",
        default=False
    )
    
    skip_existing: BoolProperty(
        name="Skip Existing", 
        description="Skip transfer if shape key already exists on target",
        default=False
    )
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        source_obj = props.shapekey_source_object
        target_obj = props.shapekey_target_object
        shape_key_name = props.shapekey_shape_key
        
        if not all([source_obj, target_obj, shape_key_name, shape_key_name != "NONE"]):
            self.report({'ERROR'}, "Please select source object, target object, and shape key")
            return {'CANCELLED'}
        
        # Prepare target mesh for compatibility BEFORE starting transfer operations
        try:
            # Store current context to isolate preparation
            current_active = bpy.context.active_object
            current_selected = bpy.context.selected_objects.copy()
            current_mode = bpy.context.mode
            
            # Run mesh preparation in isolated context
            target_compatible, target_issues = validate_mesh_for_surface_deform(target_obj)
            if not target_compatible:
                self.report({'INFO'}, f"Preparing target mesh '{target_obj.name}' for compatibility...")
                target_modified = ensure_surface_deform_compatibility(target_obj)
                if target_modified:
                    self.report({'INFO'}, f"Target mesh '{target_obj.name}' prepared successfully")
            
            # Restore context after preparation
            bpy.ops.object.select_all(action='DESELECT')
            for obj in current_selected:
                if obj:
                    obj.select_set(True)
            if current_active:
                bpy.context.view_layer.objects.active = current_active
            if current_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=current_mode)
                
        except Exception as e:
            self.report({'WARNING'}, f"Could not prepare target '{target_obj.name}': {str(e)[:50]}")
        
        # Perform the transfer using the direct function
        try:
            result = transfer_shape_key_direct(self, source_obj, target_obj, shape_key_name, 
                                             self.override_existing, self.skip_existing)
            
            if result == "SKIPPED":
                safe_name = sanitize_display_name(shape_key_name)
                safe_target = sanitize_display_name(target_obj.name)
                self.report({'INFO'}, f"Skipped '{safe_name}' on '{safe_target}' (already exists)")
                return {'FINISHED'}
            elif result:
                return {'FINISHED'}
            else:
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Transfer failed: {str(e)[:50]}")
            return {'CANCELLED'}


class MESH_OT_batch_transfer_shape_keys(Operator):
    """Transfer selected shape keys to all target meshes in batch"""
    bl_idname = "mesh.batch_transfer_shape_keys"
    bl_label = "Batch Transfer Shape Keys"
    bl_description = "Transfer selected shape keys to all target meshes (with automatic mesh compatibility)"
    bl_options = {'REGISTER', 'UNDO'}
    
    override_existing: BoolProperty(
        name="Override Existing",
        description="Replace existing shape keys with the same name",
        default=False
    )
    
    skip_existing: BoolProperty(
        name="Skip Existing",
        description="Skip transfer if shape key already exists on target",
        default=False
    )
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}
        
        source_obj = props.shapekey_source_object
        if not source_obj:
            self.report({'ERROR'}, "No source object selected")
            return {'CANCELLED'}
        
        # Get target objects and selected shape keys
        target_objects = props.get_target_objects_list()
        if not target_objects:
            self.report({'ERROR'}, "No target objects found")
            return {'CANCELLED'}
        
        selected_shape_keys = props.get_selected_shape_keys()
        if not selected_shape_keys:
            self.report({'ERROR'}, "No shape keys selected")
            return {'CANCELLED'}
        
        # Prepare target meshes for compatibility BEFORE starting batch transfer
        current_active = bpy.context.active_object
        current_selected = bpy.context.selected_objects.copy()  
        current_mode = bpy.context.mode
        
        for target_obj in target_objects:
            try:
                target_compatible, target_issues = validate_mesh_for_surface_deform(target_obj)
                if not target_compatible:
                    self.report({'INFO'}, f"Preparing target mesh '{target_obj.name}' for compatibility...")
                    target_modified = ensure_surface_deform_compatibility(target_obj)
                    if target_modified:
                        self.report({'INFO'}, f"Target mesh '{target_obj.name}' prepared successfully")
            except Exception as e:
                self.report({'WARNING'}, f"Could not prepare target '{target_obj.name}': {str(e)[:50]}")
        
        # Restore context after all preparations
        try:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in current_selected:
                if obj:
                    obj.select_set(True)
            if current_active:
                bpy.context.view_layer.objects.active = current_active
            if current_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=current_mode)
        except Exception as context_error:
            print(f"Error restoring context after batch preparation: {context_error}")
        
        # Perform batch transfer
        successful_transfers = 0
        failed_transfers = 0
        skipped_transfers = 0
        
        for shape_key_name in selected_shape_keys:
            for target_obj in target_objects:
                try:
                    # Call the transfer logic directly with override/skip options
                    result = transfer_shape_key_direct(self, source_obj, target_obj, shape_key_name,
                                                     self.override_existing, self.skip_existing)
                    
                    if result == "SKIPPED":
                        skipped_transfers += 1
                    elif result:
                        successful_transfers += 1
                    else:
                        failed_transfers += 1
                        self.report({'WARNING'}, f"Failed: '{shape_key_name}' → '{target_obj.name}'")
                        
                except Exception as e:
                    failed_transfers += 1
                    self.report({'ERROR'}, f"Error transferring '{shape_key_name}' to '{target_obj.name}': {str(e)[:50]}")
        
        # Report final results
        if successful_transfers > 0 or skipped_transfers > 0:
            result_msg = f"Batch transfer complete: {successful_transfers} successful"
            if skipped_transfers > 0:
                result_msg += f", {skipped_transfers} skipped"
            if failed_transfers > 0:
                result_msg += f", {failed_transfers} failed"
            self.report({'INFO'}, result_msg)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Batch transfer failed: 0 successful, {failed_transfers} failed")
            return {'CANCELLED'}


def get_classes():
    """Get all transfer operator classes for registration"""
    return [
        MESH_OT_transfer_shape_key,
        MESH_OT_batch_transfer_shape_keys,
    ]