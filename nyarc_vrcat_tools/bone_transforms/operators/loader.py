"""
Bone Transform Loading Operations
Handles the complex process of loading saved bone transforms back to armatures
"""

import bpy
from mathutils import Vector, Quaternion, Matrix

# Import precision correction module with fallback
try:
    from ..precision import (
        apply_precision_corrections,
        preset_has_precision_data,
        is_diff_export_preset,
        PRECISION_AVAILABLE
    )
except ImportError:
    PRECISION_AVAILABLE = False
    print("Warning: Precision correction module not available")
    
    # Fallback functions
    def preset_has_precision_data(preset_data):
        """Fallback - check if preset has precision data"""
        if not preset_data or 'bones' not in preset_data:
            return False
        for bone_name, bone_data in preset_data['bones'].items():
            if isinstance(bone_data, dict) and 'precision_data' in bone_data:
                return True
        return False
    
    def is_diff_export_preset(preset_data):
        """Fallback - check if preset is diff export"""
        return preset_data.get('diff_export', False) or preset_has_precision_data(preset_data)
    
    def apply_precision_corrections(context, armature, preset_data):
        """Fallback - precision correction not available"""
        print("Warning: Precision correction requested but module not available")
        return False

# Import bone mapper with fallback handling
try:
    from ..io.bone_mapper import map_bone_transforms
    BONE_MAPPER_AVAILABLE = True
except ImportError:
    BONE_MAPPER_AVAILABLE = False
    print("Warning: bone_mapper not available, using exact matching only")

# Import inheritance flattening utilities (HARD DEPENDENCY)
from ..utils.inheritance_flattening import (
    prepare_bones_for_flattened_load,
    restore_original_inherit_scales
)

