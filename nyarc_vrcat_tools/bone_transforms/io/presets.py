# Bone Transform Loader Module
# Contains the complex bone transform loading logic

import bpy
from mathutils import Vector, Quaternion

# Import modularized calculations
try:
    from .bone_transform_calculations import apply_head_tail_transform_with_mesh_deformation
    CALCULATIONS_AVAILABLE = True
except ImportError:
    CALCULATIONS_AVAILABLE = False
    print("Warning: bone_transform_calculations not available for loader")

# Import bone name mapper
try:
    from .bone_name_mapper import map_bone_transforms
    BONE_MAPPER_AVAILABLE = True
except ImportError:
    BONE_MAPPER_AVAILABLE = False
    print("Warning: bone_name_mapper not available for loader")

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
            
            # Apply exact matches
            bones_applied = 0
            for preset_bone, armature_bone in exact_matches.items():
                if armature_bone in armature.pose.bones:
                    transform_data = preset_data['bones'][preset_bone]
                    
                    # Apply standard pose transform method (all presets now use this format)
                    if all(key in transform_data for key in ['location', 'rotation_quaternion', 'scale']):
                        pose_bone = armature.pose.bones[armature_bone]
                        pose_bone.location = Vector(transform_data['location'])
                        pose_bone.rotation_quaternion = Quaternion(transform_data['rotation_quaternion'])
                        pose_bone.scale = Vector(transform_data['scale'])
                        bones_applied += 1
                    else:
                        print(f"WARNING: Bone '{preset_bone}' missing pose transform keys, skipping")
            
            # Apply semantic matches
            semantic_applied = 0
            for preset_bone, armature_bone in semantic_matches.items():
                print(f"DEBUG: Trying to apply semantic transform: '{preset_bone}' -> '{armature_bone}'")
                if armature_bone in armature.pose.bones:
                    transform_data = preset_data['bones'][preset_bone]
                    
                    # Apply standard pose transform method (all presets now use this format)
                    if all(key in transform_data for key in ['location', 'rotation_quaternion', 'scale']):
                        pose_bone = armature.pose.bones[armature_bone]
                        print(f"DEBUG: Applying POSE transform to bone '{armature_bone}': loc={transform_data['location']}, rot={transform_data['rotation_quaternion']}, scale={transform_data['scale']}")
                        
                        pose_bone.location = Vector(transform_data['location'])
                        pose_bone.rotation_quaternion = Quaternion(transform_data['rotation_quaternion'])
                        pose_bone.scale = Vector(transform_data['scale'])
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
                    pose_bone = armature.pose.bones[bone_name]
                    
                    # Apply transforms
                    pose_bone.location = Vector(transform_data['location'])
                    pose_bone.rotation_quaternion = Quaternion(transform_data['rotation_quaternion'])
                    pose_bone.scale = Vector(transform_data['scale'])
                    
                    bones_applied += 1
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
            # Success message
            if BONE_MAPPER_AVAILABLE and 'semantic_applied' in locals() and semantic_applied > 0:
                if inherit_scale_applied > 0:
                    operator_self.report({'INFO'}, f"Successfully applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total and inherit_scale to {inherit_scale_applied} bones from preset '{preset_name}'. Use 'Apply as Rest Pose' to make permanent.")
                else:
                    operator_self.report({'INFO'}, f"Successfully applied transforms: {bones_applied} exact + {semantic_applied} semantic = {total_applied} total from preset '{preset_name}'. Use 'Apply as Rest Pose' to make permanent.")
            else:
                if inherit_scale_applied > 0:
                    operator_self.report({'INFO'}, f"Successfully applied transforms and inherit_scale to {total_applied} bones from preset '{preset_name}'. Use 'Apply as Rest Pose' to make the mesh deformation permanent.")
                else:
                    operator_self.report({'INFO'}, f"Successfully applied transforms to {total_applied} bones from preset '{preset_name}'. Use 'Apply as Rest Pose' to make the mesh deformation permanent.")
        
        return {'FINISHED'}
        
    except Exception as e:
        operator_self.report({'ERROR'}, f"Failed to load bone transforms: {str(e)}")
        return {'CANCELLED'}