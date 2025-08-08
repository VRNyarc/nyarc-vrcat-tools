bl_info = {
    "name": "Nyarc VRCat Tools",
    "blender": (4, 0, 0),
    "category": "3D View", 
    "version": (0, 3, 1),
    "author": "Nyarc",
    "description": "Small quality-of-life addons for heavy VRCat avatar editing - Shape Key Transfer, Bone Transform Saver, Armature Diff Export, and more!",
    "location": "View3D > Sidebar > Nyarc VRCat Tools",
    "support": "COMMUNITY",
}

import bpy
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty
from bpy.types import Panel, PropertyGroup, Object

# Import all modules
from . import modules


def armature_poll(self, obj):
    """Poll function to filter armature objects"""
    return obj and obj.type == 'ARMATURE'


def mesh_poll(self, obj):
    """Poll function to filter mesh objects"""
    return obj and obj.type == 'MESH'


class ShapeKeyTargetItem(PropertyGroup):
    """Individual target object for shape key transfer"""
    target_object: PointerProperty(
        name="Target Mesh",
        description="Mesh to transfer shape keys to",
        type=Object,
        poll=mesh_poll
    )


class ShapeKeySelectionItem(PropertyGroup):
    """Individual shape key selection state"""
    name: StringProperty(
        name="Shape Key Name",
        description="Name of the shape key"
    )
    
    selected: BoolProperty(
        name="Selected",
        description="Whether this shape key is selected for transfer",
        default=False
    )


