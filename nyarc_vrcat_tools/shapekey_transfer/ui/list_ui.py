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
            
            # Check if shape key exists on any target mesh
            shape_key_exists = self._check_shape_key_exists_on_targets(context, item.name)
            
            # Use red text if shape key doesn't exist on targets
            if shape_key_exists:
                row.label(text=item.name, icon='SHAPEKEY_DATA')
            else:
                # Red text for non-transferred shape keys
                red_row = row.row()
                red_row.alert = True  # Makes text red
                red_row.label(text=item.name, icon='SHAPEKEY_DATA')
                
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "selected", text="", emboss=False)
    
    def _check_shape_key_exists_on_targets(self, context, shape_key_name):
        """Check if shape key exists on any target mesh"""
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            return False
        
        # Get all target objects
        target_objects = []
        if props.shapekey_target_object:
            target_objects.append(props.shapekey_target_object)
        target_objects.extend(props.get_target_objects_list())
        
        # Check if shape key exists on any target
        for target_obj in target_objects:
            if (target_obj and target_obj.data.shape_keys and 
                target_obj.data.shape_keys.key_blocks and
                shape_key_name in target_obj.data.shape_keys.key_blocks):
                return True
        
        return False


def get_classes():
    """Get all list UI classes for registration"""
    return [
        SHAPEKEY_UL_selection_list,
    ]