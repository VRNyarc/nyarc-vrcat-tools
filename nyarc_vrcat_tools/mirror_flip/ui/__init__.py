# Mirror Flip UI
from .panels import *

# Registration
def register():
    from .panels import register as register_panels
    register_panels()

def unregister():
    from .panels import unregister as unregister_panels
    unregister_panels()