class NyarcToolsProperties(PropertyGroup):
    """Main properties container for all Nyarc Tools"""
    
    # UI expansion toggles
    shapekey_show_ui: BoolProperty(
        name="Show Shape Key Transfer",
        description="Show/hide Shape Key Transfer panel",
        default=True
    )
    
    bone_show_ui: BoolProperty(
        name="Show Bone Transform Saver", 
        description="Show/hide Bone Transform Saver panel",
        default=False
    )
    
    bone_diff_show_ui: BoolProperty(
        name="Show Armature Diff Export",
        description="Show/hide Armature Diff Export panel",
        default=False
    )
    
    def shapekey_source_update_callback(self, context):
        """Called when source object changes - update shape key selections"""
        try:
            self.update_shape_key_selections(context)
        except Exception as e:
            print(f"Error updating shape key selections: {e}")
    
    # Shape Key Transfer Properties (prefixed to avoid conflicts)
    shapekey_source_object: PointerProperty(
        name="Source Mesh",
        description="Mesh with shape keys to transfer from (drag from Outliner)",
        type=Object,
        poll=mesh_poll,
        update=shapekey_source_update_callback
    )
    
    shapekey_target_object: PointerProperty(
        name="Target Mesh", 
        description="Mesh to transfer shape keys to (drag from Outliner)",
        type=Object,
        poll=mesh_poll
    )
    
    shapekey_shape_key: EnumProperty(
        name="Shape Key",
        description="Shape key to transfer",
        items=lambda self, context: self.get_shape_keys(context),
        default=0
    )
    
    # Multi-target and multi-shape key properties
    shapekey_target_objects: CollectionProperty(
        name="Target Objects",
        description="Collection of target meshes for batch transfer",
        type=ShapeKeyTargetItem
    )
    
    shapekey_selected_keys: CollectionProperty(
        name="Selected Shape Keys",
        description="Collection of selected shape keys for batch transfer",
        type=ShapeKeySelectionItem
    )
    
    # UI mode toggle
    shapekey_multi_mode: BoolProperty(
        name="Multi-Target Mode",
        description="Enable multi-target and multi-shape key transfer mode",
        default=False
    )
    
    # Transfer options
    shapekey_override_existing: BoolProperty(
        name="Override Existing",
        description="Replace existing shape keys with the same name",
        default=False
    )
    
    shapekey_skip_existing: BoolProperty(
        name="Skip Existing",
        description="Skip transfer if shape key already exists on target",
        default=False
    )
    
    # Active index for scrollable shape key list
    shapekey_active_index: IntProperty(
        name="Active Shape Key Index",
        description="Currently active shape key in the scrollable list",
        default=0,
        min=0
    )
    
    # Live preview and synchronization properties
    shapekey_preview_mode: BoolProperty(
        name="Show Live Preview",
        description="Show live shape key synchronization preview panel",
        default=False
    )
    
    shapekey_sync_enabled: BoolProperty(
        name="Enable Sync",
        description="Enable live synchronization of shape key values between meshes",
        default=False
    )
    
    shapekey_help_expanded: BoolProperty(
        name="Show Help",
        description="Show/hide help information panel",
        default=False
    )
    
    def armature_update_callback(self, context):
        """Called when armature selection changes - update inherit scale warning"""
        if self.bone_armature_object:
            try:
                # Import and call the update function safely
                from .bone_transforms.operators.inherit_scale import update_inherit_scale_warning
                update_inherit_scale_warning(self.bone_armature_object)
            except ImportError:
                # Module not ready yet, skip silently
                pass
            except Exception as e:
                print(f"Error in armature update callback: {e}")
    
    # Bone Transform Saver Properties (prefixed to avoid conflicts)  
    bone_armature_object: PointerProperty(
        name="Armature",
        description="Armature to save/load bone transforms from",
        type=Object,
        poll=armature_poll,
        update=armature_update_callback
    )
    
    bone_preset_name: StringProperty(
        name="Preset Name",
        description="Name for the bone transform preset",
        default="BonePreset"
    )
    
    bone_editing_active: BoolProperty(
        name="Bone Editing Active",
        description="Whether pose mode editing is currently active",
        default=False
    )
    
    bone_presets_show_ui: BoolProperty(
        name="Show Transform Presets",
        description="Show/hide Transform Presets section",
        default=True
    )
    
    # Preset scrolling properties for handling large preset lists
    bone_presets_scroll_offset: IntProperty(
        name="Presets Scroll Offset",
        description="Current scroll position in preset list",
        default=0,
        min=0
    )
    
    bone_presets_items_per_page: IntProperty(
        name="Presets Per Page",
        description="Number of presets to show at once",
        default=8,
        min=3,
        max=20
    )
    
    # Armature Diff Export Properties (for comparing two armatures)
    bone_diff_original_armature: PointerProperty(
        name="Original Armature",
        description="Base/original armature with default transforms",
        type=Object,
        poll=armature_poll
    )
    
    bone_diff_modified_armature: PointerProperty(
        name="Modified Armature", 
        description="Armature with saved/changed bone transforms",
        type=Object,
        poll=armature_poll
    )
    
    bone_diff_preset_name: StringProperty(
        name="Diff Preset Name",
        description="Name for the armature difference preset",
        default="DiffPreset"
    )
    
    bone_details_show_ui: BoolProperty(
        name="Show Details & Companion Tools",
        description="Show/hide Details and Companion Tools information panel",
        default=False
    )
    
    def pose_history_enabled_callback(self, context):
        """Callback when pose history enabled state changes"""
        if self.pose_history_enabled:
            # User just enabled pose history - show education popup
            try:
                bpy.ops.armature.pose_history_education_popup('INVOKE_DEFAULT')
            except Exception as e:
                print(f"Could not show pose history education popup: {e}")
        else:
            # User disabled pose history - check if they have existing history and warn
            if self.bone_armature_object:
                try:
                    # Check if pose history exists using new armature modifier system
                    from .bone_transforms.pose_history.metadata_storage import has_shape_key_pose_history
                    
                    if has_shape_key_pose_history(self.bone_armature_object):
                        # They have existing history - show warning
                        bpy.ops.armature.pose_history_disable_warning('INVOKE_DEFAULT')
                except Exception as e:
                    print(f"Could not check pose history status: {e}")
    
    # Pose History Properties
    pose_history_enabled: BoolProperty(
        name="Enable Pose History",
        description="Auto-save pose state before 'Apply as Rest Pose' operations. Creates hidden metadata for revert functionality.",
        default=False,  # Default OFF - user must opt-in
        update=pose_history_enabled_callback
    )
    
    pose_history_show_ui: BoolProperty(
        name="Show Pose History",
        description="Show/hide Pose History section in pose mode",
        default=True
    )
    
    # Mirror Flip Properties
    mirror_flip_show_ui: BoolProperty(
        name="Show Mirror Flip Tools",
        description="Show/hide Mirror Flip Tools section",
        default=True
    )
    
    # Precision Correction Properties
    apply_precision_correction: BoolProperty(
        name="Apply Precision Correction",
        description="🚨 CRITICAL: Only for EXACT SAME base armature used for diff export! Automatically applies precision correction for amateur models with mixed inherit scale settings. DO NOT use on different armatures - bones will move to wrong absolute positions. Only works with original armature used to create the preset",
        default=True
    )
    
    def get_shape_keys(self, context):
        """Get shape keys from source object for dropdown"""
        items = [("NONE", "Select Shape Key", "Select a shape key")]
        
        try:
            source_obj = self.shapekey_source_object
            
            # Verify object is still valid and has shape keys
            if (source_obj and source_obj.type == 'MESH' and 
                hasattr(source_obj, 'data') and source_obj.data and
                hasattr(source_obj.data, 'shape_keys') and source_obj.data.shape_keys):
                
                for shape_key in source_obj.data.shape_keys.key_blocks:
                    if shape_key.name and shape_key.name != "Basis":  # Skip basis shape key
                        tooltip = f"Shape key: {shape_key.name}"
                        items.append((shape_key.name, shape_key.name, tooltip))
                            
        except Exception:
            # If shape key enumeration fails, return basic items to prevent UI crash
            items.append(("ERROR", "Error loading shape keys", "Error accessing shape keys"))
        
        return items
    
    def add_target_object(self, target_obj):
        """Add a target object to the collection if not already present"""
        if not target_obj or target_obj.type != 'MESH':
            return False
        
        # Check if already in collection
        for item in self.shapekey_target_objects:
            if item.target_object == target_obj:
                return False
        
        # Add new target
        new_item = self.shapekey_target_objects.add()
        new_item.target_object = target_obj
        return True
    
    def remove_target_object(self, index):
        """Remove target object at given index"""
        if 0 <= index < len(self.shapekey_target_objects):
            self.shapekey_target_objects.remove(index)
            return True
        return False
    
    def clear_target_objects(self):
        """Clear all target objects"""
        self.shapekey_target_objects.clear()
    
    def get_target_objects_list(self):
        """Get list of actual target objects (not the PropertyGroup items)"""
        targets = []
        for item in self.shapekey_target_objects:
            if item.target_object:
                targets.append(item.target_object)
        return targets
    
    def update_shape_key_selections(self, context):
        """Update the shape key selection list based on source object"""
        self.shapekey_selected_keys.clear()
        
        source_obj = self.shapekey_source_object
        if not (source_obj and source_obj.type == 'MESH' and 
                hasattr(source_obj, 'data') and source_obj.data and
                hasattr(source_obj.data, 'shape_keys') and source_obj.data.shape_keys):
            return
        
        # Add all shape keys (except Basis) as selectable items
        for shape_key in source_obj.data.shape_keys.key_blocks:
            if shape_key.name and shape_key.name != "Basis":
                new_item = self.shapekey_selected_keys.add()
                new_item.name = shape_key.name
                new_item.selected = False
    
    def get_selected_shape_keys(self):
        """Get list of selected shape key names"""
        selected = []
        for item in self.shapekey_selected_keys:
            if item.selected:
                selected.append(item.name)
        return selected
    
    def select_all_shape_keys(self, select=True):
        """Select or deselect all shape keys"""
        for item in self.shapekey_selected_keys:
            item.selected = select
    
    def get_batch_transfer_summary(self):
        """Get summary of what will be transferred in batch mode"""
        targets = self.get_target_objects_list()
        shape_keys = self.get_selected_shape_keys()
        
        if not targets or not shape_keys:
            return "No targets or shape keys selected"
        
        total_operations = len(targets) * len(shape_keys)
        return f"{len(shape_keys)} shape key(s) → {len(targets)} target(s) = {total_operations} operations"


