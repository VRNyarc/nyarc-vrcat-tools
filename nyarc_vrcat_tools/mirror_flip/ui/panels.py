# Mirror Flip UI Panels

import bpy
from bpy.types import Panel

from ..utils.detection import auto_detect_flip_candidates
from ..utils.validation import validate_selected_objects


class VIEW3D_PT_mirror_flip_tools(Panel):
    """Mirror Flip Tools Panel"""
    bl_label = "Mirror Flip Tools"
    bl_idname = "VIEW3D_PT_mirror_flip_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nyarc VRChat Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        self.layout.label(text="", icon='MOD_MIRROR')
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mirror_flip_props if hasattr(context.scene, 'mirror_flip_props') else None
        
        # Selection info
        self._draw_selection_info(layout, context)
        
        # Separator
        layout.separator()
        
        # Main operations
        self._draw_main_operations(layout, context, props)
        
        # Separator  
        layout.separator()
        
        # Options
        if props:
            self._draw_options(layout, props)
        
        # Separator
        layout.separator()
        
        # Advanced operations
        self._draw_advanced_operations(layout, context)
    
    def _draw_selection_info(self, layout, context):
        """Draw information about current selection"""
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Selection:", icon='RESTRICT_SELECT_OFF')
        
        selected_objects = context.selected_objects
        mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
        armature_objects = [obj for obj in selected_objects if obj.type == 'ARMATURE']
        
        if not selected_objects:
            col.label(text="No objects selected", icon='INFO')
            return
        
        # Show mesh objects
        if mesh_objects:
            col.label(text=f"📦 Meshes ({len(mesh_objects)}):")
            for i, obj in enumerate(mesh_objects[:3]):  # Show max 3
                col.label(text=f"  • {obj.name}")
            if len(mesh_objects) > 3:
                col.label(text=f"  ... and {len(mesh_objects) - 3} more")
        
        # Show armature objects
        if armature_objects:
            col.label(text=f"🦴 Armatures ({len(armature_objects)}):")
            for i, obj in enumerate(armature_objects[:2]):  # Show max 2
                col.label(text=f"  • {obj.name}")
            if len(armature_objects) > 2:
                col.label(text=f"  ... and {len(armature_objects) - 2} more")
        
        # Show validation warnings
        if mesh_objects or armature_objects:
            errors, warnings = validate_selected_objects()
            if warnings:
                col.separator()
                col.label(text="⚠️ Warnings:", icon='ERROR')
                for warning in warnings[:2]:  # Show max 2 warnings
                    col.label(text=f"  {warning}", icon='DOT')
    
    def _draw_main_operations(self, layout, context, props):
        """Draw main flip operations"""
        box = layout.box()
        col = box.column(align=True)
        col.label(text="🔄 Flip Operations:", icon='MOD_MIRROR')
        
        # Check what's selected
        selected_objects = context.selected_objects
        has_meshes = any(obj.type == 'MESH' for obj in selected_objects)
        has_armatures = any(obj.type == 'ARMATURE' for obj in selected_objects)
        
        # Main combined operation
        row = col.row(align=True)
        row.scale_y = 1.5
        op = row.operator("object.flip_mesh_and_bones_combined", text="Flip to Other Side", icon='MOD_MIRROR')
        if props:
            op.auto_detect_bones = props.auto_detect_bones
            op.apply_transforms = props.apply_transforms
            op.auto_rename = props.auto_rename
            op.mirror_axis = props.mirror_axis
        
        # Show what will be flipped
        if context.mode == 'OBJECT':
            try:
                candidates = auto_detect_flip_candidates()
                if candidates['meshes'] or candidates['bones']:
                    subrow = col.row()
                    subrow.scale_y = 0.8
                    info_text = ""
                    if candidates['meshes']:
                        info_text += f"{len(candidates['meshes'])} mesh(es)"
                    if candidates['bones']:
                        if info_text:
                            info_text += ", "
                        info_text += f"{len(candidates['bones'])} bone(s)"
                    subrow.label(text=f"Will flip: {info_text}", icon='INFO')
            except:
                pass  # Auto-detection failed, continue without info
        
        # Enable/disable based on selection
        if not (has_meshes or has_armatures):
            col.enabled = False
            col.label(text="Select mesh or armature objects", icon='INFO')
    
    def _draw_options(self, layout, props):
        """Draw options for flip operations"""
        box = layout.box()
        col = box.column(align=True)
        col.label(text="⚙️ Options:", icon='PREFERENCES')
        
        # Auto-detection
        col.prop(props, "auto_detect_bones", text="Auto-detect bones")
        
        # Transform options
        col.prop(props, "apply_transforms", text="Apply transforms")
        col.prop(props, "auto_rename", text="Auto-rename (.L → .R)")
        
        # Mirror axis
        col.prop(props, "mirror_axis", text="Mirror Axis")
        
        # Keep original selected
        col.prop(props, "keep_original_selected", text="Keep original selected")
    
    def _draw_advanced_operations(self, layout, context):
        """Draw advanced/individual operations"""
        box = layout.box()
        col = box.column(align=True)
        col.label(text="📋 Individual Operations:", icon='PRESET')
        
        # Individual operators
        selected_objects = context.selected_objects
        has_meshes = any(obj.type == 'MESH' for obj in selected_objects)
        has_armatures = any(obj.type == 'ARMATURE' for obj in selected_objects)
        
        row = col.row(align=True)
        
        # Mesh only
        mesh_col = row.column()
        mesh_col.enabled = (context.mode == 'OBJECT' and has_meshes)
        mesh_op = mesh_col.operator("object.flip_mesh", text="Mesh Only", icon='MESH_DATA')
        mesh_op.apply_transforms = True
        mesh_op.auto_rename = True
        
        # Bones only  
        bone_col = row.column()
        bone_col.enabled = (has_armatures and context.mode in ['OBJECT', 'EDIT_ARMATURE'])
        bone_op = bone_col.operator("armature.flip_bones", text="Bones Only", icon='BONE_DATA')
        bone_op.auto_rename = True
        bone_op.apply_armature_transforms = True