def load_bone_transforms_internal(context, armature, preset_data, operator_self):
    """Internal function to load bone transforms - shared by both operators"""
    try:
        # Ensure we're in pose mode with the target armature
        if context.mode != 'POSE' or context.object != armature:
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
        
        # Set armature to POSE position to show current transforms visually
        armature.data.pose_position = 'POSE'
        
        # Set bone editing as active so UI reflects pose mode state
        props = getattr(context.scene, 'nyarc_tools_props', None)
        if props:
            props.bone_editing_active = True
        
        # FLATTENED LOADING: Prepare bones for consistent inheritance context
        target_bones = set(preset_data['bones'].keys())
        original_inherit_scales = {}
        
        # ALWAYS use flattening context for mathematical consistency
        is_flattened_preset = preset_data.get('flattened', False)
        
        if not is_flattened_preset:
            operator_self.report({'WARNING'}, "Loading legacy preset - applying flattening context for inheritance consistency")
            print(f"Preset Load: Legacy preset detected, applying flattening context")
        
        # Prepare bones for flattened loading (set inherit_scale=NONE)
        original_inherit_scales = prepare_bones_for_flattened_load(armature, target_bones)
        print(f"Preset Load: Prepared {len(target_bones)} bones for flattened loading")
        
        # Apply bone transforms using hybrid matching
        armature_bone_names = [bone.name for bone in armature.pose.bones]
        
        if BONE_MAPPER_AVAILABLE:
            # Use intelligent bone mapping
            exact_matches, semantic_matches, unmatched_bones, summary = map_bone_transforms(
                preset_data['bones'], armature_bone_names
            )
            print(f"Bone Mapper: {summary}")
            
            # Quick debug report to user
            operator_self.report({'INFO'}, f"DEBUG: Found {len(semantic_matches)} semantic matches - check console for details")
            
            # Apply exact matches (with identity transform filtering)
            bones_applied = 0
            for preset_bone, armature_bone in exact_matches.items():
                if armature_bone in armature.pose.bones:
                    transform_data = preset_data['bones'][preset_bone]
                    
                    # Apply standard pose transform method (all presets now use this format)
                    if all(key in transform_data for key in ['location', 'rotation_quaternion', 'scale']):
                        # FILTER OUT IDENTITY TRANSFORMS (no actual changes)
                        location = transform_data['location']
                        rotation = transform_data['rotation_quaternion'] 
                        scale = transform_data['scale']
                        
                        # Check if this is essentially an identity transform
                        is_identity = (
                            abs(location[0]) < 0.0001 and abs(location[1]) < 0.0001 and abs(location[2]) < 0.0001 and
                            abs(rotation[0] - 1.0) < 0.0001 and abs(rotation[1]) < 0.0001 and abs(rotation[2]) < 0.0001 and abs(rotation[3]) < 0.0001 and
                            abs(scale[0] - 1.0) < 0.0001 and abs(scale[1] - 1.0) < 0.0001 and abs(scale[2] - 1.0) < 0.0001
                        )
                        
                        if is_identity:
                            print(f"DEBUG: Skipping identity transform for bone '{preset_bone}' -> '{armature_bone}' (no actual changes)")
                            continue  # Skip applying identity transforms
                        
                        pose_bone = armature.pose.bones[armature_bone]
                        pose_bone.location = Vector(location)
                        pose_bone.rotation_quaternion = Quaternion(rotation)
                        pose_bone.scale = Vector(scale)
                        bones_applied += 1
                        print(f"DEBUG: Applied non-identity transform to '{armature_bone}': loc={location}, rot={rotation}, scale={scale}")
                    else:
                        print(f"WARNING: Bone '{preset_bone}' missing pose transform keys, skipping")
            
            # Apply semantic matches (with identity transform filtering)
            semantic_applied = 0
            for preset_bone, armature_bone in semantic_matches.items():
                print(f"DEBUG: Trying to apply semantic transform: '{preset_bone}' -> '{armature_bone}'")
                if armature_bone in armature.pose.bones:
                    transform_data = preset_data['bones'][preset_bone]
                    
                    # Apply standard pose transform method (all presets now use this format)
                    if all(key in transform_data for key in ['location', 'rotation_quaternion', 'scale']):
                        # FILTER OUT IDENTITY TRANSFORMS (no actual changes)
                        location = transform_data['location']
                        rotation = transform_data['rotation_quaternion'] 
                        scale = transform_data['scale']
                        
                        # Check if this is essentially an identity transform
                        is_identity = (
                            abs(location[0]) < 0.0001 and abs(location[1]) < 0.0001 and abs(location[2]) < 0.0001 and
                            abs(rotation[0] - 1.0) < 0.0001 and abs(rotation[1]) < 0.0001 and abs(rotation[2]) < 0.0001 and abs(rotation[3]) < 0.0001 and
                            abs(scale[0] - 1.0) < 0.0001 and abs(scale[1] - 1.0) < 0.0001 and abs(scale[2] - 1.0) < 0.0001
                        )
                        
                        if is_identity:
                            print(f"DEBUG: Skipping identity transform for semantic bone '{preset_bone}' -> '{armature_bone}' (no actual changes)")
                            continue  # Skip applying identity transforms
                        
                        pose_bone = armature.pose.bones[armature_bone]
                        pose_bone.location = Vector(location)
                        pose_bone.rotation_quaternion = Quaternion(rotation)
                        pose_bone.scale = Vector(scale)
                        semantic_applied += 1
                        print(f"Semantic POSE mapping APPLIED: '{preset_bone}' -> '{armature_bone}'")
                    else:
                        print(f"WARNING: Bone '{preset_bone}' missing pose transform keys, skipping")
                else:
                    print(f"DEBUG: ERROR - Armature bone '{armature_bone}' not found in pose bones!")
            
            bones_missing = unmatched_bones
            total_applied = bones_applied + semantic_applied
            
        else:
            # Fallback to exact matching only
            bones_applied = 0
            bones_missing = []
            total_applied = 0
            
            for bone_name, transform_data in preset_data['bones'].items():
                if bone_name in armature.pose.bones:
                    # Apply standard pose transform method (with identity filtering)
                    if all(key in transform_data for key in ['location', 'rotation_quaternion', 'scale']):
                        # FILTER OUT IDENTITY TRANSFORMS (no actual changes)
                        location = transform_data['location']
                        rotation = transform_data['rotation_quaternion'] 
                        scale = transform_data['scale']
                        
                        # Check if this is essentially an identity transform
                        is_identity = (
                            abs(location[0]) < 0.0001 and abs(location[1]) < 0.0001 and abs(location[2]) < 0.0001 and
                            abs(rotation[0] - 1.0) < 0.0001 and abs(rotation[1]) < 0.0001 and abs(rotation[2]) < 0.0001 and abs(rotation[3]) < 0.0001 and
                            abs(scale[0] - 1.0) < 0.0001 and abs(scale[1] - 1.0) < 0.0001 and abs(scale[2] - 1.0) < 0.0001
                        )
                        
                        if is_identity:
                            print(f"DEBUG: Skipping identity transform for bone '{bone_name}' (no actual changes)")
                            continue  # Skip applying identity transforms
                        
                        pose_bone = armature.pose.bones[bone_name]
                        pose_bone.location = Vector(location)
                        pose_bone.rotation_quaternion = Quaternion(rotation)
                        pose_bone.scale = Vector(scale)
                        bones_applied += 1
                        print(f"DEBUG: Applied non-identity transform to '{bone_name}': loc={location}, rot={rotation}, scale={scale}")
                    else:
                        print(f"WARNING: Bone '{bone_name}' missing pose transform keys, skipping")
                        bones_missing.append(bone_name)
                else:
                    bones_missing.append(bone_name)
            
            total_applied = bones_applied
        
        # Apply inherit_scale settings if present in preset
        inherit_scale_applied = 0
        if any('inherit_scale' in bone_data for bone_data in preset_data['bones'].values()):
            print("Applying inherit_scale settings from preset")
            
            # Switch to edit mode to set inherit_scale
            original_mode = context.mode
            if context.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            
            if BONE_MAPPER_AVAILABLE:
                # Use the same bone mapping as transforms (exact + semantic matches)
                
                # Apply inherit_scale for exact matches
                for preset_bone, armature_bone in exact_matches.items():
                    if (armature_bone in armature.data.edit_bones and 
                        preset_bone in preset_data['bones'] and 
                        'inherit_scale' in preset_data['bones'][preset_bone]):
                        edit_bone = armature.data.edit_bones[armature_bone]
                        edit_bone.inherit_scale = preset_data['bones'][preset_bone]['inherit_scale']
                        inherit_scale_applied += 1
                        print(f"Applied inherit_scale (exact): '{preset_bone}' -> '{armature_bone}' = {preset_data['bones'][preset_bone]['inherit_scale']}")
                
                # Apply inherit_scale for semantic matches
                for preset_bone, armature_bone in semantic_matches.items():
                    if (armature_bone in armature.data.edit_bones and 
                        preset_bone in preset_data['bones'] and 
                        'inherit_scale' in preset_data['bones'][preset_bone]):
                        edit_bone = armature.data.edit_bones[armature_bone]
                        edit_bone.inherit_scale = preset_data['bones'][preset_bone]['inherit_scale']
                        inherit_scale_applied += 1
                        print(f"Applied inherit_scale (semantic): '{preset_bone}' -> '{armature_bone}' = {preset_data['bones'][preset_bone]['inherit_scale']}")
                        
            else:
                # Fallback to exact matching only
                for bone_name, transform_data in preset_data['bones'].items():
                    if bone_name in armature.data.edit_bones and 'inherit_scale' in transform_data:
                        edit_bone = armature.data.edit_bones[bone_name]
                        edit_bone.inherit_scale = transform_data['inherit_scale']
                        inherit_scale_applied += 1
            
            # Switch back to original mode
            if original_mode == 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            elif original_mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
                
            print(f"Applied inherit_scale to {inherit_scale_applied} bones")
        
        # Update the scene to ensure pose changes are reflected
        context.view_layer.update()
        bpy.context.view_layer.depsgraph.update()
        
        # Track if precision correction was applied for contextual messaging
        precision_correction_applied = False
        
        # Apply precision correction ONLY for diff export presets when checkbox is enabled
        # Normal presets use standard loader even when checkbox is checked
        if (props.apply_precision_correction and 
            is_diff_export_preset(preset_data) and 
            preset_has_precision_data(preset_data)):
            try:
                print("DEBUG: Using precision correction for amateur diff export preset")
                precision_applied = apply_precision_corrections(context, armature, preset_data)
                if precision_applied:
                    precision_correction_applied = True
                    operator_self.report({'INFO'}, "Applied precision correction for enhanced accuracy")
                    
                    # For diff exports, automatically apply as rest pose so edit mode coordinates match
                    if preset_data.get('diff_export', False):
                        try:
                            # Use proper Blender operator call
                            result = bpy.ops.armature.apply_as_rest_pose()
                            
                            if result == {'FINISHED'}:
                                operator_self.report({'INFO'}, "Automatically applied precision corrections as rest pose for diff export")
                            else:
                                operator_self.report({'WARNING'}, "Precision correction applied but failed to apply as rest pose")
                        except Exception as rest_error:
                            operator_self.report({'WARNING'}, f"Precision correction applied but failed to apply as rest pose: {str(rest_error)}")
                else:
                    operator_self.report({'WARNING'}, "Precision correction attempted but no improvements detected")
            except Exception as e:
                operator_self.report({'WARNING'}, f"Precision correction failed: {str(e)}")
        elif props.apply_precision_correction and not is_diff_export_preset(preset_data):
            print("DEBUG: Skipping precision correction for standard preset (not amateur diff export)")
            operator_self.report({'INFO'}, "Standard preset loaded normally (precision correction only applies to amateur diff exports)")
        
        # Report results with intelligent mapping info
        preset_name = preset_data.get('name', 'Unknown')
        if bones_missing:
            if BONE_MAPPER_AVAILABLE and 'semantic_applied' in locals() and semantic_applied > 0:
                # Show detailed breakdown when using semantic mapping
                if inherit_scale_applied > 0:
                    operator_self.report({'WARNING'}, f"Applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total, inherit_scale to {inherit_scale_applied} bones, {len(bones_missing)} bones not found: {', '.join(bones_missing[:5])}")
                else:
                    operator_self.report({'WARNING'}, f"Applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total, {len(bones_missing)} bones not found: {', '.join(bones_missing[:5])}")
            else:
                # Standard message for exact matching only
                if inherit_scale_applied > 0:
                    operator_self.report({'WARNING'}, f"Applied transforms to {total_applied} bones and inherit_scale to {inherit_scale_applied} bones, {len(bones_missing)} bones not found: {', '.join(bones_missing[:5])}")
                else:
                    operator_self.report({'WARNING'}, f"Applied transforms to {total_applied} bones, {len(bones_missing)} bones not found: {', '.join(bones_missing[:5])}")
        else:
            # Success message - contextually appropriate based on precision correction
            if BONE_MAPPER_AVAILABLE and 'semantic_applied' in locals() and semantic_applied > 0:
                if inherit_scale_applied > 0:
                    if precision_correction_applied:
                        operator_self.report({'INFO'}, f"Successfully applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total and inherit_scale to {inherit_scale_applied} bones from preset '{preset_name}'. Precision correction completed - mesh deformation finalized.")
                    else:
                        operator_self.report({'INFO'}, f"Successfully applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total and inherit_scale to {inherit_scale_applied} bones from preset '{preset_name}'. Use 'Apply as Rest Pose' to make permanent.")
                else:
                    if precision_correction_applied:
                        operator_self.report({'INFO'}, f"Successfully applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total from preset '{preset_name}'. Precision correction completed - mesh deformation finalized.")
                    else:
                        operator_self.report({'INFO'}, f"Successfully applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total from preset '{preset_name}'. Use 'Apply as Rest Pose' to make permanent.")
            else:
                if inherit_scale_applied > 0:
                    if precision_correction_applied:
                        operator_self.report({'INFO'}, f"Successfully applied transforms and inherit_scale to {total_applied} bones from preset '{preset_name}'. Precision correction completed - mesh deformation finalized.")
                    else:
                        operator_self.report({'INFO'}, f"Successfully applied transforms and inherit_scale to {total_applied} bones from preset '{preset_name}'. Use 'Apply as Rest Pose' to make the mesh deformation permanent.")
                else:
                    if precision_correction_applied:
                        operator_self.report({'INFO'}, f"Successfully applied transforms to {total_applied} bones from preset '{preset_name}'. Precision correction completed - mesh deformation finalized.")
                    else:
                        operator_self.report({'INFO'}, f"Successfully applied transforms to {total_applied} bones from preset '{preset_name}'. Use 'Apply as Rest Pose' to make the mesh deformation permanent.")
        
        # DON'T restore inherit_scale settings for preset loading - we want to keep inherit_scale=NONE
        # for proper flattened inheritance behavior. This ensures child bones get the correct
        # flattened scaling instead of reverting to original inherit_scale settings.
        print(f"Preset Load: Keeping inherit_scale=NONE for {len(original_inherit_scales)} bones (flattened inheritance)")
        
        return {'FINISHED'}
        
    except Exception as e:
        operator_self.report({'ERROR'}, f"Failed to load bone transforms: {str(e)}")
        return {'CANCELLED'}