# Details and Companion Tools Module - Standalone
# Information about all tools and integration with other VRChat workflow tools

import bpy
from bpy.types import Operator

class INFO_OT_open_documentation(Operator):
    """Open VRChat Avatar Tools documentation"""
    bl_idname = "info.open_documentation"
    bl_label = "Open Documentation"
    bl_description = "Open VRChat Avatar Tools documentation in web browser"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        import webbrowser
        # Replace with actual documentation URL
        webbrowser.open("https://github.com/vrchat-community/avatar-tools")
        self.report({'INFO'}, "Documentation opened in web browser")
        return {'FINISHED'}


class INFO_OT_open_support(Operator):
    """Open support and community links"""
    bl_idname = "info.open_support"
    bl_label = "Get Support"
    bl_description = "Open support channels and community resources"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        import webbrowser
        # Replace with actual support URL
        webbrowser.open("https://discord.gg/vrchat")
        self.report({'INFO'}, "Support resources opened in web browser")
        return {'FINISHED'}


class INFO_OT_open_nyarc_github(Operator):
    """Open Nyarc VRCat Tools GitHub repository"""
    bl_idname = "info.open_nyarc_github"
    bl_label = "GitHub Repository"
    bl_description = "Open the Nyarc VRCat Tools GitHub repository"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        import webbrowser
        webbrowser.open("https://github.com/nyarc-labs/vrchat-tools")
        self.report({'INFO'}, "GitHub repository opened in web browser")
        return {'FINISHED'}


