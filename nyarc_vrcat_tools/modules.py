# Module Management System
# Bridges the main addon with the modular structure

import bpy
from .core.registry import ModuleRegistry, try_import_module

# Global registry instance
registry = ModuleRegistry.get_instance()

# Import all available modules
shapekey_module, SHAPEKEY_AVAILABLE = try_import_module('nyarc_vrcat_tools.shapekey_transfer', 'shapekey_transfer')
bone_transforms_module, BONE_TRANSFORMS_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms', 'bone_transforms')
bone_transform_saver_module, BONE_TRANSFORM_SAVER_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transform_saver', 'bone_transform_saver')
details_module, DETAILS_AVAILABLE = try_import_module('nyarc_vrcat_tools.details_companion_tools', 'details_companion_tools')
mirror_flip_module, MIRROR_FLIP_AVAILABLE = try_import_module('nyarc_vrcat_tools.mirror_flip', 'mirror_flip')

def register_modules():
    """Register all available modules"""
    print("[REGISTER] Registering Nyarc VRCat Tools modules...")
    
    # Register core modules
    if SHAPEKEY_AVAILABLE and hasattr(shapekey_module, 'register'):
        try:
            # Use the module's own register function
            shapekey_module.register()
            print("[OK] Shape Key Transfer module registered")
        except Exception as e:
            print(f"[ERROR] Failed to register Shape Key Transfer: {e}")
            # Fallback to manual registration
            try:
                shapekey_classes = [shapekey_module.MESH_OT_transfer_shape_key]
                if hasattr(shapekey_module, 'VIEW3D_PT_shapekey_transfer'):
                    shapekey_classes.append(shapekey_module.VIEW3D_PT_shapekey_transfer)
                
                for cls in shapekey_classes:
                    bpy.utils.register_class(cls)
                print("[OK] Shape Key Transfer module registered (fallback)")
            except Exception as fallback_e:
                print(f"[ERROR] Fallback registration also failed: {fallback_e}")
    
    # Register bone transforms module
    print(f"[DEBUG] BONE_TRANSFORMS_AVAILABLE: {BONE_TRANSFORMS_AVAILABLE}")
    print(f"[DEBUG] Has register_module: {hasattr(bone_transforms_module, 'register_module') if BONE_TRANSFORMS_AVAILABLE else 'N/A'}")
    
    if BONE_TRANSFORMS_AVAILABLE and hasattr(bone_transforms_module, 'register_module'):
        try:
            print("[DEBUG] Calling bone_transforms_module.register_module()...")
            bone_transforms_module.register_module()
            print("[OK] Bone Transforms module registered")
        except Exception as e:
            print(f"[ERROR] Failed to register Bone Transforms: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[WARN] Bone Transforms module not available or missing register_module function")
    
    # NOTE: Bone Transform Saver registration disabled - operators now handled by bone_transforms module
    print("[DEBUG] Bone Transform Saver registration disabled - using bone_transforms module instead")
    
    # Register details module
    if DETAILS_AVAILABLE and hasattr(details_module, 'register'):
        try:
            details_module.register()
            print("[OK] Details & Companion Tools module registered")
        except Exception as e:
            print(f"[ERROR] Failed to register Details module: {e}")
    
    # Register mirror flip module
    if MIRROR_FLIP_AVAILABLE and hasattr(mirror_flip_module, 'register_module'):
        try:
            mirror_flip_module.register_module()
            print("[OK] Mirror Flip module registered")
        except Exception as e:
            print(f"[ERROR] Failed to register Mirror Flip module: {e}")
            import traceback
            traceback.print_exc()

def unregister_modules():
    """Unregister all modules"""
    print("[UNREGISTER] Unregistering Nyarc VRCat Tools modules...")
    
    # NOTE: Bone Transform Saver unregistration disabled - handled by bone_transforms module
    print("[DEBUG] Bone Transform Saver unregistration disabled")
    
    # Unregister mirror flip module
    if MIRROR_FLIP_AVAILABLE and hasattr(mirror_flip_module, 'unregister_module'):
        try:
            mirror_flip_module.unregister_module()
        except:
            pass
    
    # Unregister details module
    if DETAILS_AVAILABLE and hasattr(details_module, 'unregister'):
        try:
            details_module.unregister()
        except:
            pass
    
    if BONE_TRANSFORMS_AVAILABLE and hasattr(bone_transforms_module, 'unregister_module'):
        try:
            bone_transforms_module.unregister_module()
        except:
            pass
    
    if SHAPEKEY_AVAILABLE:
        try:
            # Use module's own unregister function if available
            if hasattr(shapekey_module, 'unregister'):
                shapekey_module.unregister()
            else:
                # Fallback to manual unregistration
                shapekey_classes = [shapekey_module.MESH_OT_transfer_shape_key]
                if hasattr(shapekey_module, 'VIEW3D_PT_shapekey_transfer'):
                    shapekey_classes.append(shapekey_module.VIEW3D_PT_shapekey_transfer)
                
                for cls in reversed(shapekey_classes):
                    try:
                        bpy.utils.unregister_class(cls)
                    except:
                        pass
        except:
            pass

