# Main Shape Key Transfer Panel
# Primary UI layout and drawing functions

import bpy
from .preview_ui import draw_live_preview_ui


def _get_shape_key_status_on_targets(props, shape_key_name):
    """Get detailed status of shape key across all target meshes
    
    Returns:
        "all" - All target meshes have this shape key
        "some" - Some target meshes have it, others don't  
        "none" - No target meshes have this shape key
    """
    if not props:
        return "none"
    
    # Get all target objects
    target_objects = []
    if props.shapekey_target_object:
        target_objects.append(props.shapekey_target_object)
    target_objects.extend(props.get_target_objects_list())
    
    if not target_objects:
        return "none"
    
    # Count how many targets have the shape key
    targets_with_key = 0
    for target_obj in target_objects:
        if (target_obj and target_obj.data.shape_keys and 
            target_obj.data.shape_keys.key_blocks and
            shape_key_name in target_obj.data.shape_keys.key_blocks):
            targets_with_key += 1
    
    total_targets = len(target_objects)
    
    if targets_with_key == 0:
        return "none"
    elif targets_with_key == total_targets:
        return "all"
    else:
        return "some"


def draw_ui(layout, context):
    """Draw the Shape Key Transfer UI content (called from modules.py)"""
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        layout.label(text="Nyarc Tools properties not found!", icon='ERROR')
        return
    
    # Mode toggle
    layout.prop(props, "shapekey_multi_mode", text="Multi-Target Mode", icon='OUTLINER_OB_GROUP_INSTANCE')
    
    # Source object selector (reduced spacing)
    layout.separator(factor=0.5)
    layout.label(text="Source Mesh (with shape keys):")
    layout.prop(props, "shapekey_source_object", text="")
    
    # Shape key refresh control
    if props.shapekey_source_object:
        row = layout.row()
        row.label(text="Shape Keys:")
        row.operator("mesh.update_shapekey_list", text="", icon='FILE_REFRESH')
    
    # Mode-specific UI (reduced spacing)
    layout.separator(factor=0.5)
    if props.shapekey_multi_mode:
        draw_multi_target_ui(layout, context, props)
    else:
        draw_single_target_ui(layout, context, props)
    
    # Live Preview Section
    if props.shapekey_source_object:
        draw_live_preview_ui(layout, context, props)
        
        # Help section moved here - below live preview
        draw_help_section(layout, context, multi_mode=props.shapekey_multi_mode)


