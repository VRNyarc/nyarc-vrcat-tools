# Bone Transforms UI Module
# User interface components for bone transformation tools

from ...core.registry import try_import_module

# Try to import UI modules with graceful fallbacks
panels_module, PANELS_AVAILABLE = try_import_module('nyarc_vrcat_tools.bone_transforms.ui.panels', 'bone_transforms.ui.panels')

# Re-export commonly used functions if available
if PANELS_AVAILABLE:
    try:
        from nyarc_vrcat_tools.bone_transforms.ui.panels import draw_ui
    except ImportError:
        pass

UI_CLASSES = []