# Main Shape Key Transfer Panel
# Primary UI layout and drawing functions

import bpy
from .preview_ui import draw_live_preview_ui


def draw_ui(layout, context):
    """Draw the Shape Key Transfer UI content (called from modules.py)"""
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        layout.label(text="Nyarc Tools properties not found!", icon='ERROR')
        return
    
    # Mode toggle
    layout.prop(props, "shapekey_multi_mode", text="Multi-Target Mode", icon='OUTLINER_OB_GROUP_INSTANCE')
    
    layout.separator()
    
    # Source object selector
    layout.label(text="Source Mesh (with shape keys):")
    layout.prop(props, "shapekey_source_object", text="")
    
    # Shape key refresh control
    if props.shapekey_source_object:
        row = layout.row()
        row.label(text="Shape Keys:")
        row.operator("mesh.update_shapekey_list", text="", icon='FILE_REFRESH')
    
    layout.separator()
    
    # Mode-specific UI
    if props.shapekey_multi_mode:
        draw_multi_target_ui(layout, context, props)
    else:
        draw_single_target_ui(layout, context, props)
    
    # Live Preview Section
    if props.shapekey_source_object:
        draw_live_preview_ui(layout, context, props)


def draw_single_target_ui(layout, context, props):
    """Draw single target mode UI (legacy mode)"""
    # Target object selector
    layout.label(text="Target Mesh:")
    layout.prop(props, "shapekey_target_object", text="")
    
    # Shape key selector (only show if source is selected)
    if props.shapekey_source_object:
        layout.label(text="Shape Key to Transfer:")
        layout.prop(props, "shapekey_shape_key", text="")
    
    layout.separator()
    
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
        layout.separator()
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
    
    # Help section
    layout.separator()
    draw_help_section(layout, context, multi_mode=False)


def draw_multi_target_ui(layout, context, props):
    """Draw multi-target mode UI with batch operations"""
    # Target management section
    targets_box = layout.box()
    targets_header = targets_box.row()
    targets_header.label(text="Target Meshes:", icon='OUTLINER_OB_MESH')
    targets_header.operator("mesh.add_target_object", text="", icon='ADD')
    targets_header.operator("mesh.clear_target_objects", text="", icon='TRASH')
    
    # Show current targets
    for i, target_item in enumerate(props.shapekey_target_objects):
        if target_item.target_object:
            row = targets_box.row()
            row.label(text=target_item.target_object.name, icon='MESH_DATA')
            remove_op = row.operator("mesh.remove_target_object", text="", icon='X')
            remove_op.index = i
    
    if not props.shapekey_target_objects:
        targets_box.label(text="Click + to add target meshes", icon='INFO')
    
    layout.separator()
    
    # Shape key selection section
    keys_box = layout.box()
    keys_header = keys_box.row()
    keys_header.label(text="Shape Keys to Transfer:", icon='SHAPEKEY_DATA')
    
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
                    row.prop(key_item, "selected", text=key_item.name)
        else:
            keys_box.label(text="Click refresh button to load shape keys", icon='INFO')
    
    layout.separator()
    
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
        layout.separator()
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
    
    # Help section
    layout.separator()
    draw_help_section(layout, context, multi_mode=True)


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