def draw_single_target_ui(layout, context, props):
    """Draw single target mode UI (legacy mode)"""
    # Target object selector
    layout.label(text="Target Mesh:")

    # Get viewport-selected target if dropdown is empty
    viewport_target = None
    if not props.shapekey_target_object and context.selected_objects:
        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj != props.shapekey_source_object:
                viewport_target = obj
                break

    # Show the dropdown field
    layout.prop(props, "shapekey_target_object", text="")

    # Show viewport selection info inside a box below the dropdown
    if not props.shapekey_target_object and viewport_target:
        info_box = layout.box()
        info_row = info_box.row()
        info_row.label(text=f"Using selected: {viewport_target.name}", icon='OUTLINER_OB_MESH')

    # Shape key selector (only show if source is selected)
    if props.shapekey_source_object:
        layout.label(text="Shape Key to Transfer:")
        layout.prop(props, "shapekey_shape_key", text="")

    layout.separator(factor=0.5)

    # Determine actual target (dropdown or viewport)
    actual_target = props.shapekey_target_object or viewport_target

    # Transfer button - show if we have source, target (dropdown OR viewport), and shape key
    if (props.shapekey_source_object and actual_target and
        props.shapekey_shape_key and props.shapekey_shape_key != "NONE"):
        
        # Check if smoothing mask exists for current shape key
        shape_key_name = props.shapekey_shape_key
        vgroup_name = f"Smooth_{shape_key_name}"
        mask_exists = vgroup_name in actual_target.vertex_groups if actual_target else False

        # Transfer button row
        row = layout.row(align=True)
        row.scale_y = 1.5

        # Choose operator based on robust mode toggle
        if props.shapekey_use_robust_transfer:
            # ROBUST TRANSFER MODE
            transfer_op = row.operator("mesh.transfer_shape_key_robust", text="Robust Transfer Shape Key", icon='SMOOTHCURVE')
            # Properties are read from scene props directly in the operator
        else:
            # LEGACY TRANSFER MODE
            # Main transfer button (75% width if mask exists)
            if mask_exists and props.shapekey_smooth_boundary:
                col = row.column(align=True)
                col.scale_x = 3.0  # 75% width
                transfer_op = col.operator("mesh.transfer_shape_key", text="Transfer + Generate Mask", icon='VPAINT_HLT')
                transfer_op.override_existing = props.shapekey_override_existing
                transfer_op.skip_existing = props.shapekey_skip_existing

                # Delete Mask button (25% width)
                col = row.column(align=True)
                col.scale_x = 1.0  # 25% width
                col.operator("mesh.delete_smoothing_mask", text="Delete Mask", icon='TRASH')
            else:
                # Full width transfer button
                if props.shapekey_smooth_boundary:
                    transfer_op = row.operator("mesh.transfer_shape_key", text="Transfer + Generate Mask", icon='VPAINT_HLT')
                else:
                    transfer_op = row.operator("mesh.transfer_shape_key", text="Transfer Shape Key", icon='SHAPEKEY_DATA')
                transfer_op.override_existing = props.shapekey_override_existing
                transfer_op.skip_existing = props.shapekey_skip_existing

        # Show Apply Smoothing button after transfer if mask exists (LEGACY MODE ONLY)
        if mask_exists and props.shapekey_smooth_boundary and not props.shapekey_use_robust_transfer:
            row = layout.row()
            row.scale_y = 1.3
            row.alert = True  # Make button red
            row.operator("mesh.apply_smoothing_mask", text="Apply Smoothing", icon='SMOOTHCURVE')
        
        # Transfer options below the button
        layout.separator(factor=0.3)
        options_box = layout.box()
        options_box.label(text="Transfer Options:", icon='PREFERENCES')
        
        # Robust Transfer Toggle
        col = options_box.column()
        col.prop(props, "shapekey_use_robust_transfer", text="Use Robust Transfer (Harmonic Inpainting)")

        # Skip/Override options (available in BOTH modes)
        layout.separator(factor=0.2)
        skip_override_col = options_box.column()
        skip_override_col.prop(props, "shapekey_skip_existing", text="Skip Existing Shape Keys")
        skip_override_col.prop(props, "shapekey_override_existing", text="Override Existing Shape Keys")

        # Warning if both are selected (shouldn't happen with mutual exclusion, but just in case)
        if props.shapekey_override_existing and props.shapekey_skip_existing:
            skip_override_col.label(text="⚠️ Both enabled - Skip takes priority", icon='ERROR')

        # Conditional UI based on robust toggle
        if props.shapekey_use_robust_transfer:
            # Check if dependencies are available
            from ..robust import DEPENDENCIES_AVAILABLE, get_missing_dependencies
            
            layout.separator(factor=0.3)
            robust_box = layout.box()
            robust_header = robust_box.row()
            robust_header.label(text="Robust Transfer Settings", icon='SMOOTHCURVE')
            
            # Show installer if dependencies missing
            if not DEPENDENCIES_AVAILABLE:
                missing = get_missing_dependencies()
                warning_box = robust_box.box()
                warning_col = warning_box.column(align=True)
                warning_col.alert = True
                warning_col.label(text=f"Missing dependencies: {', '.join(missing)}", icon='ERROR')
                warning_col.label(text="Install required libraries to use Robust Transfer")
                warning_col.separator()
                install_row = warning_col.row()
                install_row.scale_y = 1.5
                install_row.operator("mesh.install_robust_dependencies", text="Install Dependencies", icon='IMPORT')
                warning_col.separator(factor=0.5)
                info_col = warning_col.column(align=True)
                info_col.scale_y = 0.7
                info_col.label(text="This will download scipy and robust-laplacian", icon='INFO')
                info_col.label(text="Takes ~30-60 seconds, restart Blender after")
                return  # Don't show settings if deps missing
            
            robust_col = robust_box.column(align=True)
            robust_col.scale_y = 0.9
            
            # Distance threshold with auto-tune
            dist_row = robust_col.row(align=True)
            dist_row.prop(props, "robust_distance_threshold", text="Distance Threshold", slider=True)
            dist_row.operator("mesh.auto_tune_distance_threshold", text="", icon='AUTO')

            # Normal threshold
            robust_col.prop(props, "robust_normal_threshold", text="Normal Threshold", slider=True)

            # Point cloud option
            robust_col.prop(props, "robust_use_pointcloud", text="Use Point Cloud Laplacian")

            # Post-smoothing
            robust_col.prop(props, "robust_smooth_iterations", text="Post-Smooth Iterations", slider=True)

            robust_col.separator()

            # Island handling (fully automatic, just a checkbox)
            robust_col.prop(props, "robust_handle_islands", text="Auto-Handle Unmatched Islands (Buttons, Patches)")

            robust_col.separator()

            # Debug visualization
            robust_col.prop(props, "robust_show_debug", text="Show Match Quality Debug")
            
            # Info box
            info_box = robust_box.box()
            info_col = info_box.column(align=True)
            info_col.scale_y = 0.7
            info_col.label(text="Robust Transfer uses harmonic inpainting for smooth boundaries", icon='INFO')
            info_col.label(text="Blue=perfect, Green=good, Yellow=acceptable, Red=inpainted")

        else:
            # LEGACY MODE: Show Advanced Options (collapsible)
            layout.separator(factor=0.3)
            advanced_box = layout.box()
            advanced_header = advanced_box.row()
            advanced_header.prop(props, "shapekey_show_advanced",
                                icon='TRIA_DOWN' if props.shapekey_show_advanced else 'TRIA_RIGHT',
                                icon_only=True, emboss=False)
            advanced_header.label(text="Advanced Options", icon='PREFERENCES')

            if props.shapekey_show_advanced:
                advanced_col = advanced_box.column(align=True)
                advanced_col.scale_y = 0.9

                # Surface Deform Parameters Section
                surface_deform_box = advanced_col.box()
                surface_deform_box.label(text="Surface Deform Parameters", icon='MOD_MESHDEFORM')

                # Strength control
                strength_col = surface_deform_box.column(align=True)
                strength_label = strength_col.row()
                strength_label.scale_y = 0.8
                strength_label.label(text="Strength (0.0 - 1.0): Overall influence of deformation", icon='FORCE_FORCE')
                strength_col.prop(props, "shapekey_surface_deform_strength", text="", slider=True)

                surface_deform_box.separator(factor=0.3)

                # Falloff control
                falloff_col = surface_deform_box.column(align=True)
                falloff_label = falloff_col.row()
                falloff_label.scale_y = 0.8
                falloff_label.label(text="Falloff (0.1 - 16.0): Interpolation smoothness (lower = smoother)", icon='SMOOTHCURVE')
                falloff_col.prop(props, "shapekey_surface_deform_falloff", text="", slider=True)

                advanced_col.separator(factor=1.5)

                # Post-Transfer Smoothing Section (between Surface Deform and Pre-processing)
                smoothing_box = advanced_col.box()
                smoothing_box.label(text="Post-Transfer Smoothing", icon='MOD_SMOOTH')

                smoothing_col = smoothing_box.column(align=True)
                smoothing_col.scale_y = 0.9

                # Checkbox to enable smoothing
                smoothing_col.prop(props, "shapekey_smooth_boundary", text="Auto-Generate Smoothing Mask")

                if props.shapekey_smooth_boundary:
                    smooth_settings = smoothing_col.box()

                    # Boundary width slider
                    width_label = smooth_settings.row()
                    width_label.scale_y = 0.8
                    width_label.label(text="Boundary Width (1 - 10 rings):", icon='MESH_GRID')
                    smooth_settings.prop(props, "shapekey_smooth_boundary_width", text="", slider=True)

                    smooth_settings.separator(factor=0.3)

                    # Iterations slider
                    iter_label = smooth_settings.row()
                    iter_label.scale_y = 0.8
                    iter_label.label(text="Smoothing Iterations (1 - 10):", icon='PREFERENCES')
                    smooth_settings.prop(props, "shapekey_smooth_iterations", text="", slider=True)

                    smooth_settings.separator(factor=0.3)

                    # Auto-blur option
                    smooth_settings.prop(props, "shapekey_auto_blur_mask", text="Auto-Blur Mask (Recommended)")

                    if props.shapekey_auto_blur_mask:
                        blur_label = smooth_settings.row()
                        blur_label.scale_y = 0.8
                        blur_label.label(text="Blur Iterations (1 - 5):", icon='SMOOTHCURVE')
                        smooth_settings.prop(props, "shapekey_blur_iterations", text="", slider=True)

                    smooth_settings.separator(factor=0.5)

                    # Workflow info
                    info_col = smooth_settings.column(align=True)
                    info_col.scale_y = 0.7
                    info_col.label(text="Workflow:", icon='INFO')
                    info_col.label(text="1. 'Transfer + Generate Mask' creates mask + Weight Paint mode")
                    info_col.label(text="2. Edit mask: Paint/blur weights, exclude unwanted areas")
                    info_col.label(text="3. Red 'Apply Smoothing' button appears below transfer button")

                advanced_col.separator(factor=1.5)

                # Partial Island Handling Section (between smoothing and pre-processing)
                island_box = advanced_col.box()
                island_box.label(text="Partial Island Handling (WIP)", icon='MESH_CUBE')

                island_col = island_box.column(align=True)
                island_col.scale_y = 0.9

                # Description
                desc_col = island_col.column(align=True)
                desc_col.scale_y = 0.8
                desc_col.label(text="Handle small mesh islands that are partially deformed", icon='INFO')
                desc_col.label(text="(buttons, belts, small details)")

                island_col.separator(factor=0.3)

                # Mode dropdown
                island_col.label(text="Mode:", icon='PREFERENCES')
                island_col.prop(props, "shapekey_partial_island_mode", text="")

                island_col.separator(factor=0.3)

                # Island size threshold (always visible, controls both mask generation and island processing)
                threshold_label = island_col.row()
                threshold_label.scale_y = 0.8
                threshold_label.label(text="Island Size Threshold (0.005 - 0.20):", icon='MESH_GRID')
                island_col.prop(props, "shapekey_partial_island_threshold", text="", slider=True)

                threshold_info = island_col.column(align=True)
                threshold_info.scale_y = 0.6
                threshold_info.label(text="Max % of mesh to qualify as small island (0.05 = 5%)", icon='INFO')

                # Explain that this affects both systems when mode != NONE
                if props.shapekey_partial_island_mode != 'NONE':
                    threshold_info.label(text="Affects: Smoothing mask generation + partial island processing", icon='LINKED')
                else:
                    threshold_info.label(text="Island detection disabled when mode = NONE", icon='INFO')

                # Mode-specific info
                if props.shapekey_partial_island_mode != 'NONE':
                    island_col.separator(factor=0.3)

                    mode_info = island_col.box()
                    mode_info_col = mode_info.column(align=True)
                    mode_info_col.scale_y = 0.75

                    if props.shapekey_partial_island_mode == 'EXCLUDE':
                        mode_info_col.label(text="EXCLUDE Mode:", icon='PANEL_CLOSE')
                        mode_info_col.label(text="• Resets partially moved islands to basis shape")
                        mode_info_col.label(text="• Preserves original mesh for small details")
                        mode_info_col.label(text="• Use when buttons/accessories get distorted")
                    elif props.shapekey_partial_island_mode == 'AVERAGE':
                        mode_info_col.label(text="AVERAGE Mode:", icon='ORIENTATION_GLOBAL')
                        mode_info_col.label(text="• Applies uniform displacement to entire island")
                        mode_info_col.label(text="• Moves buttons/details together as a unit")
                        mode_info_col.label(text="• Keeps mesh intact, may need manual adjustment")

                advanced_col.separator(factor=1.5)

                # Pre-processing Modifiers Section (at bottom)
                preprocessing_box = advanced_col.box()
                preprocessing_box.label(text="Pre-processing Modifiers (EXPERIMENTAL)", icon='ERROR')

                preprocessing_col = preprocessing_box.column(align=True)
                preprocessing_col.scale_y = 0.9

                # Info text
                info_row = preprocessing_col.row()
                info_row.scale_y = 0.8
                info_row.label(text="Works on temporary copy - original mesh unchanged", icon='INFO')

                preprocessing_col.separator(factor=0.5)

                # Subdivision options
                subdiv_row = preprocessing_col.row()
                subdiv_row.prop(props, "shapekey_use_subdivision", text="Subdivision Surface")
                if props.shapekey_use_subdivision:
                    subdiv_settings = preprocessing_col.box()
                    subdiv_settings.prop(props, "shapekey_subdivision_levels", text="Levels", slider=True)

                    # Simple subdivision with explanation
                    simple_row = subdiv_settings.row()
                    simple_row.prop(props, "shapekey_subdivision_simple", text="Simple Subdivision")
                    simple_info = subdiv_settings.row()
                    simple_info.scale_y = 0.7
                    simple_info.label(text="(Use for hard edges/mechanical parts)", icon='INFO')

                preprocessing_col.separator(factor=0.3)

                # Displace options
                displace_row = preprocessing_col.row()
                displace_row.prop(props, "shapekey_use_displace", text="Displace")
                if props.shapekey_use_displace:
                    displace_settings = preprocessing_col.box()

                    # Strength with slider showing min/max
                    strength_row = displace_settings.row()
                    strength_row.label(text="Strength (0.0 - 1.0):")
                    displace_settings.prop(props, "shapekey_displace_strength", text="", slider=True)

                    # Midlevel with slider showing min/max
                    midlevel_row = displace_settings.row()
                    midlevel_row.label(text="Midlevel (0.0 - 1.0):")
                    displace_settings.prop(props, "shapekey_displace_midlevel", text="", slider=True)

                    # Direction
                    displace_settings.prop(props, "shapekey_displace_direction", text="Direction")

    else:
        layout.label(text="Select source, target, and shape key", icon='INFO')


