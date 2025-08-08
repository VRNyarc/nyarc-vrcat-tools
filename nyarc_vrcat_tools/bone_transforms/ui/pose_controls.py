# Pose Mode Controls UI
# The main pose mode control buttons section

import bpy

# Import pose history system
try:
    from ..pose_history import get_pose_history_list
    POSE_HISTORY_AVAILABLE = True
except ImportError:
    POSE_HISTORY_AVAILABLE = False
    print("Warning: pose_history not available for UI")

def draw_pose_controls_ui(layout, context, props):
    """Draw the Pose Mode Controls section"""
    if not props.bone_armature_object:
        return
    
    # CATS-like controls box
    cats_box = layout.box()
    
    # Dynamic header text based on pose mode state
    if getattr(props, 'bone_editing_active', False):
        cats_box.label(text="Pose Mode Controls (Active)", icon='POSE_HLT')
    else:
        cats_box.label(text="Pose Mode Controls", icon='POSE_HLT')
    
    # Main toggle button
    main_row = cats_box.row()
    main_row.scale_y = 1.3
    
    # Dynamic button text based on current state
    if getattr(props, 'bone_editing_active', False) and context.mode == 'POSE':
        # Show stop option when in pose mode
        main_row.operator("armature.toggle_pose_mode", text="Stop Pose Mode", icon='PAUSE')
        
        # Reset & Stop button
        reset_row = cats_box.row() 
        reset_row.scale_y = 1.2
        reset_row.operator("armature.reset_and_stop_pose_mode", text="Reset & Stop Pose Mode", icon='LOOP_BACK')
        
        # Apply as rest pose - ONLY show when in pose mode
        rest_row = cats_box.row()
        rest_row.scale_y = 1.2
        rest_row.operator("armature.apply_as_rest_pose", text="Apply as Rest Pose", icon='ARMATURE_DATA')
        
        # POSE HISTORY SECTION - Only show when pose mode is active
        if POSE_HISTORY_AVAILABLE:
            draw_pose_history_ui(cats_box, context, props)
    else:
        main_row.operator("armature.toggle_pose_mode", text="Start Pose Mode", icon='PLAY')
    
    # Inherit Scale Section
    inherit_scale_box = cats_box.box()
    
    # Section header
    header_row = inherit_scale_box.row()
    header_row.label(text="Inherit Scale", icon='BONE_DATA')
    
    armature = props.bone_armature_object
    
    # Initialize warning state on first armature selection (using global cache now)
    if armature:
        try:
            # Import the update function
            from ..operators.inherit_scale import update_inherit_scale_warning, get_inherit_scale_warning
            update_inherit_scale_warning(armature)
        except Exception as e:
            print(f"Error initializing inherit scale warning: {e}")
    
    # Warning message if mixed state detected (from cache)
    show_warning = False
    if armature:
        try:
            from ..operators.inherit_scale import get_inherit_scale_warning
            show_warning = get_inherit_scale_warning(armature)
            # DEBUG: Disabled for cleaner console output
            # print(f"DEBUG UI: Checking warning for '{armature.name}': {show_warning}")
        except Exception as e:
            print(f"Error getting inherit scale warning: {e}")
    
    if show_warning:
        warning_row = inherit_scale_box.row()
        warning_row.alert = True
        warning_row.label(text="⚠ Warning: Mixed inherit scale detected", icon='ERROR')
    
    # Two buttons for setting all bones - None and Full
    scale_row = inherit_scale_box.row()
    scale_row.scale_y = 1.1
    
    # Set All to None button
    scale_row.operator("armature.set_inherit_scale_all_none", text="Set All → None", icon='BONE_DATA')
    
    # Set All to Full button  
    scale_row.operator("armature.set_inherit_scale_all_full", text="Set All → Full", icon='BONE_DATA')
    
    # Selected bones section - separate line underneath with headline
    selected_header_row = inherit_scale_box.row()
    selected_header_row.label(text="Selected Bones", icon='RESTRICT_SELECT_OFF')
    
    # Two buttons for selected bones - None and Full
    selected_row = inherit_scale_box.row()
    selected_row.scale_y = 1.0
    
    # Set Selected to None button
    selected_row.operator("armature.set_inherit_scale_selected_none", text="Selected → None", icon='BONE_DATA')
    
    # Set Selected to Full button  
    selected_row.operator("armature.set_inherit_scale_selected_full", text="Selected → Full", icon='BONE_DATA')