def draw_details_ui(layout, context, props):
    """Draw the Details/Information section about all modules and companion tools"""
    try:
        details_box = layout.box()
        
        # Header with toggle (matching other modules' style)
        details_header = details_box.row()
        details_header.label(text="Details & Companion Tools", icon='INFO')
        details_header.prop(props, "bone_details_show_ui", text="", icon='TRIA_DOWN' if getattr(props, "bone_details_show_ui", False) else 'TRIA_RIGHT')
        
        # Show content if expanded
        if getattr(props, "bone_details_show_ui", False):
            # Main description - Updated to describe ALL modules
            info_col = details_box.column(align=True)
            info_col.scale_y = 0.9
            
            info_col.label(text="🎯 Purpose:", icon='FILE_TICK')
            info_col.label(text="Comprehensive toolkit for VRChat avatar editing workflows")
            info_col.label(text="providing shape key transfer, bone transform tools, and more.")
            
            details_box.separator()
            
            # Available Modules Overview
            modules_box = details_box.box()
            modules_box.label(text="📦 Available Modules", icon='OUTLINER_OB_GROUP_INSTANCE')
            
            modules_col = modules_box.column(align=True)
            modules_col.scale_y = 0.85
            
            # Shape Key Transfer
            shapekey_row = modules_col.row()
            shapekey_row.label(text="🔄 Shape Key Transfer", icon='SHAPEKEY_DATA')
            shapekey_info = modules_col.column(align=True)
            shapekey_info.scale_y = 0.8
            shapekey_info.label(text="  • Transfer shape keys between different mesh topologies")
            shapekey_info.label(text="  • Uses Surface Deform for accurate deformation mapping")
            shapekey_info.label(text="  • Supports drag-and-drop object selection")
            
            modules_col.separator(factor=0.5)
            
            # Pose Mode Bone Editor
            pose_row = modules_col.row()
            pose_row.label(text="🦴 Pose Mode Bone Editor", icon='POSE_HLT')
            pose_info = modules_col.column(align=True)
            pose_info.scale_y = 0.8
            pose_info.label(text="  • Save and load bone transform presets")
            pose_info.label(text="  • Professional-grade precision correction")
            pose_info.label(text="  • Armature diff export for change tracking")
            pose_info.label(text="  • Pose history and undo system")
            
            details_box.separator()
            
            # Companion Tools Section - Updated for broader compatibility
            companion_box = details_box.box()
            companion_box.label(text="🛠️ Recommended Companion Tools", icon='TOOL_SETTINGS')
            
            # CATS Plugin
            cats_row = companion_box.row()
            cats_row.scale_y = 1.1
            cats_row.label(text="🐱 CATS Blender Plugin (Unofficial)", icon='ARMATURE_DATA')
            
            cats_info = companion_box.column(align=True)
            cats_info.scale_y = 0.8
            cats_info.label(text="  ✓ Use for: Armature fixing, bone merging, basic pose controls")
            cats_info.label(text="  ✓ GitHub: github.com/teamneoneko/Cats-Blender-Plugin-Unofficial")
            cats_info.label(text="  ✓ Works alongside: All Nyarc VRCat Tools modules")
            
            companion_box.separator()
            
            # Avatar Toolkit
            toolkit_row = companion_box.row()
            toolkit_row.scale_y = 1.1
            toolkit_row.label(text="🔧 Avatar Toolkit", icon='MODIFIER_DATA')
            
            toolkit_info = companion_box.column(align=True)
            toolkit_info.scale_y = 0.8
            toolkit_info.label(text="  ✓ Use for: Advanced avatar optimization and utilities")
            toolkit_info.label(text="  ✓ GitHub: github.com/teamneoneko/Avatar-Toolkit")
            toolkit_info.label(text="  ✓ Complements: Shape key transfer and bone tools")
            
            companion_box.separator()
            
            # VRM Tools
            vrm_row = companion_box.row()
            vrm_row.scale_y = 1.1
            vrm_row.label(text="🤖 VRM Import/Export Tools", icon='IMPORT')
            
            vrm_info = companion_box.column(align=True)
            vrm_info.scale_y = 0.8
            vrm_info.label(text="  ✓ Use for: VRM avatar format support")
            vrm_info.label(text="  ✓ Works with: All shape key and bone transform workflows")
            
            details_box.separator()
            
            # Integration Workflow - Updated for all modules
            integration_box = details_box.box()
            integration_box.label(text="🔗 Integration Workflow", icon='LINKED')
            
            workflow_col = integration_box.column(align=True)
            workflow_col.scale_y = 0.85
            workflow_col.label(text="1. Import avatar and fix with CATS or Avatar Toolkit")
            workflow_col.label(text="2. Use Shape Key Transfer for expression/viseme setup")
            workflow_col.label(text="3. Use Pose Mode Bone Editor for bone transform presets")
            workflow_col.label(text="4. Save/load different configurations for testing")
            workflow_col.label(text="5. Export final transforms and finish with companion tools")
            
            details_box.separator()
            
            # Tool Categories - New section describing tool types
            categories_box = details_box.box()
            categories_box.label(text="📋 Tool Categories", icon='OUTLINER_COLLECTION')
            
            categories_col = categories_box.column(align=True)
            categories_col.scale_y = 0.85
            categories_col.label(text="🔄 Mesh Tools: Shape key transfer, deformation mapping")
            categories_col.label(text="🦴 Armature Tools: Bone transforms, presets, diff export")
            categories_col.label(text="⚙️ Workflow Tools: Integration helpers, companion tool support")
            categories_col.label(text="🎯 Quality Tools: Precision correction, compatibility checking")
            
            details_box.separator()
            
            # Quick Action Buttons
            actions_box = details_box.box()
            actions_box.label(text="🚀 Quick Actions", icon='TOOL_SETTINGS')
            
            actions_row = actions_box.row()
            actions_row.scale_y = 1.2
            actions_row.operator("info.open_documentation", text="Documentation", icon='HELP')
            actions_row.operator("info.open_support", text="Support", icon='COMMUNITY') 
            actions_row.operator("info.open_nyarc_github", text="GitHub", icon='URL')
            
            details_box.separator()
            
            # Credits and Community
            credits_box = details_box.box()
            credits_box.scale_y = 0.8
            credits_box.label(text="🌍 Community Tools Ecosystem", icon='WORLD')
            
            credits_col = credits_box.column(align=True)
            credits_col.scale_y = 0.75
            credits_col.label(text="Part of the VRChat community's open-source toolkit")
            credits_col.label(text="Works best when combined with other community plugins")
            credits_col.label(text="Built for professional and amateur VRChat avatar workflows")
            
            # Development Credits
            dev_box = details_box.box()
            dev_box.scale_y = 0.8
            dev_box.label(text="👥 Development Team", icon='COMMUNITY')
            
            dev_col = dev_box.column(align=True)
            dev_col.scale_y = 0.75
            dev_col.label(text="🎯 Nyarc - Project Maintainer & Lead Developer")
            dev_col.label(text="🤖 Claude Code - AI Coding Agent & Architecture Assistant")
            dev_col.label(text="🌟 VRChat Community - Feature requests & testing")
    
    except Exception as e:
        # Fallback UI if there's an error
        error_box = layout.box()
        error_box.label(text="Details & Companion Tools (Error)", icon='ERROR')
        error_box.label(text=f"UI Error: {str(e)}", icon='INFO')
        print(f"Details UI Error: {e}")


# Operator classes for registration
classes = (
    INFO_OT_open_documentation,
    INFO_OT_open_support,
    INFO_OT_open_nyarc_github,
)


def register():
    """Register the operators"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister the operators"""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass