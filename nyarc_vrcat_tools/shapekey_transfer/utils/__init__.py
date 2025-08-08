# Shape Key Transfer Utils
# Core utility functions and validation

from .mesh_utils import *
from .validation import *

def get_classes():
    """Get all utility classes for registration"""
    from .mesh_utils import get_classes as mesh_classes
    from .validation import get_classes as validation_classes
    
    classes = []
    classes.extend(mesh_classes())
    classes.extend(validation_classes())
    return classes