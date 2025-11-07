# Core Shape Key Transfer Operators
# Main transfer functionality and core operations

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

from ..utils.mesh_utils import sanitize_display_name, ensure_surface_deform_compatibility, get_unique_shape_key_name, remove_surface_deform_compatibility_modifiers
from ..utils.validation import validate_mesh_for_surface_deform
from ..utils.preprocessing import create_preprocessed_source, cleanup_preprocessed_source
from ..utils.smooth_boundary import generate_smoothing_weights, apply_vertex_group_smoothing, process_partially_moved_islands, paint_averaged_islands_in_mask


def transfer_shape_key_direct(operator, source_obj, target_obj, shape_key_name, override_existing=False, skip_existing=False,
                              surface_deform_strength=1.0, surface_deform_falloff=2.5,
                              smooth_boundary=False, smooth_iterations=3, boundary_width=2,
                              auto_blur_mask=True, blur_iterations=2, partial_island_mode='NONE', partial_island_threshold=0.05):
    """Direct shape key transfer function that can be called without operator instantiation

    Args:
        surface_deform_strength: Surface Deform modifier strength (0.0-1.0, default: 1.0)
        surface_deform_falloff: Surface Deform falloff distance (0.1-16.0, default: 2.5)
    """
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

        # Apply Surface Deform parameters
        surface_deform.strength = surface_deform_strength
        surface_deform.falloff = surface_deform_falloff

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

                # Process partially moved islands if enabled (store results for later)
                averaged_vert_indices = set()
                if partial_island_mode != 'NONE':
                    mode_text = "Excluding" if partial_island_mode == 'EXCLUDE' else "Averaging"
                    operator.report({'INFO'}, f"{mode_text} partially moved islands...")
                    processed_count, averaged_vert_indices = process_partially_moved_islands(
                        target_obj, final_name,
                        mode=partial_island_mode,
                        island_threshold=partial_island_threshold
                    )
                    if processed_count > 0:
                        action_text = "Excluded" if partial_island_mode == 'EXCLUDE' else "Averaged"
                        operator.report({'INFO'}, f"{action_text} {processed_count} partially moved islands")

                # Generate smoothing mask if enabled
                if smooth_boundary:
                    operator.report({'INFO'}, f"Generating smoothing mask for '{final_name}'...")
                    vgroup_name = generate_smoothing_weights(
                        target_obj,
                        final_name,
                        boundary_width=boundary_width,
                        displacement_threshold=0.001,
                        auto_blur=auto_blur_mask,
                        blur_iterations=blur_iterations,
                        island_threshold=partial_island_threshold,
                        partial_island_mode=partial_island_mode
                    )
                    if vgroup_name:
                        operator.report({'INFO'}, f"Smoothing mask '{vgroup_name}' created")

                        # NOW paint averaged islands into the mask (after mask exists)
                        if partial_island_mode == 'AVERAGE' and averaged_vert_indices:
                            # Paint with weight 0.5 (orange/mid-range) so they're visible and distinguishable
                            # User can manually adjust if they want more/less smoothing on these islands
                            paint_averaged_islands_in_mask(target_obj, final_name, averaged_vert_indices, weight=0.5)
                            operator.report({'INFO'}, f"Painted {len(averaged_vert_indices)} averaged vertices in smoothing mask (orange)")

                        print(f"[DEBUG] Returning WEIGHT_PAINT tuple: {vgroup_name}")
                        # Return special marker to signal weight paint mode switch should happen
                        return ("WEIGHT_PAINT", target_obj, vgroup_name)
                    else:
                        operator.report({'WARNING'}, f"No boundary detected for smoothing mask")

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

            # Restore original mode
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

        # Clean up debug visualization from robust transfer if present
        if target_obj and target_obj.type == 'MESH':
            try:
                from ..robust.debug import clear_match_quality_debug
                clear_match_quality_debug(target_obj)
            except (ImportError, Exception):
                pass  # Silently ignore if robust module not available or other errors

        # Fallback: Use selected mesh in viewport if no target is set in dropdown
        if not target_obj and context.selected_objects:
            # Find first selected mesh that isn't the source
            for obj in context.selected_objects:
                if obj.type == 'MESH' and obj != source_obj:
                    target_obj = obj
                    self.report({'INFO'}, f"Using selected mesh '{obj.name}' as target")
                    break

        if not all([source_obj, target_obj, shape_key_name, shape_key_name != "NONE"]):
            self.report({'ERROR'}, "Please select source object, target object (or select in viewport), and shape key")
            return {'CANCELLED'}
        
        # Pre-processing: Create temporary preprocessed source if needed
        working_source, is_temp_source = create_preprocessed_source(
            source_obj, context,
            use_subdivision=props.shapekey_use_subdivision,
            subdivision_levels=props.shapekey_subdivision_levels,
            subdivision_simple=props.shapekey_subdivision_simple,
            use_displace=props.shapekey_use_displace,
            displace_strength=props.shapekey_displace_strength,
            displace_midlevel=props.shapekey_displace_midlevel,
            displace_direction=props.shapekey_displace_direction
        )

        # Prepare BOTH source and target meshes for compatibility BEFORE starting transfer operations
        source_modifiers = []
        target_modifiers = []

        try:
            # Store current context to isolate preparation
            current_active = bpy.context.active_object
            current_selected = bpy.context.selected_objects.copy()
            current_mode = bpy.context.mode

            # Prepare SOURCE mesh (fixes "Target contains concave polygons" warnings)
            source_compatible, source_issues = validate_mesh_for_surface_deform(working_source)
            if not source_compatible:
                self.report({'INFO'}, f"Preparing source mesh '{working_source.name}' for compatibility...")
                source_result = ensure_surface_deform_compatibility(working_source)
                if source_result['modified']:
                    source_modifiers = source_result['modifiers_added']
                    self.report({'INFO'}, f"Source mesh '{working_source.name}' prepared successfully")

            # Prepare TARGET mesh
            target_compatible, target_issues = validate_mesh_for_surface_deform(target_obj)
            if not target_compatible:
                self.report({'INFO'}, f"Preparing target mesh '{target_obj.name}' for compatibility...")
                target_result = ensure_surface_deform_compatibility(target_obj)
                if target_result['modified']:
                    target_modifiers = target_result['modifiers_added']
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
        
        # Perform the transfer using the direct function (with preprocessed source)
        try:
            result = transfer_shape_key_direct(self, working_source, target_obj, shape_key_name,
                                             self.override_existing, self.skip_existing,
                                             props.shapekey_surface_deform_strength,
                                             props.shapekey_surface_deform_falloff,
                                             props.shapekey_smooth_boundary,
                                             props.shapekey_smooth_iterations,
                                             props.shapekey_smooth_boundary_width,
                                             props.shapekey_auto_blur_mask,
                                             props.shapekey_blur_iterations,
                                             props.shapekey_partial_island_mode,
                                             props.shapekey_partial_island_threshold)

            print(f"[DEBUG] Result type: {type(result)}, Value: {result}")

            if result == "SKIPPED":
                safe_name = sanitize_display_name(shape_key_name)
                safe_target = sanitize_display_name(target_obj.name)
                self.report({'INFO'}, f"Skipped '{safe_name}' on '{safe_target}' (already exists)")
                return {'FINISHED'}
            elif isinstance(result, tuple) and result[0] == "WEIGHT_PAINT":
                print(f"[DEBUG] Detected WEIGHT_PAINT tuple, processing...")
                # Special case: Need to switch to weight paint mode
                _, target_for_paint, vgroup_name = result

                # Clean up first (before switching to weight paint mode)
                print(f"[DEBUG] Cleaning up modifiers...")
                if source_modifiers:
                    remove_surface_deform_compatibility_modifiers(working_source, source_modifiers)
                    source_modifiers = []  # Mark as cleaned to prevent double cleanup in finally
                if target_modifiers:
                    remove_surface_deform_compatibility_modifiers(target_obj, target_modifiers)
                    target_modifiers = []  # Mark as cleaned to prevent double cleanup in finally
                if is_temp_source:
                    cleanup_preprocessed_source(working_source, context)
                    is_temp_source = False  # Mark as cleaned to prevent double cleanup in finally

                # Now switch to weight paint mode
                print(f"[DEBUG] Switching to Weight Paint mode...")
                try:
                    bpy.ops.object.select_all(action='DESELECT')
                    target_for_paint.select_set(True)
                    context.view_layer.objects.active = target_for_paint

                    vgroup = target_for_paint.vertex_groups.get(vgroup_name)
                    if vgroup:
                        target_for_paint.vertex_groups.active_index = vgroup.index

                    print(f"[DEBUG] About to call mode_set(WEIGHT_PAINT)...")
                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                    print(f"[DEBUG] Mode set complete. Current mode: {bpy.context.mode}")

                    # Force UI refresh to show Apply Smoothing button
                    for area in context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()

                    self.report({'INFO'}, f"Switched to Weight Paint mode - Edit mask then click 'Apply Smoothing'")
                except Exception as e:
                    print(f"[DEBUG] Exception during mode switch: {e}")
                    self.report({'WARNING'}, f"Transfer complete but couldn't switch to Weight Paint: {str(e)[:50]}")

                return {'FINISHED'}
            elif result:
                return {'FINISHED'}
            else:
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Transfer failed: {str(e)[:50]}")
            return {'CANCELLED'}
        finally:
            # Clean up temporary modifiers BEFORE deleting temp objects
            # This ensures the object still exists when we try to access it
            if source_modifiers:
                remove_surface_deform_compatibility_modifiers(working_source, source_modifiers)
            if target_modifiers:
                remove_surface_deform_compatibility_modifiers(target_obj, target_modifiers)

            # Clean up temporary preprocessed source AFTER modifier cleanup
            if is_temp_source:
                cleanup_preprocessed_source(working_source, context)


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

        # Clean up debug visualization from robust transfer on all target objects
        try:
            from ..robust.debug import clear_match_quality_debug
            for target_obj in target_objects:
                if target_obj and target_obj.type == 'MESH':
                    clear_match_quality_debug(target_obj)
        except (ImportError, Exception):
            pass  # Silently ignore if robust module not available or other errors
        
        selected_shape_keys = props.get_selected_shape_keys()
        if not selected_shape_keys:
            self.report({'ERROR'}, "No shape keys selected")
            return {'CANCELLED'}
        
        # Pre-processing: Create temporary preprocessed source if needed (used for all transfers)
        working_source, is_temp_source = create_preprocessed_source(
            source_obj, context,
            use_subdivision=props.shapekey_use_subdivision,
            subdivision_levels=props.shapekey_subdivision_levels,
            subdivision_simple=props.shapekey_subdivision_simple,
            use_displace=props.shapekey_use_displace,
            displace_strength=props.shapekey_displace_strength,
            displace_midlevel=props.shapekey_displace_midlevel,
            displace_direction=props.shapekey_displace_direction
        )

        # Prepare source and target meshes for compatibility BEFORE starting batch transfer
        current_active = bpy.context.active_object
        current_selected = bpy.context.selected_objects.copy()
        current_mode = bpy.context.mode

        source_modifiers = []
        target_modifiers_dict = {}  # Track modifiers per target object

        # Prepare SOURCE mesh once (used for all transfers)
        try:
            source_compatible, source_issues = validate_mesh_for_surface_deform(working_source)
            if not source_compatible:
                self.report({'INFO'}, f"Preparing source mesh '{working_source.name}' for compatibility...")
                source_result = ensure_surface_deform_compatibility(working_source)
                if source_result['modified']:
                    source_modifiers = source_result['modifiers_added']
                    self.report({'INFO'}, f"Source mesh '{working_source.name}' prepared successfully")
        except Exception as e:
            self.report({'WARNING'}, f"Could not prepare source '{working_source.name}': {str(e)[:50]}")

        # Prepare all TARGET meshes
        for target_obj in target_objects:
            try:
                target_compatible, target_issues = validate_mesh_for_surface_deform(target_obj)
                if not target_compatible:
                    self.report({'INFO'}, f"Preparing target mesh '{target_obj.name}' for compatibility...")
                    target_result = ensure_surface_deform_compatibility(target_obj)
                    if target_result['modified']:
                        target_modifiers_dict[target_obj] = target_result['modifiers_added']
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
                    result = transfer_shape_key_direct(self, working_source, target_obj, shape_key_name,
                                                     self.override_existing, self.skip_existing,
                                                     props.shapekey_surface_deform_strength,
                                                     props.shapekey_surface_deform_falloff,
                                                     props.shapekey_smooth_boundary,
                                                     props.shapekey_smooth_iterations,
                                                     props.shapekey_smooth_boundary_width,
                                                     props.shapekey_auto_blur_mask,
                                                     props.shapekey_blur_iterations,
                                                     props.shapekey_partial_island_mode,
                                                     props.shapekey_partial_island_threshold)
                    
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
        
        # Clean up temporary modifiers AFTER all transfers are complete
        try:
            # Remove source modifiers
            if source_modifiers:
                remove_surface_deform_compatibility_modifiers(working_source, source_modifiers)

            # Remove target modifiers for each target object
            for target_obj, modifiers in target_modifiers_dict.items():
                if modifiers:
                    remove_surface_deform_compatibility_modifiers(target_obj, modifiers)

            # Clean up temporary preprocessed source if created
            if is_temp_source:
                cleanup_preprocessed_source(working_source, context)

        except Exception as cleanup_error:
            self.report({'WARNING'}, f"Could not clean up temporary modifiers: {str(cleanup_error)[:50]}")

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


class MESH_OT_generate_smoothing_mask(Operator):
    """Generate a vertex group mask showing where smoothing should be applied"""
    bl_idname = "mesh.generate_smoothing_mask"
    bl_label = "Generate Smoothing Mask"
    bl_description = "Analyze shape key displacement and create a weight-painted mask for smoothing (red = smooth, blue = preserve)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}

        target_obj = props.shapekey_target_object
        shape_key_name = props.shapekey_shape_key

        # Fallback: Use active object if no target is set
        if not target_obj and context.active_object:
            if context.active_object.type == 'MESH':
                target_obj = context.active_object
                self.report({'INFO'}, f"Using active mesh '{context.active_object.name}' as target")

        if not all([target_obj, shape_key_name, shape_key_name != "NONE"]):
            self.report({'ERROR'}, "Please select target object and shape key")
            return {'CANCELLED'}

        # Clean up debug visualization from robust transfer if present
        if target_obj and target_obj.type == 'MESH':
            try:
                from ..robust.debug import clear_match_quality_debug
                clear_match_quality_debug(target_obj)
            except (ImportError, Exception):
                pass  # Silently ignore if robust module not available or other errors

        # Generate smoothing weights
        vgroup_name = generate_smoothing_weights(
            target_obj,
            shape_key_name,
            boundary_width=props.shapekey_smooth_boundary_width,
            displacement_threshold=0.001,
            auto_blur=props.shapekey_auto_blur_mask,
            blur_iterations=props.shapekey_blur_iterations,
            island_threshold=props.shapekey_partial_island_threshold,
            partial_island_mode=props.shapekey_partial_island_mode
        )

        if not vgroup_name:
            self.report({'ERROR'}, "Failed to generate smoothing mask")
            return {'CANCELLED'}

        # Switch to Weight Paint mode for editing
        try:
            # Ensure we're in object mode first
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            # Select only the target object
            bpy.ops.object.select_all(action='DESELECT')
            target_obj.select_set(True)
            context.view_layer.objects.active = target_obj

            # Set active vertex group
            vgroup = target_obj.vertex_groups.get(vgroup_name)
            if vgroup:
                target_obj.vertex_groups.active_index = vgroup.index

            # Switch to Weight Paint mode
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')

            self.report({'INFO'}, f"Smoothing mask created: '{vgroup_name}' - Edit weights in Weight Paint mode (Red=smooth, Blue=preserve)")

        except Exception as e:
            self.report({'WARNING'}, f"Mask created but couldn't switch to Weight Paint mode: {str(e)[:50]}")

        return {'FINISHED'}


