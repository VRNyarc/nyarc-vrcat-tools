# Shape Key Transfer Operators
# All operator classes for shape key transfer functionality

from .transfer_ops import *
from .target_ops import *
from .management_ops import *
from .robust_transfer_ops import *

def get_classes():
    """Get all operator classes for registration"""
    from .transfer_ops import get_classes as transfer_classes
    from .target_ops import get_classes as target_classes
    from .management_ops import get_classes as management_classes
    from .robust_transfer_ops import classes as robust_classes
    
    classes = []
    classes.extend(transfer_classes())
    classes.extend(target_classes())
    classes.extend(management_classes())
    classes.extend(robust_classes)  # Robust operators
    return classes
