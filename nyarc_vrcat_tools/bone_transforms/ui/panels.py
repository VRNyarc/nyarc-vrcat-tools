# Bone Transform Saver UI Module - Main Coordinator
# Coordinates all the modular UI components

import bpy
from .pose_controls import draw_pose_controls_ui
from ..presets.ui import draw_presets_ui
# Details UI moved to top-level module
# from .details import draw_details_ui

def draw_ui(layout, context):
    """Draw the complete Pose Mode Bone Editor UI"""
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        layout.label(text="Nyarc Tools properties not found!", icon='ERROR')
        return
    
    # Armature selector (always visible)
    layout.label(text="Armature:")
    layout.prop(props, "bone_armature_object", text="")
    
    if props.bone_armature_object:
        layout.separator()
        
        # 1. Pose Mode Controls (always expanded when armature selected)
        draw_pose_controls_ui(layout, context, props)
        
        layout.separator()
        
        # 2. Transform Presets (collapsible)
        draw_presets_ui(layout, context, props)
        
        layout.separator()
        
        # 3. Armature Diff Export (collapsible)
        draw_diff_export_ui(layout, context, props)
        
        layout.separator()
        
        # 4. Usage instructions (Details moved to top-level module)
        draw_usage_info(layout)

def draw_diff_export_ui(layout, context, props):
    """Draw the Armature Diff Export section"""
    try:
        diff_box = layout.box()
        
        # Header with toggle
        diff_header = diff_box.row()
        diff_header.prop(props, "bone_diff_show_ui", 
                        icon="TRIA_DOWN" if props.bone_diff_show_ui else "TRIA_RIGHT", 
                        icon_only=True, emboss=False)
        diff_header.label(text="Armature Diff Export", icon='MODIFIER_DATA')
        
        # Show content if expanded
        if props.bone_diff_show_ui:
            diff_box.label(text="Compare two armatures and export differences:")
            
            # WARNING about inherit_scale requirement
            warning_box = diff_box.box()
            warning_box.alert = True
            warning_header = warning_box.row()
            warning_header.label(text="⚠️ IMPORTANT REQUIREMENT", icon='ERROR')
            warning_row1 = warning_box.row()
            warning_row1.scale_y = 0.8
            warning_row1.label(text="Modified armature MUST have ALL bones set to:")
            warning_row2 = warning_box.row()
            warning_row2.scale_y = 0.8
            warning_row2.label(text="Inherit Scale: NONE")
            warning_row3 = warning_box.row()
            warning_row3.scale_y = 0.8
            warning_row3.label(text="(inherit_scale=FULL causes precision errors)")
            
            # WARNING about X/Z scaling limitation
            xz_warning_box = diff_box.box()
            xz_warning_box.alert = True
            xz_warning_header = xz_warning_box.row()
            xz_warning_header.label(text="⚠️ SCALING LIMITATION", icon='ERROR')
            xz_warning_row1 = xz_warning_box.row()
            xz_warning_row1.scale_y = 0.8
            xz_warning_row1.label(text="Currently ONLY Y-axis scaling works correctly")
            xz_warning_row2 = xz_warning_box.row()  
            xz_warning_row2.scale_y = 0.8
            xz_warning_row2.label(text="X/Z scaling forced to 1.0 (coordinate space issues)")
            xz_warning_row3 = xz_warning_box.row()
            xz_warning_row3.scale_y = 0.8
            xz_warning_row3.label(text="Use Y-only scaling for bone length changes")
            
            diff_box.separator()
            
            # Original armature selector
            diff_box.label(text="Original/Base Armature:")
            diff_box.prop(props, "bone_diff_original_armature", text="")
            
            # Modified armature selector  
            diff_box.label(text="Modified Armature:")
            diff_box.prop(props, "bone_diff_modified_armature", text="")
            
            # Preset name for diff export
            diff_box.label(text="Diff Preset Name:")
            diff_box.prop(props, "bone_diff_preset_name", text="")
            
            # Export button
            export_row = diff_box.row()
            export_row.scale_y = 1.3
            
            # Only enable if both armatures are selected
            is_ready = (props.bone_diff_original_armature and 
                       props.bone_diff_modified_armature and 
                       props.bone_diff_preset_name.strip())
            
            if not is_ready:
                export_row.enabled = False
            
            export_row.operator("armature.export_armature_diff", 
                              text="Export Transform Differences", 
                              icon='EXPORT')
            
            # Info about diff export
            info_row = diff_box.row()
            info_row.scale_y = 0.8
            if not is_ready:
                info_row.label(text="Select both armatures and enter preset name", icon='INFO')
            else:
                info_row.label(text="Ready to export differences as preset", icon='FILE_TICK')
    
    except Exception as e:
        # Fallback UI if there's an error
        error_box = layout.box()
        error_box.label(text="Armature Diff Export (Error)", icon='ERROR')
        error_box.label(text=f"UI Error: {str(e)}", icon='INFO')
        print(f"Diff Export UI Error: {e}")

def draw_usage_info(layout):
    """Draw usage instructions"""
    info_box = layout.box()
    info_box.label(text="Quick Start Guide", icon='INFO')
    
    col = info_box.column(align=True)
    col.scale_y = 0.9
    col.label(text="1. ► Select armature → Start Pose Mode")
    col.label(text="2. ⚙ Toggle Inherit Scale if needed")
    col.label(text="3. ✋ Edit bone transforms manually")
    col.label(text="4. 💾 Save as preset for reuse")
    col.label(text="5. ✓ Apply as Rest Pose when done")