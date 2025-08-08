# Shape Key List UI Components
# Scrollable list and selection UI

import bpy
from bpy.types import UIList


class SHAPEKEY_UL_selection_list(UIList):
    """UI List for scrollable shape key selection"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        """Draw individual shape key item in the list"""
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Show checkbox for selection and shape key name
            row = layout.row(align=True)
            row.prop(item, "selected", text="")
            row.label(text=item.name, icon='SHAPEKEY_DATA')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "selected", text="", emboss=False)


def get_classes():
    """Get all list UI classes for registration"""
    return [
        SHAPEKEY_UL_selection_list,
    ]