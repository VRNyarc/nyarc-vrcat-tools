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
            
            # Check detailed status of shape key on targets
            shape_key_status = self._get_shape_key_status_on_targets(context, item.name)
            
            # Visual indicators based on target status
            if shape_key_status == "all":
                # Normal white text - all targets have it
                row.label(text=item.name, icon='SHAPEKEY_DATA')
            elif shape_key_status == "some":
                # Try different sequence colors to find yellow
                partial_row = row.row()
                # Test sequence colors - SEQUENCE_COLOR_05 was blue, try others
                # partial_row.label(text=item.name, icon='INFO')        # Yellow triangle with !
                # partial_row.label(text=item.name, icon='SEQUENCE_COLOR_01')  # Try color 1
                partial_row.label(text=item.name, icon='SEQUENCE_COLOR_02')  # Try color 2 (might be yellow)
                # partial_row.label(text=item.name, icon='SEQUENCE_COLOR_04')  # Try color 4
            else:  # "none"
                # Red text - no targets have it  
                red_row = row.row()
                red_row.alert = True
                red_row.label(text=item.name, icon='SHAPEKEY_DATA')
                
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "selected", text="", emboss=False)
    
    def _get_shape_key_status_on_targets(self, context, shape_key_name):
        """Get detailed status of shape key across all target meshes
        
        Returns:
            "all" - All target meshes have this shape key
            "some" - Some target meshes have it, others don't  
            "none" - No target meshes have this shape key
        """
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            return "none"
        
        # Get all target objects
        target_objects = []
        if props.shapekey_target_object:
            target_objects.append(props.shapekey_target_object)
        target_objects.extend(props.get_target_objects_list())
        
        if not target_objects:
            return "none"
        
        # Count how many targets have the shape key
        targets_with_key = 0
        for target_obj in target_objects:
            if (target_obj and target_obj.data.shape_keys and 
                target_obj.data.shape_keys.key_blocks and
                shape_key_name in target_obj.data.shape_keys.key_blocks):
                targets_with_key += 1
        
        total_targets = len(target_objects)
        
        if targets_with_key == 0:
            return "none"
        elif targets_with_key == total_targets:
            return "all"
        else:
            return "some"


def get_classes():
    """Get all list UI classes for registration"""
    return [
        SHAPEKEY_UL_selection_list,
    ]