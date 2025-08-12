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
    layout.prop(props, "shapekey_target_object", text="")
    
    # Shape key selector (only show if source is selected)
    if props.shapekey_source_object:
        layout.label(text="Shape Key to Transfer:")
        layout.prop(props, "shapekey_shape_key", text="")
    
    layout.separator(factor=0.5)
    
    # Transfer button
    if (props.shapekey_source_object and props.shapekey_target_object and 
        props.shapekey_shape_key and props.shapekey_shape_key != "NONE"):
        
        # Single transfer button
        row = layout.row()
        row.scale_y = 1.5
        transfer_op = row.operator("mesh.transfer_shape_key", text="Transfer Shape Key", icon='SHAPEKEY_DATA')
        transfer_op.override_existing = props.shapekey_override_existing
        transfer_op.skip_existing = props.shapekey_skip_existing
        
        # Transfer options below the button
        layout.separator(factor=0.3)
        options_box = layout.box()
        options_box.label(text="Transfer Options:", icon='PREFERENCES')
        
        # Checkboxes for transfer behavior
        col = options_box.column()
        col.prop(props, "shapekey_override_existing", text="Override Existing Shape Keys")
        col.prop(props, "shapekey_skip_existing", text="Skip Existing Shape Keys")
        
        # Warning if both are selected
        if props.shapekey_override_existing and props.shapekey_skip_existing:
            col.label(text="⚠️ Both options selected - Skip takes priority", icon='ERROR')
            
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
        
        # Checkboxes for transfer behavior
        col = options_box.column()
        col.prop(props, "shapekey_override_existing", text="Override Existing Shape Keys")
        col.prop(props, "shapekey_skip_existing", text="Skip Existing Shape Keys")
        
        # Warning if both are selected
        if props.shapekey_override_existing and props.shapekey_skip_existing:
            col.label(text="⚠️ Both options selected - Skip takes priority", icon='ERROR')
        
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
        else:
            help_box.label(text="Single Target Mode:")
            help_box.label(text="• Select source mesh with shape keys")
            help_box.label(text="• Select target mesh")
            help_box.label(text="• Choose one shape key to transfer")
            help_box.label(text="• Set transfer options:")
            help_box.label(text="  ☑️ Override Existing: Replace if exists")
            help_box.label(text="  ☑️ Skip Existing: Skip if exists")
            help_box.label(text="• Click 'Transfer Shape Key'")


def get_classes():
    """Get all main panel classes for registration (none for main_panel)"""
    return []