# Shape Key Transfer Module
# Modular implementation for shape key transfer functionality
#
# NOTE: Hot reload is handled by main __init__.py via sys.modules cleanup
# No manual reload code needed here!

# Import all submodule components
import bpy
from . import operators
from . import ui
from . import utils
from . import sync

# Main UI entry point (called from modules.py)
def draw_ui(layout, context):
    """Draw the Shape Key Transfer UI content (called from modules.py)"""
    from .ui.main_panel import draw_ui as draw_main_ui
    return draw_main_ui(layout, context)

# Module registration
def get_classes():
    """Get all classes for registration"""
    classes = []
    
    # Add all operator classes
    classes.extend(operators.get_classes())
    
    # Add all UI classes  
    classes.extend(ui.get_classes())
    
    # Add all utility classes
    classes.extend(utils.get_classes())
    
    # Add all sync classes
    classes.extend(sync.get_classes())
    
    return classes

def register():
    """Register all module classes and handlers"""
    import bpy
    for cls in get_classes():
        bpy.utils.register_class(cls)
    
    # Register sync handlers
    from .sync.sync_ops import register_handlers
    register_handlers()

def unregister():
    """Unregister all module classes and handlers"""
    import bpy
    
    # Unregister sync handlers first
    from .sync.sync_ops import unregister_handlers
    unregister_handlers()
    
    for cls in reversed(get_classes()):
        bpy.utils.unregister_class(cls)