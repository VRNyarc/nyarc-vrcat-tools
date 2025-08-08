# Live Preview UI Components
# Preview panel and synchronization controls

import bpy


def draw_live_preview_ui(layout, context, props):
    """Draw the live preview and synchronization UI section"""
    layout.separator()
    
    # Collapsible preview section
    preview_box = layout.box()
    preview_header = preview_box.row()
    preview_header.prop(props, "shapekey_preview_mode", 
                       icon='TRIA_DOWN' if props.shapekey_preview_mode else 'TRIA_RIGHT',
                       icon_only=True, emboss=False)
    preview_header.label(text="Live Preview & Sync", icon='VIEWZOOM')
    
    if props.shapekey_preview_mode:
        # Sync controls header
        sync_header = preview_box.row()
        sync_header.prop(props, "shapekey_sync_enabled", text="Enable Live Sync")
        sync_header.operator("mesh.reset_shape_key_values", text="Reset All", icon='X')
        sync_header.operator("mesh.clear_live_preview_modifiers", text="Clear Previews", icon='MODIFIER')
        
        # Get available shape keys from source
        source_obj = props.shapekey_source_object
        if not source_obj or not source_obj.data.shape_keys:
            preview_box.label(text="No shape keys found in source mesh", icon='INFO')
            return
        
        # Get target objects for validation
        target_objects = []
        if props.shapekey_target_object:
            target_objects.append(props.shapekey_target_object)
        target_objects.extend(props.get_target_objects_list())
        target_objects = list(set(target_objects))  # Remove duplicates
        
        if not target_objects:
            preview_box.label(text="No target meshes selected", icon='INFO')
            return
        
        # Show sync status with more detail
        status_row = preview_box.row()
        
        # Count targets with and without transferred keys
        targets_with_keys = 0
        targets_without_keys = 0
        
        for target_obj in target_objects:
            if target_obj and target_obj.data.shape_keys:
                targets_with_keys += 1
            else:
                targets_without_keys += 1
        
        if targets_without_keys > 0:
            status_row.label(text=f"Sync: Source + {targets_with_keys} transferred | {targets_without_keys} need transfer first", icon='INFO')
        else:
            status_row.label(text=f"Syncing: Source + {len(target_objects)} target(s)", icon='LINKED')
        
        # Show helpful note if there are targets without transferred shape keys
        if targets_without_keys > 0:
            info_row = preview_box.row()
            info_row.label(text="💡 Transfer shape keys first to enable full live sync on all targets", icon='LIGHTBULB')
        
        # Dynamic sliders for each shape key
        if props.shapekey_multi_mode:
            # In multi-target mode, show sliders for selected shape keys
            selected_keys = props.get_selected_shape_keys()
            
            # Debug info for selected keys
            preview_box.label(text=f"Selected keys: {len(selected_keys)}", icon='INFO')
            
            if not selected_keys:
                preview_box.label(text="Select shape keys to preview", icon='INFO')
                return
            
            # Show sliders for ALL selected keys
            for key_name in selected_keys:
                if key_name != "Basis" and key_name in source_obj.data.shape_keys.key_blocks:
                    key_block = source_obj.data.shape_keys.key_blocks[key_name]
                    row = preview_box.row()
                    
                    # Shape key name
                    row.label(text=key_name)
                    slider_row = row.row()
                    slider_row.scale_x = 2.0
                    
                    # Show slider based on sync mode
                    if props.shapekey_sync_enabled:
                        # Interactive slider with automatic live sync (no manual button needed)
                        slider_row.prop(key_block, "value", text="", slider=True)
                        # Small indicator that live sync is active
                        row.label(text="", icon='LINKED')
                    else:
                        # Interactive slider with manual sync button when live sync is off
                        slider_row.prop(key_block, "value", text="", slider=True)
                        sync_btn = row.operator("mesh.sync_shape_key_value", text="↻", icon='FILE_REFRESH')
                        sync_btn.shape_key_name = key_name
                        sync_btn.shape_key_value = key_block.value
        else:
            # In single target mode, show slider for selected shape key
            preview_box.label(text=f"Single mode - Selected: {props.shapekey_shape_key}", icon='INFO')
            
            if props.shapekey_shape_key and props.shapekey_shape_key != "NONE":
                key_name = props.shapekey_shape_key
                if key_name in source_obj.data.shape_keys.key_blocks:
                    key_block = source_obj.data.shape_keys.key_blocks[key_name]
                    row = preview_box.row()
                    
                    # Shape key name
                    row.label(text=key_name)
                    slider_row = row.row()
                    slider_row.scale_x = 2.0
                    
                    # Show slider based on sync mode
                    if props.shapekey_sync_enabled:
                        # Interactive slider with automatic live sync (no manual button needed)
                        slider_row.prop(key_block, "value", text="", slider=True)
                        # Small indicator that live sync is active
                        row.label(text="", icon='LINKED')
                    else:
                        # Interactive slider with manual sync button when live sync is off
                        slider_row.prop(key_block, "value", text="", slider=True)
                        sync_btn = row.operator("mesh.sync_shape_key_value", text="↻", icon='FILE_REFRESH')
                        sync_btn.shape_key_name = key_name
                        sync_btn.shape_key_value = key_block.value
            else:
                preview_box.label(text="Select a shape key to preview", icon='INFO')


def get_classes():
    """Get all preview UI classes for registration (none for preview_ui)"""
    return []