class VIEW3D_PT_mirror_flip_detection(Panel):
    """Mirror Flip Detection Subpanel"""
    bl_label = "Detection Info"
    bl_idname = "VIEW3D_PT_mirror_flip_detection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nyarc VRChat Tools"
    bl_parent_id = "VIEW3D_PT_mirror_flip_tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        self.layout.label(text="", icon='VIEWZOOM')
    
    def draw(self, context):
        layout = self.layout
        
        if context.mode != 'OBJECT':
            layout.label(text="Switch to Object Mode", icon='INFO')
            return
        
        try:
            # Show auto-detection results
            candidates = auto_detect_flip_candidates()
            
            col = layout.column(align=True)
            
            # Detected meshes
            if candidates['meshes']:
                col.label(text=f"📦 Detected Meshes ({len(candidates['meshes'])}):")
                for mesh_name in candidates['meshes'][:5]:  # Show max 5
                    col.label(text=f"  • {mesh_name}")
                if len(candidates['meshes']) > 5:
                    col.label(text=f"  ... and {len(candidates['meshes']) - 5} more")
            else:
                col.label(text="📦 No suitable meshes detected")
            
            col.separator()
            
            # Detected bones
            if candidates['bones']:
                col.label(text=f"🦴 Detected Bones ({len(candidates['bones'])}):")
                for bone_name in candidates['bones'][:5]:  # Show max 5
                    col.label(text=f"  • {bone_name}")
                if len(candidates['bones']) > 5:
                    col.label(text=f"  ... and {len(candidates['bones']) - 5} more")
            else:
                col.label(text="🦴 No suitable bones detected")
            
            col.separator()
            
            # Relationships
            if candidates['relationships']:
                col.label(text="🔗 Mesh-Armature Links:")
                for mesh_name, relationships in candidates['relationships'].items():
                    for rel in relationships[:2]:  # Show max 2 per mesh
                        armature_name = rel['armature'].name if rel['armature'] else 'Unknown'
                        col.label(text=f"  {mesh_name} → {armature_name}")
            
        except Exception as e:
            layout.label(text=f"Detection failed: {str(e)}", icon='ERROR')


# Registration
classes = (
    VIEW3D_PT_mirror_flip_tools,
    VIEW3D_PT_mirror_flip_detection,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass