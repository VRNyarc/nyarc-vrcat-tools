# Mirror Flip Module
# One-click solution to flip accessories and bones from one side to the other

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty

# Import submodules
from . import operators, ui, utils

def _get_direction_items(self, context):
    """Get direction items based on selected mirror axis"""
    axis = getattr(self, 'mirror_axis', 'X')
    
    if axis == 'X':
        return [
            ('LEFT_TO_RIGHT', "Left → Right", "Flip from left side to right side"),
            ('RIGHT_TO_LEFT', "Right → Left", "Flip from right side to left side")
        ]
    elif axis == 'Y':
        return [
            ('FRONT_TO_BACK', "Front → Back", "Flip from front side to back side"),
            ('BACK_TO_FRONT', "Back → Front", "Flip from back side to front side")
        ]
    elif axis == 'Z':
        return [
            ('UP_TO_DOWN', "Up → Down", "Flip from up side to down side"),
            ('DOWN_TO_UP', "Down → Up", "Flip from down side to up side")
        ]
    else:
        # Fallback
        return [
            ('POSITIVE', "Positive → Negative", "Flip to negative side of axis"),
            ('NEGATIVE', "Negative → Positive", "Flip to positive side of axis")
        ]

# Module information for dynamic registration
MODULE_INFO = {
    'name': 'mirror_flip',
    'version': '1.0.0',
    'dependencies': ['core'],
    'operators': [
        'OBJECT_OT_flip_mesh',
        'ARMATURE_OT_flip_bones', 
        'OBJECT_OT_flip_mesh_and_bones_combined'
    ],
    'ui_panels': [
        'VIEW3D_PT_mirror_flip_tools'
    ],
    'property_groups': [
        'MirrorFlipProperties'
    ]
}

class MirrorFlipProperties(PropertyGroup):
    """Properties for mirror flip operations"""
    
    # Auto-detection options
    auto_detect_bones: BoolProperty(
        name="Auto-detect Bones",
        description="Automatically detect bones associated with selected meshes",
        default=True
    )
    
    # Transform options
    apply_transforms: BoolProperty(
        name="Apply Transforms", 
        description="Apply location, rotation, and scale after mirroring",
        default=True
    )
    
    # Naming options
    auto_rename: BoolProperty(
        name="Auto-rename (.L → .R)",
        description="Automatically rename bones and objects using .L/.R convention",
        default=True
    )
    
    # Selection options
    keep_original_selected: BoolProperty(
        name="Keep Original Selected",
        description="Keep the original objects selected after flipping",
        default=False
    )
    
    # Mirror axis
    mirror_axis: EnumProperty(
        name="Mirror Axis",
        description="Axis to mirror across",
        items=[
            ('X', "X-Axis (Left ↔ Right)", "Mirror across X-axis"),
            ('Y', "Y-Axis (Front ↔ Back)", "Mirror across Y-axis"),
            ('Z', "Z-Axis (Up ↔ Down)", "Mirror across Z-axis")
        ],
        default='X'
    )
    
    # Manual mode toggle
    manual_mode: BoolProperty(
        name="Manual Mode",
        description="Override automatic axis and direction detection",
        default=False
    )
    
    # Manual direction (only shown in manual mode)
    manual_direction: EnumProperty(
        name="Manual Direction", 
        description="Manually specify flip direction",
        items=lambda self, context: _get_direction_items(self, context),
        default=0
    )

# Registration functions
def register_module():
    """Register all module components"""
    print("Registering mirror_flip module...")
    
    # Register property group
    bpy.utils.register_class(MirrorFlipProperties)
    
    # Add properties to scene
    if not hasattr(bpy.types.Scene, 'mirror_flip_props'):
        bpy.types.Scene.mirror_flip_props = bpy.props.PointerProperty(type=MirrorFlipProperties)
    
    # Register submodules
    operators.register()
    # NOTE: UI panels disabled - integrated into main modules.py UI
    # ui.register()
    
    print("Mirror flip module registered successfully")

def unregister_module():
    """Unregister all module components"""
    print("Unregistering mirror_flip module...")
    
    # Unregister submodules
    # NOTE: UI panels disabled - integrated into main modules.py UI  
    # ui.unregister()
    operators.unregister()
    
    # Remove properties from scene
    if hasattr(bpy.types.Scene, 'mirror_flip_props'):
        del bpy.types.Scene.mirror_flip_props
    
    # Unregister property group
    bpy.utils.unregister_class(MirrorFlipProperties)
    
    print("Mirror flip module unregistered successfully")

# Keep compatibility with direct import
classes = (
    MirrorFlipProperties,
)

def register():
    register_module()

def unregister():
    unregister_module()