class MESH_OT_apply_smoothing_mask(Operator):
    """Apply Laplacian smoothing to shape key based on vertex group weights"""
    bl_idname = "mesh.apply_smoothing_mask"
    bl_label = "Apply Smoothing"
    bl_description = "Apply Laplacian smoothing to the shape key using the vertex group weights (run after editing mask)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}

        target_obj = props.shapekey_target_object
        shape_key_name = props.shapekey_shape_key

        # Fallback: Use active object if no target is set
        if not target_obj and context.active_object:
            if context.active_object.type == 'MESH':
                target_obj = context.active_object

        if not all([target_obj, shape_key_name, shape_key_name != "NONE"]):
            self.report({'ERROR'}, "Please select target object and shape key")
            return {'CANCELLED'}

        # Clean up debug visualization from robust transfer if present
        if target_obj and target_obj.type == 'MESH':
            try:
                from ..robust.debug import clear_match_quality_debug
                clear_match_quality_debug(target_obj)
            except (ImportError, Exception):
                pass  # Silently ignore if robust module not available or other errors

        # Get vertex group name
        vgroup_name = f"Smooth_{shape_key_name}"
        vgroup = target_obj.vertex_groups.get(vgroup_name)

        if not vgroup:
            self.report({'ERROR'}, f"Vertex group '{vgroup_name}' not found. Generate mask first.")
            return {'CANCELLED'}

        # Store original mode to restore later
        original_mode = context.mode

        # Ensure we're in object mode for shape key modification
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Apply smoothing
        result = apply_vertex_group_smoothing(
            target_obj,
            shape_key_name,
            vgroup_name,
            smooth_iterations=props.shapekey_smooth_iterations
        )

        if result:
            # Ensure shape key is visible (value = 1.0)
            shape_key = target_obj.data.shape_keys.key_blocks.get(shape_key_name)
            if shape_key:
                shape_key.value = 1.0
                print(f"[Apply Smoothing] Set '{shape_key_name}' value to 1.0 for visibility")

            # Force mesh data update
            target_obj.data.update()

            # Force viewport refresh
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

            # Restore original mode
            if original_mode == 'PAINT_WEIGHT':
                try:
                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                except (RuntimeError, TypeError) as e:
                    # Stay in object mode if weight paint fails
                    print(f"Warning: Failed to restore weight paint mode: {e}")

            self.report({'INFO'}, f"Smoothing applied successfully with {props.shapekey_smooth_iterations} iterations")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to apply smoothing")
            return {'CANCELLED'}


