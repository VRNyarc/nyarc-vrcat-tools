# Preset UI Module
# Handles the collapsible presets section UI

import bpy
import json
import os
from .manager import get_available_presets
from ..operators.loader import preset_has_precision_data

def has_precision_capable_presets(visible_presets):
    """Check if any of the visible presets have precision data"""
    presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
    
    for preset_name in visible_presets:
        preset_file = os.path.join(presets_dir, f"{preset_name}.json")
        try:
            if os.path.exists(preset_file):
                with open(preset_file, 'r') as f:
                    preset_data = json.load(f)
                    if preset_has_precision_data(preset_data):
                        return True
        except:
            continue
    return False

def preset_has_precision_data_by_name(preset_name):
    """Check if a specific preset has precision data"""
    presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
    preset_file = os.path.join(presets_dir, f"{preset_name}.json")
    
    try:
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                preset_data = json.load(f)
                return preset_has_precision_data(preset_data) and preset_data.get('diff_export', False)
    except:
        pass
    return False

def draw_presets_ui(layout, context, props):
    """Draw the Transform Presets UI as a collapsible section"""
    try:
        # Preset management box
        preset_box = layout.box()
        
        # Header with toggle for presets section
        preset_header = preset_box.row()
        preset_header.prop(props, "bone_presets_show_ui", 
                          icon="TRIA_DOWN" if props.bone_presets_show_ui else "TRIA_RIGHT", 
                          icon_only=True, emboss=False)
        preset_header.label(text="Transform Presets", icon='PRESET')
        
        # Show preset content if expanded
        if props.bone_presets_show_ui:
            # Preset name input
            preset_box.label(text="Preset Name:")
            preset_box.prop(props, "bone_preset_name", text="")
            
            # Save button
            save_row = preset_box.row()
            save_row.scale_y = 1.2
            save_row.operator("armature.save_bone_transforms", text="Save Preset", icon='EXPORT')
            
            # Available presets with scrollable list
            presets = get_available_presets()
            if presets:
                preset_box.separator()
                
                # Header with preset count and navigation
                header_row = preset_box.row()
                header_row.label(text=f"Available Presets ({len(presets)} total):")
                
                # Calculate page info first
                items_per_page = getattr(props, 'bone_presets_items_per_page', 8)
                current_offset = getattr(props, 'bone_presets_scroll_offset', 0)
                
                # Calculate pagination values
                total_pages = (len(presets) + items_per_page - 1) // items_per_page
                current_page = (current_offset // items_per_page) + 1
                start_idx = current_offset + 1
                end_idx = min(current_offset + items_per_page, len(presets))
                
                # Page info (for user reference)
                info_row = preset_box.row()
                info_row.scale_y = 0.7
                info_row.label(text=f"Page {current_page}/{total_pages} • Items {start_idx}-{end_idx} of {len(presets)}", icon='INFO')
                
                # Navigation controls - Force show for testing (remove condition temporarily)
                if True:  # len(presets) > items_per_page:
                    nav_box = preset_box.box()
                    nav_box.label(text="Navigation:", icon='HAND')
                    
                    nav_row = nav_box.row()
                    nav_row.scale_y = 1.2
                    
                    # Use already calculated pagination values
                    
                    # Navigation buttons - make them more prominent
                    nav_row.operator("armature.preset_scroll_to_top", text="First", icon='REW')
                    nav_row.operator("armature.preset_scroll_up", text="Previous", icon='TRIA_UP')
                    
                    # Page indicator in center
                    page_col = nav_row.column()
                    page_col.scale_x = 1.5
                    page_col.label(text=f"Page {current_page}/{total_pages}")
                    page_col.label(text=f"({start_idx}-{end_idx})")
                    
                    # Navigation buttons  
                    nav_row.operator("armature.preset_scroll_down", text="Next", icon='TRIA_DOWN')
                    nav_row.operator("armature.preset_scroll_to_bottom", text="Last", icon='FF')
                else:
                    # Show reason why navigation isn't visible
                    info_row = preset_box.row()
                    info_row.scale_y = 0.6
                    info_row.label(text=f"Navigation hidden: {len(presets)} <= {items_per_page} presets")
                
                # Show current page of presets
                start_idx = props.bone_presets_scroll_offset
                end_idx = start_idx + props.bone_presets_items_per_page
                visible_presets = presets[start_idx:end_idx]
                
                for preset_name in visible_presets:
                    row = preset_box.row()
                    # Different icon for diff presets vs regular presets
                    icon = 'MOD_DISPLACE' if preset_name.endswith('_diff') else 'PRESET'
                    row.label(text=preset_name, icon=icon)
                    
                    # Load button - change text for diff presets with precision correction enabled
                    button_text = "Load"
                    button_icon = 'IMPORT'
                    
                    if (props.apply_precision_correction and 
                        preset_has_precision_data_by_name(preset_name)):
                        button_text = "Apply Pose"
                        button_icon = 'ARMATURE_DATA'
                    
                    load_op = row.operator("armature.load_bone_transforms", text=button_text, icon=button_icon)
                    load_op.preset_name = preset_name
                    
                    # Delete button (small X)
                    delete_op = row.operator("armature.delete_bone_transforms", text="", icon='X')
                    delete_op.preset_name = preset_name
                
                # Show precision correction checkbox if any visible presets have precision data
                if has_precision_capable_presets(visible_presets):
                    preset_box.separator()
                    precision_box = preset_box.box()
                    precision_box.label(text="Precision Options:", icon='MODIFIER_DATA')
                    
                    precision_row = precision_box.row()
                    precision_row.prop(props, "apply_precision_correction", 
                                     text="Apply Precision Correction")
                    
                    # Info about precision correction
                    info_row = precision_box.row()
                    info_row.scale_y = 0.8
                    if props.apply_precision_correction:
                        info_row.label(text="🚨 ENABLED - Only use with SAME base armature as diff export!", icon='ERROR')
                        # WIP warning row
                        warning_row = precision_box.row()
                        warning_row.scale_y = 0.7
                        warning_row.label(text="⚠️ WIP: Precision correction is broken - do not use!", icon='ERROR')
                    else:
                        info_row.label(text="Precision correction disabled - may have small offsets", icon='INFO')
                        # WIP warning row 
                        warning_row = precision_box.row()
                        warning_row.scale_y = 0.7
                        warning_row.label(text="⚠️ WIP: Precision correction is broken - feature under development", icon='ERROR')
                    
            else:
                preset_box.label(text="No presets found - save one first!", icon='INFO')
            
            # Preset folder management
            preset_box.separator()
            folder_row = preset_box.row()
            folder_row.scale_y = 0.9
            folder_row.operator("wm.open_presets_folder", text="Open Presets Folder", icon='FILE_FOLDER')
            
            # Usage info
            info_box = preset_box.box()
            info_box.scale_y = 0.8
            info_box.label(text="Tips:", icon='INFO')
            info_box.label(text="- Enter pose mode first, then save presets")
            info_box.label(text="- Name presets with model name for easy identification")
            info_box.label(text="- Presets work best on similar bone structures")
            
            # Additional info when precision correction is enabled
            if props.apply_precision_correction and has_precision_capable_presets(visible_presets):
                info_box.separator()
                info_box.label(text="Precision Mode:", icon='MODIFIER_DATA')
                info_box.label(text="- 'Apply Pose' buttons auto-apply corrections as rest pose")
                info_box.label(text="- Edit mode coordinates will match corrected positions")
    
    except Exception as e:
        # Fallback UI if there's an error
        error_box = layout.box()
        error_box.label(text="Transform Presets (Error)", icon='ERROR')
        error_box.label(text=f"UI Error: {str(e)}", icon='INFO')
        print(f"Presets UI Error: {e}")