def _delayed_message_bus_setup():
    """Set up message bus subscription after Blender is fully loaded"""
    try:
        from .bone_transforms.operators.inherit_scale import update_inherit_scale_warning_from_context
        
        # Subscribe to bone property changes
        bpy.msgbus.subscribe_rna(
            key=(bpy.types.Bone, "inherit_scale"),
            owner=object(),  # Unique owner for this subscription
            args=(),
            notify=update_inherit_scale_warning_from_context,
        )
        print("Nyarc Tools: Successfully subscribed to inherit_scale property changes")
    except Exception as e:
        print(f"Nyarc Tools: Error setting up inherit_scale monitoring: {e}")
    
    # Return None to not repeat the timer
    return None


class VIEW3D_PT_nyarc_tools_manager(Panel):
    """Main panel for Nyarc VRCat Tools"""
    bl_label = "Nyarc VRCat Tools"
    bl_idname = "VIEW3D_PT_nyarc_tools_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nyarc VRCat Tools"
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='TOOL_SETTINGS')
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.nyarc_tools_props
        
        # Header info
        header_box = layout.box()
        header_row = header_box.row()
        header_row.label(text="Nyarc VRCat Tools v0.3.1", icon='TOOL_SETTINGS')
        header_row.label(text="🐱 Meow!")
        
        # Separator
        layout.separator()
        
        # Draw all module UIs using the modules system
        try:
            modules.draw_modules(layout, context)
        except Exception as e:
            error_box = layout.box()
            error_box.label(text="Error loading modules!", icon='ERROR')
            error_box.label(text=f"Details: {str(e)[:50]}")
        
        # Footer info
        layout.separator()
        footer_box = layout.box()
        footer_box.scale_y = 0.8
        footer_box.label(text="Add new tools by creating modules/", icon='INFO')
        footer_box.label(text="Each tool has its own collapsible section")