class MESH_OT_delete_smoothing_mask(Operator):
    """Delete the smoothing mask vertex group for the current shape key"""
    bl_idname = "mesh.delete_smoothing_mask"
    bl_label = "Delete Mask"
    bl_description = "Delete the smoothing mask vertex group for the current shape key"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Properties not found")
            return {'CANCELLED'}

        # Get target object (dropdown or active)
        target_obj = props.shapekey_target_object
        shape_key_name = props.shapekey_shape_key

        # Fallback to active object
        if not target_obj and context.active_object:
            if context.active_object.type == 'MESH':
                target_obj = context.active_object

        if not all([target_obj, shape_key_name, shape_key_name != "NONE"]):
            self.report({'ERROR'}, "Please select target object and shape key")
            return {'CANCELLED'}

        # Get vertex group name
        vgroup_name = f"Smooth_{shape_key_name}"
        vgroup = target_obj.vertex_groups.get(vgroup_name)

        if not vgroup:
            self.report({'WARNING'}, f"No mask found for '{shape_key_name}'")
            return {'CANCELLED'}

        # Store current mode to check if we need to exit weight paint
        current_mode = context.mode

        # Delete the vertex group
        target_obj.vertex_groups.remove(vgroup)
        self.report({'INFO'}, f"Deleted smoothing mask '{vgroup_name}'")

        # Exit weight paint mode if currently in it (return to object mode)
        if current_mode == 'PAINT_WEIGHT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except (RuntimeError, TypeError) as e:
                print(f"Warning: Failed to exit weight paint mode: {e}")

        # Force UI refresh
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        return {'FINISHED'}


def get_classes():
    """Get all transfer operator classes for registration"""
    return [
        MESH_OT_transfer_shape_key,
        MESH_OT_batch_transfer_shape_keys,
        MESH_OT_generate_smoothing_mask,
        MESH_OT_apply_smoothing_mask,
        MESH_OT_delete_smoothing_mask,
    ]