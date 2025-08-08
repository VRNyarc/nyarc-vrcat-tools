# Shape Key Synchronization System
# Live preview and value synchronization

from .sync_ops import *

def get_classes():
    """Get all sync classes for registration"""
    from .sync_ops import get_classes as sync_classes
    
    classes = []
    classes.extend(sync_classes())
    return classes