# Armature Diff Export Module - CASCADING DIRECTION FIX VERSION  
# Contains the diff export logic extracted from bone_transform_saver.py
# 
# v0.8.3 - CASCADING DIRECTION MATHEMATICS FIX:
# - Fixed the direction error in child bone positioning (was moving up instead of down)
# - Transform11 proved the cascading logic works, but math direction was backwards
# - Child bones now move DOWN when parent bones shorten (correct direction)
# - Ankle/foot bones should finally position correctly relative to scaled legs

import bpy
import json
import os
from bpy.types import Operator
from bpy.props import StringProperty

# Import modularized calculations
try:
    from ..diff_export.armature_diff import (
        get_armature_transforms,
        calculate_head_tail_differences
    )
    from ..diff_export.transforms_diff import (
        convert_head_tail_to_pose_transforms_filtered
    )
    CALCULATIONS_AVAILABLE = True
except ImportError:
    CALCULATIONS_AVAILABLE = False
    print("Warning: armature_diff calculations not available for diff export")

class ARMATURE_OT_export_armature_diff(Operator):
    """Export transform differences between two armatures as a preset"""
    bl_idname = "armature.export_armature_diff"
    bl_label = "Export Armature Diff"
    bl_description = "Compare two armatures and export transform differences as a preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if not props:
            self.report({'ERROR'}, "Nyarc Tools properties not found")
            return {'CANCELLED'}
        
        # Validate inputs
        if not props.bone_diff_original_armature:
            self.report({'ERROR'}, "Please select the original/base armature")
            return {'CANCELLED'}
        
        if not props.bone_diff_modified_armature:
            self.report({'ERROR'}, "Please select the modified armature")
            return {'CANCELLED'}
        
        if not props.bone_diff_preset_name.strip():
            self.report({'ERROR'}, "Please enter a preset name")
            return {'CANCELLED'}
        
        if props.bone_diff_original_armature == props.bone_diff_modified_armature:
            self.report({'ERROR'}, "Original and modified armatures must be different objects")
            return {'CANCELLED'}
        
        if not CALCULATIONS_AVAILABLE:
            self.report({'ERROR'}, "Bone transform calculations module not available")
            return {'CANCELLED'}
        
        original_armature = props.bone_diff_original_armature
        modified_armature = props.bone_diff_modified_armature
        preset_name = props.bone_diff_preset_name.strip()
        
        # Automatically add _diff suffix to distinguish from regular presets
        if not preset_name.endswith('_diff'):
            preset_name = preset_name + '_diff'
        
        try:
            # Store current state to restore later
            original_active = context.view_layer.objects.active
            original_selected = context.selected_objects[:]
            original_mode = context.mode
            
            # Switch to object mode first
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Get bone transforms from both armatures
            original_transforms = get_armature_transforms(original_armature)
            modified_transforms = get_armature_transforms(modified_armature)
            
            if not original_transforms:
                self.report({'ERROR'}, f"Could not read transforms from original armature '{original_armature.name}'")
                return {'CANCELLED'}
            
            if not modified_transforms:
                self.report({'ERROR'}, f"Could not read transforms from modified armature '{modified_armature.name}'")
                return {'CANCELLED'}
            
            # Find meshes associated with each armature for XYZ scaling analysis
            def find_meshes_for_armature(armature):
                """Find all mesh objects that have this armature as their armature modifier target"""
                associated_meshes = []
                for obj in bpy.data.objects:
                    if obj.type == 'MESH':
                        for modifier in obj.modifiers:
                            if modifier.type == 'ARMATURE' and modifier.object == armature:
                                associated_meshes.append(obj)
                                break
                return associated_meshes
            
            original_meshes = find_meshes_for_armature(original_armature)
            modified_meshes = find_meshes_for_armature(modified_armature)
            
            print(f"MESH ANALYSIS: Found {len(original_meshes)} original meshes, {len(modified_meshes)} modified meshes")
            for mesh in original_meshes:
                print(f"  Original mesh: {mesh.name}")
            for mesh in modified_meshes:
                print(f"  Modified mesh: {mesh.name}")
            
            # Calculate differences using pose transform method with mesh analysis for accurate XYZ scaling
            diff_data = convert_head_tail_to_pose_transforms_filtered(
                original_transforms, 
                modified_transforms, 
                original_meshes, 
                modified_meshes
            )
            bones_with_differences = len(diff_data)
            
            if bones_with_differences == 0:
                self.report({'WARNING'}, "No transform differences found between the two armatures")
                return {'CANCELLED'}
            
            # Create preset data structure in standard format
            preset_data = {
                'name': preset_name,
                'source_armature': f"{original_armature.name} -> {modified_armature.name}",
                'bone_count': bones_with_differences,
                'bones': diff_data,
                'created_date': bpy.context.scene.frame_current,
                'diff_export': True,  # Mark as diff export for metadata
                'original_armature': original_armature.name,
                'modified_armature': modified_armature.name,
                'description': 'Bone differences converted to standard pose transforms (compatible with all loaders)'
            }
            
            # Save to file
            presets_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'nyarc_tools_presets')
            os.makedirs(presets_dir, exist_ok=True)
            
            preset_file = os.path.join(presets_dir, f"{preset_name}.json")
            
            with open(preset_file, 'w') as f:
                json.dump(preset_data, f, indent=2)
            
            self.report({'INFO'}, f"Exported diff preset '{preset_name}': {bones_with_differences} bones with differences (auto-added _diff suffix)")
            self.report({'INFO'}, f"Transform direction: {original_armature.name} (original) → {modified_armature.name} (modified)")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export armature diff: {str(e)}")
            return {'CANCELLED'}
        
        finally:
            # Restore original state
            try:
                if context.mode != original_mode:
                    if original_mode == 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    elif original_mode == 'POSE':
                        bpy.ops.object.mode_set(mode='POSE')
                
                # Restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in original_selected:
                    obj.select_set(True)
                context.view_layer.objects.active = original_active
            except:
                pass