def draw_pose_history_ui(parent_box, context, props):
    """Draw the Pose History section (only visible when pose mode is active)"""
    try:
        if not POSE_HISTORY_AVAILABLE or not props.bone_armature_object:
            return
        
        armature = props.bone_armature_object
        
        # Pose History Section
        history_box = parent_box.box()
        
        # Header with toggle and enable checkbox
        header_row = history_box.row()
        header_row.prop(props, "pose_history_show_ui", 
                       text="Pose History", 
                       icon='TRIA_DOWN' if getattr(props, 'pose_history_show_ui', True) else 'TRIA_RIGHT',
                       emboss=False)
        
        # Enable/Disable checkbox with education button
        enable_row = header_row.row()
        enable_row.alignment = 'RIGHT'
        
        # Show checkbox state
        if getattr(props, 'pose_history_enabled', False):
            enable_row.prop(props, "pose_history_enabled", text="", icon='CHECKBOX_HLT')
        else:
            enable_row.prop(props, "pose_history_enabled", text="", icon='CHECKBOX_DEHLT')
        
        # Info button that also serves as toggle
        info_op = enable_row.operator("armature.pose_history_education_popup", text="", icon='INFO')
        
        # Only show content if expanded
        if not getattr(props, 'pose_history_show_ui', True):
            return
        
        # Check if pose history is enabled
        pose_history_enabled = getattr(props, 'pose_history_enabled', False)
        
        if not pose_history_enabled:
            # Show opt-in message when disabled
            disabled_row = history_box.row()
            disabled_row.alert = True
            disabled_row.alignment = 'CENTER'
            disabled_row.label(text="Pose History Disabled", icon='CANCEL')
            
            info_row = history_box.row()
            info_row.scale_y = 0.8
            info_row.alignment = 'CENTER'
            info_row.label(text="Enable checkbox above to start saving pose history")
            
            tip_row = history_box.row()
            tip_row.scale_y = 0.8
            tip_row.alignment = 'CENTER'
            tip_row.label(text="Click [i] button for more information")
            return
        
        # DEBUG: Force scene update to ensure we see latest data
        try:
            context.view_layer.update()
        except:
            pass
        
        # Get pose history entries with error handling (only when enabled)
        history_entries = []
        try:
            history_entries = get_pose_history_list(armature)
            
            # Pose history entries loaded for UI display
                        
        except Exception as e:
            # Silently handle pose history loading errors
            pass
        
        if not history_entries:
            # Check if metadata object exists but entries aren't loading
            metadata_obj_name = f"{armature.name}_VRCAT_PoseHistory"
            metadata_obj = bpy.data.objects.get(metadata_obj_name)
            
            if metadata_obj:
                # Metadata exists but entries not loading - likely timing issue
                timing_row = history_box.row()
                timing_row.alert = True
                timing_row.label(text="Pose history detected, refreshing...", icon='FILE_REFRESH')
                tip_row = history_box.row()
                tip_row.scale_y = 0.8
                tip_row.label(text="Try switching modes or wait a moment for UI update")
                
                # Add manual refresh button
                refresh_row = history_box.row()
                refresh_row.scale_y = 1.1
                refresh_row.operator("armature.refresh_pose_history_ui", text="Refresh UI", icon='FILE_REFRESH')
            else:
                # No history available yet - show encouraging message
                ready_row = history_box.row()
                ready_row.alignment = 'CENTER'
                ready_row.label(text="Ready to save pose history!", icon='CHECKMARK')
                
                tip_row = history_box.row()
                tip_row.scale_y = 0.8
                tip_row.alignment = 'CENTER'
                tip_row.label(text="History auto-saves when you 'Apply as Rest Pose'")
                
                # Manual snapshots removed - pose history only works with Apply Rest Pose
                # This ensures proper revert-to-original functionality
            return
        
        # Show entry count
        count_row = history_box.row()
        count_row.scale_y = 0.8
        count_row.label(text=f"Found {len(history_entries)} history entries:", icon='INFO')
        
        # History entries list (show max 5 recent entries)
        display_entries = history_entries[:5]
        
        # With sequential numbering, Entry #1 is ALWAYS the original
        original_entry_id = "1"  # Sequential system: Entry #1 = Original Pose
        
        for i, (entry_id, name, timestamp, entry_type) in enumerate(display_entries):
            entry_row = history_box.row()
            
            # With sequential numbering: Entry #1 = Original, all others = regular poses
            is_original = (entry_id == "1")
            
            # Button text: "Load Original Pose" for first entry, "Load Pose" for others
            button_text = "Load Original Pose" if is_original else "Load Pose"
            
            # Revert button with appropriate text
            revert_op = entry_row.operator("armature.revert_pose_history", text=button_text)
            revert_op.entry_id = entry_id
            
            # Small export to preset button
            export_op = entry_row.operator("armature.export_pose_history_to_preset", text="Save→Rest", emboss=True)
            export_op.entry_id = entry_id
            export_op.preset_name = f"From_{name.replace(' ', '_')[:15]}"  # Default name from history entry
            
            # Format timestamp nicely
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%m/%d %H:%M")
            except Exception as e:
                time_str = timestamp[:16].replace('T', ' ')
            
            # Icon and text based on entry type and if it's original
            if is_original:
                icon = 'HOME'  # Special icon for original
                info_text = "Original Pose"
            else:
                # Use valid Blender icons
                icon = 'LOOP_BACK' if entry_type == "before_apply_rest" else 'RECOVER_LAST'
                info_text = f"{time_str}"
            
            entry_row.label(text=info_text, icon=icon)
        
        # Show count if more entries exist
        if len(history_entries) > 5:
            more_row = history_box.row()
            more_row.scale_y = 0.8
            more_row.label(text=f"... and {len(history_entries) - 5} older entries", icon='DOWNARROW_HLT')
        
        # Management section - show at bottom when pose history is enabled
        if pose_history_enabled and history_entries:
            history_box.separator()
            management_row = history_box.row()
            management_row.alert = True
            management_row.scale_y = 1.1
            management_row.operator("armature.disable_and_delete_pose_history", 
                                   text="🗑️ Disable & Delete All", 
                                   icon='CANCEL')
    
    except Exception as e:
        # Fallback UI if there's an error - similar to presets UI
        error_box = parent_box.box()
        error_box.label(text="Pose History (Error)", icon='ERROR')
        error_box.label(text=f"UI Error: {str(e)}", icon='INFO')
        print(f"Pose History UI Error: {e}")
        import traceback
        traceback.print_exc()