def draw_multi_target_ui(layout, context, props):
    """Draw multi-target mode UI with batch operations"""
    # Target management section
    targets_box = layout.box()
    targets_header = targets_box.row()
    targets_header.label(text="Target Meshes:", icon='OUTLINER_OB_MESH')
    targets_header.operator("mesh.add_target_object", text="", icon='ADD')
    targets_header.operator("mesh.clear_target_objects", text="", icon='TRASH')
    
    # Show current targets as individual drag & drop fields (like source mesh)
    for i, target_item in enumerate(props.shapekey_target_objects):
        if target_item.target_object:
            row = targets_box.row()
            # Drag & drop field for existing target
            row.prop(target_item, "target_object", text="")
            # Remove button
            remove_op = row.operator("mesh.remove_target_object", text="", icon='X')
            remove_op.index = i
    
    # Always show empty drag & drop field at bottom (like source mesh)
    empty_row = targets_box.row()
    empty_row.prop(props, "temp_target_object", text="")
    # Plus button for multi-select
    empty_row.operator("mesh.add_target_object", text="", icon='ADD')
    
    # Compact tip
    if len(props.shapekey_target_objects) == 0:
        tip_row = targets_box.row()
        tip_row.scale_y = 0.7
        tip_row.label(text="💡 Multi-select meshes + click plus", icon='INFO')
    
    layout.separator(factor=0.5)
    
    # Shape key selection section
    keys_box = layout.box()
    keys_header = keys_box.row()
    keys_header.label(text="Shape Keys to Transfer:", icon='SHAPEKEY_DATA')
    
    # Legend for visual indicators (when there are targets to check against)
    target_objects = props.get_target_objects_list()
    if len(target_objects) > 1:  # Only show legend for multi-target scenarios
        legend_row = keys_box.row()
        legend_row.scale_y = 0.7
        legend_row.label(text="Normal=All have it  Color icon=Some have it  Red=None have it", icon='INFO')
    
    # Selection controls
    if len(props.shapekey_selected_keys) > 0:
        select_row = keys_header.row()
        select_all_op = select_row.operator("mesh.select_all_shapekeys", text="", icon='CHECKBOX_HLT')
        select_all_op.select = True
        select_none_op = select_row.operator("mesh.select_all_shapekeys", text="", icon='CHECKBOX_DEHLT')
        select_none_op.select = False
        
        # Show shape key checkboxes with scrollable list
        if len(props.shapekey_selected_keys) > 0:
            # Create scrollable list for shape keys (limit to 10 visible items)
            max_visible_rows = 10
            if len(props.shapekey_selected_keys) > max_visible_rows:
                # Use template_list for scrollable interface
                keys_box.template_list(
                    "SHAPEKEY_UL_selection_list", "",
                    props, "shapekey_selected_keys",
                    props, "shapekey_active_index",
                    rows=max_visible_rows,
                    maxrows=max_visible_rows,
                    type='DEFAULT'
                )
            else:
                # Use simple column layout for smaller lists
                col = keys_box.column(align=True)
                for key_item in props.shapekey_selected_keys:
                    row = col.row()
                    
                    # Check detailed status of shape key on targets
                    shape_key_status = _get_shape_key_status_on_targets(props, key_item.name)
                    
                    # Visual indicators based on target status  
                    if shape_key_status == "all":
                        # Normal white text - all targets have it
                        row.prop(key_item, "selected", text=key_item.name)
                    elif shape_key_status == "some":
                        # Yellow warning triangle for partial coverage
                        # Split the row to show checkbox + yellow warning icon + text separately
                        row.prop(key_item, "selected", text="")
                        icon_row = row.row()
                        # Test different sequence colors to find yellow
                        # icon_row.label(text=key_item.name, icon='INFO')        # Yellow triangle with !
                        # icon_row.label(text=key_item.name, icon='SEQUENCE_COLOR_01')  # Try color 1
                        icon_row.label(text=key_item.name, icon='SEQUENCE_COLOR_02')  # Try color 2 (might be yellow)
                        # icon_row.label(text=key_item.name, icon='SEQUENCE_COLOR_04')  # Try color 4
                    else:  # "none"
                        # Red text - no targets have it
                        row.alert = True
                        row.prop(key_item, "selected", text=key_item.name)
        else:
            keys_box.label(text="Click refresh button to load shape keys", icon='INFO')
    
    layout.separator(factor=0.5)
    
    # Batch transfer section
    batch_box = layout.box()
    batch_box.label(text="Batch Transfer:", icon='MOD_ARRAY')
    
    # Show summary
    if props.shapekey_source_object:
        summary = props.get_batch_transfer_summary()
        batch_box.label(text=f"Batch Summary: {summary}", icon='INFO')
    
    # Batch transfer button (simplified)
    targets = props.get_target_objects_list()
    selected_keys = props.get_selected_shape_keys()
    
    if targets and selected_keys and props.shapekey_source_object:
        # Single batch transfer button
        row = batch_box.row()
        row.scale_y = 1.5
        batch_op = row.operator("mesh.batch_transfer_shape_keys", text="Batch Transfer Shape Keys", icon='MODIFIER')
        batch_op.override_existing = props.shapekey_override_existing
        batch_op.skip_existing = props.shapekey_skip_existing
        
        # Transfer options below the batch button
        layout.separator(factor=0.3)
        options_box = layout.box()
        options_box.label(text="Transfer Options:", icon='PREFERENCES')
        
        # Checkboxes for transfer behavior (Skip first, most common use case)
        col = options_box.column()
        col.prop(props, "shapekey_skip_existing", text="Skip Existing Shape Keys")
        col.prop(props, "shapekey_override_existing", text="Override Existing Shape Keys")

        # Warning if both are selected
        if props.shapekey_override_existing and props.shapekey_skip_existing:
            col.label(text="⚠️ Both options selected - Skip takes priority", icon='ERROR')

        # Advanced Options (collapsible) - same as single mode
        layout.separator(factor=0.3)
        advanced_box = layout.box()
        advanced_header = advanced_box.row()
        advanced_header.prop(props, "shapekey_show_advanced",
                            icon='TRIA_DOWN' if props.shapekey_show_advanced else 'TRIA_RIGHT',
                            icon_only=True, emboss=False)
        advanced_header.label(text="Advanced Options", icon='PREFERENCES')

        if props.shapekey_show_advanced:
            advanced_col = advanced_box.column(align=True)
            advanced_col.scale_y = 0.9

            # Surface Deform Parameters Section
            surface_deform_box = advanced_col.box()
            surface_deform_box.label(text="Surface Deform Parameters", icon='MOD_MESHDEFORM')

            # Strength control
            strength_col = surface_deform_box.column(align=True)
            strength_label = strength_col.row()
            strength_label.scale_y = 0.8
            strength_label.label(text="Strength (0.0 - 1.0): Overall influence of deformation", icon='FORCE_FORCE')
            strength_col.prop(props, "shapekey_surface_deform_strength", text="", slider=True)

            surface_deform_box.separator(factor=0.3)

            # Falloff control
            falloff_col = surface_deform_box.column(align=True)
            falloff_label = falloff_col.row()
            falloff_label.scale_y = 0.8
            falloff_label.label(text="Falloff (0.1 - 16.0): Interpolation smoothness (lower = smoother)", icon='SMOOTHCURVE')
            falloff_col.prop(props, "shapekey_surface_deform_falloff", text="", slider=True)

            advanced_col.separator(factor=1.5)

            # Post-Transfer Smoothing Section (between Surface Deform and Pre-processing)
            smoothing_box = advanced_col.box()
            smoothing_box.label(text="Post-Transfer Smoothing", icon='MOD_SMOOTH')

            smoothing_col = smoothing_box.column(align=True)
            smoothing_col.scale_y = 0.9

            # Checkbox to enable smoothing
            smoothing_col.prop(props, "shapekey_smooth_boundary", text="Auto-Generate Smoothing Mask")

            if props.shapekey_smooth_boundary:
                smooth_settings = smoothing_col.box()

                # Boundary width slider
                width_label = smooth_settings.row()
                width_label.scale_y = 0.8
                width_label.label(text="Boundary Width (1 - 10 rings):", icon='MESH_GRID')
                smooth_settings.prop(props, "shapekey_smooth_boundary_width", text="", slider=True)

                smooth_settings.separator(factor=0.3)

                # Iterations slider
                iter_label = smooth_settings.row()
                iter_label.scale_y = 0.8
                iter_label.label(text="Smoothing Iterations (1 - 10):", icon='PREFERENCES')
                smooth_settings.prop(props, "shapekey_smooth_iterations", text="", slider=True)

                smooth_settings.separator(factor=0.3)

                # Auto-blur option
                smooth_settings.prop(props, "shapekey_auto_blur_mask", text="Auto-Blur Mask (Recommended)")

                if props.shapekey_auto_blur_mask:
                    blur_label = smooth_settings.row()
                    blur_label.scale_y = 0.8
                    blur_label.label(text="Blur Iterations (1 - 5):", icon='SMOOTHCURVE')
                    smooth_settings.prop(props, "shapekey_blur_iterations", text="", slider=True)

                smooth_settings.separator(factor=0.5)

                # Workflow info
                info_col = smooth_settings.column(align=True)
                info_col.scale_y = 0.7
                info_col.label(text="Workflow:", icon='INFO')
                info_col.label(text="1. 'Transfer + Generate Mask' creates mask + Weight Paint mode")
                info_col.label(text="2. Edit mask: Paint/blur weights, exclude unwanted areas")
                info_col.label(text="3. Red 'Apply Smoothing' button appears below transfer button")

            advanced_col.separator(factor=1.5)

            # Partial Island Handling Section (between smoothing and pre-processing)
            island_box = advanced_col.box()
            island_box.label(text="Partial Island Handling (WIP)", icon='MESH_CUBE')

            island_col = island_box.column(align=True)
            island_col.scale_y = 0.9

            # Description
            desc_col = island_col.column(align=True)
            desc_col.scale_y = 0.8
            desc_col.label(text="Handle small mesh islands that are partially deformed", icon='INFO')
            desc_col.label(text="(buttons, belts, small details)")

            island_col.separator(factor=0.3)

            # Mode dropdown
            island_col.label(text="Mode:", icon='PREFERENCES')
            island_col.prop(props, "shapekey_partial_island_mode", text="")

            island_col.separator(factor=0.3)

            # Island size threshold (always visible, controls both mask generation and island processing)
            threshold_label = island_col.row()
            threshold_label.scale_y = 0.8
            threshold_label.label(text="Island Size Threshold (0.005 - 0.20):", icon='MESH_GRID')
            island_col.prop(props, "shapekey_partial_island_threshold", text="", slider=True)

            threshold_info = island_col.column(align=True)
            threshold_info.scale_y = 0.6
            threshold_info.label(text="Max % of mesh to qualify as small island (0.05 = 5%)", icon='INFO')

            # Explain that this affects both systems when mode != NONE
            if props.shapekey_partial_island_mode != 'NONE':
                threshold_info.label(text="Affects: Smoothing mask generation + partial island processing", icon='LINKED')
            else:
                threshold_info.label(text="Island detection disabled when mode = NONE", icon='INFO')

            # Mode-specific info
            if props.shapekey_partial_island_mode != 'NONE':
                island_col.separator(factor=0.3)

                mode_info = island_col.box()
                mode_info_col = mode_info.column(align=True)
                mode_info_col.scale_y = 0.75

                if props.shapekey_partial_island_mode == 'EXCLUDE':
                    mode_info_col.label(text="EXCLUDE Mode:", icon='PANEL_CLOSE')
                    mode_info_col.label(text="• Resets partially moved islands to basis shape")
                    mode_info_col.label(text="• Preserves original mesh for small details")
                    mode_info_col.label(text="• Use when buttons/accessories get distorted")
                elif props.shapekey_partial_island_mode == 'AVERAGE':
                    mode_info_col.label(text="AVERAGE Mode:", icon='ORIENTATION_GLOBAL')
                    mode_info_col.label(text="• Applies uniform displacement to entire island")
                    mode_info_col.label(text="• Moves buttons/details together as a unit")
                    mode_info_col.label(text="• Keeps mesh intact, may need manual adjustment")

            advanced_col.separator(factor=1.5)

            # Pre-processing Modifiers Section (at bottom)
            preprocessing_box = advanced_col.box()
            preprocessing_box.label(text="Pre-processing Modifiers (EXPERIMENTAL)", icon='ERROR')

            preprocessing_col = preprocessing_box.column(align=True)
            preprocessing_col.scale_y = 0.9

            # Info text
            info_row = preprocessing_col.row()
            info_row.scale_y = 0.8
            info_row.label(text="Works on temporary copy - original mesh unchanged", icon='INFO')

            preprocessing_col.separator(factor=0.5)

            # Subdivision options
            subdiv_row = preprocessing_col.row()
            subdiv_row.prop(props, "shapekey_use_subdivision", text="Subdivision Surface")
            if props.shapekey_use_subdivision:
                subdiv_settings = preprocessing_col.box()
                subdiv_settings.prop(props, "shapekey_subdivision_levels", text="Levels", slider=True)

                # Simple subdivision with explanation
                simple_row = subdiv_settings.row()
                simple_row.prop(props, "shapekey_subdivision_simple", text="Simple Subdivision")
                simple_info = subdiv_settings.row()
                simple_info.scale_y = 0.7
                simple_info.label(text="(Use for hard edges/mechanical parts)", icon='INFO')

            preprocessing_col.separator(factor=0.3)

            # Displace options
            displace_row = preprocessing_col.row()
            displace_row.prop(props, "shapekey_use_displace", text="Displace")
            if props.shapekey_use_displace:
                displace_settings = preprocessing_col.box()

                # Strength with slider showing min/max
                strength_row = displace_settings.row()
                strength_row.label(text="Strength (0.0 - 1.0):")
                displace_settings.prop(props, "shapekey_displace_strength", text="", slider=True)

                # Midlevel with slider showing min/max
                midlevel_row = displace_settings.row()
                midlevel_row.label(text="Midlevel (0.0 - 1.0):")
                displace_settings.prop(props, "shapekey_displace_midlevel", text="", slider=True)

                # Direction
                displace_settings.prop(props, "shapekey_displace_direction", text="Direction")

    else:
        batch_box.label(text="Add targets and select shape keys to enable batch transfer", icon='INFO')


