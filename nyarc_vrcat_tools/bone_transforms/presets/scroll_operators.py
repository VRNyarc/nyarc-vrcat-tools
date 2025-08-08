# Preset Scroll Operators
# Navigation operators for scrollable preset list

import bpy
from bpy.types import Operator
from .manager import get_available_presets, open_presets_folder, get_presets_directory

def validate_scroll_position(props):
    """Ensure scroll position is valid for current preset count"""
    presets = get_available_presets()
    if not presets:
        props.bone_presets_scroll_offset = 0
        return
    
    items_per_page = props.bone_presets_items_per_page
    # Calculate max_offset to align with page boundaries
    total_pages = (len(presets) + items_per_page - 1) // items_per_page
    max_offset = max(0, (total_pages - 1) * items_per_page)
    old_offset = props.bone_presets_scroll_offset
    
    if props.bone_presets_scroll_offset > max_offset:
        props.bone_presets_scroll_offset = max_offset
        print(f"[DEBUG] Validate: corrected offset {old_offset} -> {props.bone_presets_scroll_offset} (max_offset={max_offset})")
    
    # Only debug log when validation corrects something
    if old_offset == props.bone_presets_scroll_offset:
        pass  # No correction needed

class ARMATURE_OT_preset_scroll_up(Operator):
    """Scroll preset list up"""
    bl_idname = "armature.preset_scroll_up"
    bl_label = "Scroll Up"
    bl_description = "Scroll up in preset list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            return {'CANCELLED'}
        
        # Validate current position first
        validate_scroll_position(props)
        
        # Calculate new offset
        items_per_page = props.bone_presets_items_per_page
        old_offset = props.bone_presets_scroll_offset
        new_offset = max(0, props.bone_presets_scroll_offset - items_per_page)
        props.bone_presets_scroll_offset = new_offset
        
        # Debug only if offset actually changed
        if old_offset != new_offset:
            print(f"[DEBUG] Scroll UP: {old_offset} -> {new_offset}")
        
        return {'FINISHED'}

class ARMATURE_OT_preset_scroll_down(Operator):    
    """Scroll preset list down"""
    bl_idname = "armature.preset_scroll_down"
    bl_label = "Scroll Down"
    bl_description = "Scroll down in preset list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            return {'CANCELLED'}
        
        # Validate current position first
        validate_scroll_position(props)
        
        presets = get_available_presets()
        if not presets:
            return {'CANCELLED'}
        
        # Calculate new offset ensuring we don't scroll past the end
        items_per_page = props.bone_presets_items_per_page
        # Use same max_offset calculation as validate function
        total_pages = (len(presets) + items_per_page - 1) // items_per_page
        max_offset = max(0, (total_pages - 1) * items_per_page)
        old_offset = props.bone_presets_scroll_offset
        new_offset = min(max_offset, props.bone_presets_scroll_offset + items_per_page)
        props.bone_presets_scroll_offset = new_offset
        
        # Debug only if offset actually changed
        if old_offset != new_offset:
            print(f"[DEBUG] Scroll DOWN: {old_offset} -> {new_offset} (max_offset={max_offset})")
        
        return {'FINISHED'}

class ARMATURE_OT_preset_scroll_to_top(Operator):
    """Jump to top of preset list"""
    bl_idname = "armature.preset_scroll_to_top"
    bl_label = "Go to Top"
    bl_description = "Jump to the beginning of preset list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            return {'CANCELLED'}
        
        props.bone_presets_scroll_offset = 0
        return {'FINISHED'}

class ARMATURE_OT_preset_scroll_to_bottom(Operator):
    """Jump to bottom of preset list"""
    bl_idname = "armature.preset_scroll_to_bottom"
    bl_label = "Go to Bottom"
    bl_description = "Jump to the end of preset list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            return {'CANCELLED'}
        
        presets = get_available_presets()
        if not presets:
            return {'CANCELLED'}
        
        # Calculate offset to show last page
        items_per_page = props.bone_presets_items_per_page
        # Use same max_offset calculation as validate function
        total_pages = (len(presets) + items_per_page - 1) // items_per_page
        max_offset = max(0, (total_pages - 1) * items_per_page)
        props.bone_presets_scroll_offset = max_offset
        
        print(f"[DEBUG] Scroll TO BOTTOM: offset set to {max_offset} (total_pages={total_pages})")
        
        # Final validation
        validate_scroll_position(props)
        
        return {'FINISHED'}

class WM_OT_open_presets_folder(Operator):
    """Open presets folder in file explorer"""
    bl_idname = "wm.open_presets_folder"
    bl_label = "Open Presets Folder"
    bl_description = "Open the presets folder in your system's file explorer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            result = open_presets_folder()
            
            # Show result in the info area
            if "Error" in result:
                self.report({'ERROR'}, result)
            elif "Open manually" in result:
                self.report({'WARNING'}, result)
            else:
                self.report({'INFO'}, result)
                
        except Exception as e:
            presets_dir = get_presets_directory()
            self.report({'ERROR'}, f"Failed to open folder. Path: {presets_dir}")
            
        return {'FINISHED'}

# Registration
SCROLL_CLASSES = (
    ARMATURE_OT_preset_scroll_up,
    ARMATURE_OT_preset_scroll_down,
    ARMATURE_OT_preset_scroll_to_top,
    ARMATURE_OT_preset_scroll_to_bottom,
    WM_OT_open_presets_folder,
)