def draw_modules(layout, context):
    """Draw UI for all available modules"""
    props = context.scene.nyarc_tools_props
    
    # Shape Key Transfer UI
    if SHAPEKEY_AVAILABLE:
        shapekey_box = layout.box()
        shapekey_header = shapekey_box.row()
        shapekey_header.label(text="Shape Key Transfer", icon='SHAPEKEY_DATA')
        shapekey_header.prop(props, "shapekey_show_ui", text="", icon='TRIA_DOWN' if props.shapekey_show_ui else 'TRIA_RIGHT')
        
        if props.shapekey_show_ui:
            # Use the module's own draw_ui function if available
            if hasattr(shapekey_module, 'draw_ui'):
                shapekey_module.draw_ui(shapekey_box, context)
            else:
                # Fallback to basic UI
                draw_shapekey_ui(shapekey_box, context, props)
    
    # Pose Mode Bone Editor (main category)
    if BONE_TRANSFORM_SAVER_AVAILABLE:
        bone_box = layout.box()
        bone_header = bone_box.row()
        bone_header.label(text="Pose Mode Bone Editor", icon='POSE_HLT')
        bone_header.prop(props, "bone_show_ui", text="", icon='TRIA_DOWN' if props.bone_show_ui else 'TRIA_RIGHT')
        
        if props.bone_show_ui:
            draw_bone_saver_ui(bone_box, context, props)
    
    # Mirror Flip Tools UI
    if MIRROR_FLIP_AVAILABLE:
        mirror_flip_box = layout.box()
        mirror_flip_header = mirror_flip_box.row()
        mirror_flip_header.label(text="Mirror Flip Tools", icon='MOD_MIRROR')
        mirror_flip_header.prop(props, "mirror_flip_show_ui", text="", icon='TRIA_DOWN' if props.mirror_flip_show_ui else 'TRIA_RIGHT')
        
        if props.mirror_flip_show_ui:
            draw_mirror_flip_ui(mirror_flip_box, context, props)
    
    # Details & Companion Tools UI (standalone module at bottom)
    if DETAILS_AVAILABLE:
        details_module.draw_details_ui(layout, context, props)

def draw_shapekey_ui(layout, context, props):
    """Draw Shape Key Transfer UI"""
    # Source object selection
    layout.label(text="Source Mesh (with shape keys):")
    layout.prop(props, "shapekey_source_object", text="")
    
    # Target object selection
    layout.label(text="Target Mesh (to transfer to):")
    layout.prop(props, "shapekey_target_object", text="")
    
    # Shape key selection
    if props.shapekey_source_object and props.shapekey_source_object.data and props.shapekey_source_object.data.shape_keys:
        layout.label(text="Shape Key to Transfer:")
        layout.prop(props, "shapekey_shape_key", text="")
        
        # Transfer button
        if props.shapekey_target_object and props.shapekey_shape_key != "NONE":
            layout.operator("mesh.transfer_shape_key", text="Transfer Shape Key", icon='FORWARD')
    else:
        layout.label(text="Select source mesh with shape keys", icon='INFO')

def draw_bone_saver_ui(layout, context, props):
    """Draw Bone Transform Saver UI - call the full UI from bone_transform_saver"""
    if BONE_TRANSFORM_SAVER_AVAILABLE and hasattr(bone_transform_saver_module, 'draw_ui'):
        # Call the full UI from bone_transform_saver module
        bone_transform_saver_module.draw_ui(layout, context)
    else:
        # Fallback basic UI
        layout.label(text="Bone Transform Saver module not available!", icon='ERROR')
        layout.label(text="Armature:")
        layout.prop(props, "bone_armature_object", text="")
        
        if props.bone_armature_object:
            layout.label(text="Preset Name:")
            layout.prop(props, "bone_preset_name", text="")
            
            row = layout.row(align=True)
            row.operator("armature.save_bone_transforms", text="Save Transforms", icon='FILE_TICK')
            row.operator("armature.load_bone_transforms", text="Load Transforms", icon='FILE_FOLDER')