def draw_help_section(layout, context, multi_mode=False):
    """Draw expandable help information section"""
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        return
    
    # Collapsible help section
    help_box = layout.box()
    help_header = help_box.row()
    help_header.prop(props, "shapekey_help_expanded", 
                    icon='TRIA_DOWN' if props.shapekey_help_expanded else 'TRIA_RIGHT',
                    icon_only=True, emboss=False)
    help_header.label(text="How to Use", icon='INFO')
    
    if props.shapekey_help_expanded:
        if multi_mode:
            help_box.label(text="Multi-Target Mode:")
            help_box.label(text="• Select source mesh with shape keys")
            help_box.label(text="• Click refresh to load shape keys")
            help_box.label(text="• Check shape keys you want to transfer")
            help_box.label(text="• Select target meshes and click + to add them")
            help_box.label(text="• Set transfer options:")
            help_box.label(text="  ☑️ Override Existing: Replace existing shape keys")
            help_box.label(text="  ☑️ Skip Existing: Skip if shape key already exists")
            help_box.label(text="• Click 'Batch Transfer Shape Keys'")

            help_box.separator()
            help_box.label(text="Advanced Options (Optional):", icon='PREFERENCES')
            help_box.label(text="Surface Deform Parameters:", icon='MOD_MESHDEFORM')
            help_box.label(text="• Strength: Overall influence (1.0 = full, 0.5 = half)")
            help_box.label(text="• Falloff: Interpolation smoothness between faces")
            help_box.label(text="  - Lower = smoother interpolation (less artifacts)")
            help_box.label(text="  - Default 2.5 works for most cases")
            help_box.label(text="Post-Transfer Smoothing:", icon='MOD_SMOOTH')
            help_box.label(text="• 'Transfer + Generate Mask' switches to Weight Paint")
            help_box.label(text="• Red = smooth boundary, Blue = preserved")
            help_box.label(text="• Auto-Blur Mask (Recommended): Smooths generated masks")
            help_box.label(text="• Edit mask by painting/blurring weights as needed")
            help_box.label(text="• Red 'Apply Smoothing' button appears after transfer")
            help_box.separator(factor=0.5)
            help_box.label(text="Partial Island Handling (WIP):", icon='MESH_CUBE')
            help_box.label(text="• Controls small mesh islands (buttons, belts, details)")
            help_box.label(text="• NONE: Disables island detection entirely (default)")
            help_box.label(text="• EXCLUDE: Resets partially moved islands to basis")
            help_box.label(text="• AVERAGE: Applies uniform displacement to island")
            help_box.label(text="• Island Size Threshold: Max % to qualify as small island")
            help_box.label(text="• Affects both mask generation and island processing")
            help_box.label(text="• Keeps mesh intact, may need manual Edit mode tweaks")
            help_box.separator(factor=0.5)
            help_box.label(text="Pre-processing Modifiers:", icon='MODIFIER')
            help_box.label(text="• Improves quality on difficult transfers")
            help_box.label(text="• Works on temporary copy (original unchanged)")
            help_box.label(text="• Subdivision: Adds geometry for better sampling")
            help_box.label(text="  - Use for low-poly → high-poly transfers")
            help_box.label(text="  - Simple mode: For hard edges/mechanical")
            help_box.label(text="• Displace: Moves geometry closer to target")
            help_box.label(text="  - Use when meshes don't align well")
            help_box.label(text="  - Start with low strength (0.01-0.1)")
        else:
            help_box.label(text="Single Target Mode:")
            help_box.label(text="• Select source mesh with shape keys")
            help_box.label(text="• Select target mesh (dropdown or viewport)")
            help_box.label(text="• Choose one shape key to transfer")
            help_box.label(text="• Set transfer options:")
            help_box.label(text="  ☑️ Override Existing: Replace if exists")
            help_box.label(text="  ☑️ Skip Existing: Skip if exists")
            help_box.label(text="• Click 'Transfer Shape Key'")

            help_box.separator()
            help_box.label(text="Advanced Options (Optional):", icon='PREFERENCES')
            help_box.label(text="Surface Deform Parameters:", icon='MOD_MESHDEFORM')
            help_box.label(text="• Strength: Overall influence (1.0 = full, 0.5 = half)")
            help_box.label(text="• Falloff: Interpolation smoothness between faces")
            help_box.label(text="  - Lower = smoother interpolation (less artifacts)")
            help_box.label(text="  - Default 2.5 works for most cases")
            help_box.label(text="Post-Transfer Smoothing:", icon='MOD_SMOOTH')
            help_box.label(text="• 'Transfer + Generate Mask' switches to Weight Paint")
            help_box.label(text="• Red = smooth boundary, Blue = preserved")
            help_box.label(text="• Auto-Blur Mask (Recommended): Smooths generated masks")
            help_box.label(text="• Edit mask by painting/blurring weights as needed")
            help_box.label(text="• Red 'Apply Smoothing' button appears after transfer")
            help_box.separator(factor=0.5)
            help_box.label(text="Partial Island Handling (WIP):", icon='MESH_CUBE')
            help_box.label(text="• Controls small mesh islands (buttons, belts, details)")
            help_box.label(text="• NONE: Disables island detection entirely (default)")
            help_box.label(text="• EXCLUDE: Resets partially moved islands to basis")
            help_box.label(text="• AVERAGE: Applies uniform displacement to island")
            help_box.label(text="• Island Size Threshold: Max % to qualify as small island")
            help_box.label(text="• Affects both mask generation and island processing")
            help_box.label(text="• Keeps mesh intact, may need manual Edit mode tweaks")
            help_box.separator(factor=0.5)
            help_box.label(text="Pre-processing Modifiers:", icon='MODIFIER')
            help_box.label(text="• Improves quality on difficult transfers")
            help_box.label(text="• Works on temporary copy (original unchanged)")
            help_box.label(text="• Subdivision: Adds geometry for better sampling")
            help_box.label(text="  - Use for low-poly → high-poly transfers")
            help_box.label(text="  - Simple mode: For hard edges/mechanical")
            help_box.label(text="• Displace: Moves geometry closer to target")
            help_box.label(text="  - Use when meshes don't align well")
            help_box.label(text="  - Start with low strength (0.01-0.1)")


def get_classes():
    """Get all main panel classes for registration (none for main_panel)"""
    return []