# Registration
classes = (
    ShapeKeyTargetItem,
    ShapeKeySelectionItem,
    NyarcToolsProperties,
    VIEW3D_PT_nyarc_tools_manager,
)


def register():
    # Register main classes first
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add main properties to scene
    bpy.types.Scene.nyarc_tools_props = PointerProperty(type=NyarcToolsProperties)
    
    # Register all modules
    try:
        modules.register_modules()
    except Exception as e:
        print(f"Nyarc Tools: Error registering modules: {e}")
    
    # Set up delayed initialization for message bus to avoid registration conflicts
    bpy.app.timers.register(_delayed_message_bus_setup, first_interval=1.0)


def unregister():
    # Clear timers
    try:
        if bpy.app.timers.is_registered(_delayed_message_bus_setup):
            bpy.app.timers.unregister(_delayed_message_bus_setup)
    except Exception as e:
        print(f"Nyarc Tools: Error clearing timer: {e}")
    
    # Clear message bus subscriptions
    try:
        bpy.msgbus.clear_by_owner(object())
        print("Nyarc Tools: Cleared message bus subscriptions")
    except Exception as e:
        print(f"Nyarc Tools: Error clearing message bus: {e}")
    
    # Unregister modules first
    try:
        modules.unregister_modules()
    except Exception as e:
        print(f"Nyarc Tools: Error unregistering modules: {e}")
    
    # Remove main properties
    try:
        del bpy.types.Scene.nyarc_tools_props
    except:
        pass
    
    # Unregister main classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass


if __name__ == "__main__":
    register()