def draw_mirror_flip_ui(layout, context, props):
    """Draw Mirror Flip Tools UI"""
    # Import detection utilities
    try:
        from .mirror_flip.utils.detection import auto_detect_flip_candidates
        from .mirror_flip.utils.validation import validate_selected_objects
    except ImportError:
        layout.label(text="Mirror Flip module not available!", icon='ERROR')
        return
    
    # Selection info
    selected_objects = context.selected_objects
    mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
    armature_objects = [obj for obj in selected_objects if obj.type == 'ARMATURE']
    
    # Current selection display
    col = layout.column(align=True)
    col.label(text="Selection:", icon='RESTRICT_SELECT_OFF')
    
    if not selected_objects:
        col.label(text="No objects selected", icon='INFO')
    else:
        if mesh_objects:
            col.label(text=f"📦 {len(mesh_objects)} mesh(es)")
        if armature_objects:
            col.label(text=f"🦴 {len(armature_objects)} armature(s)")
    
    layout.separator()
    
    # Main flip operation
    col = layout.column(align=True)
    col.label(text="Flip Operations:", icon='MOD_MIRROR')
    
    # Main combined operation
    row = col.row(align=True)
    row.scale_y = 1.2
    
    # Get properties from mirror flip module if available
    mirror_props = getattr(context.scene, 'mirror_flip_props', None)
    
    op = row.operator("object.flip_mesh_and_bones_combined", text="Flip to Other Side", icon='MOD_MIRROR')
    if mirror_props:
        op.auto_detect_bones = mirror_props.auto_detect_bones
        op.apply_transforms = mirror_props.apply_transforms
        op.auto_rename = mirror_props.auto_rename
        op.mirror_axis = mirror_props.mirror_axis
        op.manual_mode = mirror_props.manual_mode
        op.manual_direction = mirror_props.manual_direction
    
    # Show what will be flipped (if in object mode)
    if context.mode == 'OBJECT' and selected_objects:
        try:
            candidates = auto_detect_flip_candidates()
            if candidates['meshes'] or candidates['bones']:
                info_row = col.row()
                info_row.scale_y = 0.8
                info_text = ""
                if candidates['meshes']:
                    info_text += f"{len(candidates['meshes'])} mesh(es)"
                if candidates['bones']:
                    if info_text:
                        info_text += ", "
                    info_text += f"{len(candidates['bones'])} bone(s)"
                info_row.label(text=f"Will flip: {info_text}", icon='INFO')
        except:
            pass  # Auto-detection failed, continue without info
    
    layout.separator()
    
    # Options section
    if mirror_props:
        col = layout.column(align=True)
        col.label(text="Options:", icon='PREFERENCES')
        
        # Auto-detection toggle
        col.prop(mirror_props, "auto_detect_bones", text="Auto-detect bones")
        
        # Mirror axis selection
        col.prop(mirror_props, "mirror_axis", text="Mirror Axis")
        
        # Manual mode toggle
        col.prop(mirror_props, "manual_mode", text="Manual Mode")
        
        # Manual direction (only if manual mode is enabled)
        if mirror_props.manual_mode:
            sub_col = col.column(align=True)
            sub_col.enabled = True
            sub_col.prop(mirror_props, "manual_direction", text="Direction")
        
        # Transform options
        col.prop(mirror_props, "apply_transforms", text="Apply transforms")
        col.prop(mirror_props, "auto_rename", text="Auto-rename")
        col.prop(mirror_props, "keep_original_selected", text="Keep original selected")
    
    layout.separator()
    
    # Individual operations
    col = layout.column(align=True)
    col.label(text="Individual Operations:", icon='PRESET')
    
    # Individual operators
    has_meshes = any(obj.type == 'MESH' for obj in selected_objects)
    has_armatures = any(obj.type == 'ARMATURE' for obj in selected_objects)
    
    row = col.row(align=True)
    
    # Mesh only
    mesh_col = row.column()
    mesh_col.enabled = (context.mode == 'OBJECT' and has_meshes)
    mesh_op = mesh_col.operator("object.flip_mesh", text="Mesh Only", icon='MESH_DATA')
    mesh_op.apply_transforms = True
    mesh_op.auto_rename = True
    if mirror_props:
        mesh_op.mirror_axis = mirror_props.mirror_axis
    
    # Bones only  
    bone_col = row.column()
    bone_col.enabled = (has_armatures and context.mode in ['OBJECT', 'EDIT_ARMATURE'])
    bone_op = bone_col.operator("armature.flip_bones", text="Bones Only", icon='BONE_DATA')
    bone_op.auto_rename = True
    bone_op.apply_armature_transforms = True
    if mirror_props:
        bone_op.mirror_axis = mirror_props.mirror_axis
        bone_op.manual_mode = mirror_props.manual_mode
    
    # Enable/disable main operation
    if not (has_meshes or has_armatures):
        col.enabled = False

