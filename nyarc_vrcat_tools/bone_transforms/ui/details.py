"""
Details UI Module
Information about companion tools and integration with CATS and Avatar Toolkit
"""

import bpy

def draw_details_ui(layout, context, props):
    """Draw the Details/Information section about companion tools"""
    try:
        details_box = layout.box()
        
        # Header with toggle
        details_header = details_box.row()
        details_header.prop(props, "bone_details_show_ui", 
                           icon="TRIA_DOWN" if getattr(props, "bone_details_show_ui", False) else "TRIA_RIGHT", 
                           icon_only=True, emboss=False)
        details_header.label(text="Details & Companion Tools", icon='INFO')
        
        # Show content if expanded
        if getattr(props, "bone_details_show_ui", False):
            # Main description
            info_col = details_box.column(align=True)
            info_col.scale_y = 0.9
            
            info_col.label(text="🎯 Purpose:", icon='FILE_TICK')
            info_col.label(text="These bone transform tools are designed to work alongside")
            info_col.label(text="existing VRChat avatar editing workflows and tools.")
            
            details_box.separator()
            
            # Companion Tools Section
            companion_box = details_box.box()
            companion_box.label(text="🔧 Recommended Companion Tools", icon='TOOL_SETTINGS')
            
            # CATS Plugin
            cats_row = companion_box.row()
            cats_row.scale_y = 1.1
            cats_row.label(text="• CATS Blender Plugin (Unofficial)", icon='ARMATURE_DATA')
            
            cats_info = companion_box.column(align=True)
            cats_info.scale_y = 0.8
            cats_info.label(text="  └ Use for: Armature fixing, bone merging, pose mode controls")
            cats_info.label(text="  └ GitHub: github.com/teamneoneko/Cats-Blender-Plugin-Unofficial-")
            
            companion_box.separator()
            
            # Avatar Toolkit
            toolkit_row = companion_box.row()
            toolkit_row.scale_y = 1.1
            toolkit_row.label(text="• Avatar Toolkit", icon='MODIFIER_DATA')
            
            toolkit_info = companion_box.column(align=True)
            toolkit_info.scale_y = 0.8
            toolkit_info.label(text="  └ Use for: Advanced avatar optimization and utilities")
            toolkit_info.label(text="  └ GitHub: github.com/teamneoneko/Avatar-Toolkit")
            
            details_box.separator()
            
            # Integration Tips
            integration_box = details_box.box()
            integration_box.label(text="🔄 Integration Workflow", icon='LINKED')
            
            workflow_col = integration_box.column(align=True)
            workflow_col.scale_y = 0.85
            workflow_col.label(text="1. Import avatar and fix with CATS or Avatar Toolkit")
            workflow_col.label(text="2. Use Nyarc VRChat Tools for bone transform presets")
            workflow_col.label(text="3. Save/load different pose configurations easily")
            workflow_col.label(text="4. Export differences between armature states")
            workflow_col.label(text="5. Apply final transforms and finish with companion tools")
            
            details_box.separator()
            
            # Pose Mode Boneeditors Note
            boneedit_box = details_box.box()
            boneedit_box.label(text="🦴 Pose Mode Bone Editors", icon='POSE_HLT')
            
            boneedit_col = boneedit_box.column(align=True)
            boneedit_col.scale_y = 0.85
            boneedit_col.label(text="These tools complement existing pose mode bone editors:")
            boneedit_col.label(text="• Works alongside CATS 'Start/Stop Pose Mode'")
            boneedit_col.label(text="• Enhances Avatar Toolkit bone manipulation features")
            boneedit_col.label(text="• Provides preset system for quick pose switching")
            boneedit_col.label(text="• Adds compatibility checking for different rigs")
            
            details_box.separator()
            
            # Credits and Links
            credits_box = details_box.box()
            credits_box.scale_y = 0.8
            credits_box.label(text="🌐 Community Tools Ecosystem", icon='WORLD')
            
            credits_col = credits_box.column(align=True)
            credits_col.scale_y = 0.75
            credits_col.label(text="Part of the VRChat community's open-source toolkit")
            credits_col.label(text="Works best when combined with other community plugins")
            credits_col.label(text="Built for heavy VRChat avatar editing workflows")
            
            details_box.separator()
            
            # Development Credits
            dev_box = details_box.box()
            dev_box.scale_y = 0.8
            dev_box.label(text="👥 Development Team", icon='COMMUNITY')
            
            dev_col = dev_box.column(align=True)
            dev_col.scale_y = 0.75
            dev_col.label(text="• Nyarc - Project Maintainer")
            dev_col.label(text="• Claude Code - AI Coding Agent Helper")
    
    except Exception as e:
        # Fallback UI if there's an error
        error_box = layout.box()
        error_box.label(text="Details & Companion Tools (Error)", icon='ERROR')
        error_box.label(text=f"UI Error: {str(e)}", icon='INFO')
        print(f"Details UI Error: {e}")