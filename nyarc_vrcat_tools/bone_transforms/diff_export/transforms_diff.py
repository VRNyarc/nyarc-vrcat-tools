# Bone Transform Calculations Module
# Contains the complex calculation logic extracted from bone_transform_saver.py
# This modularizes the 1000+ line file and separates concerns

import bpy
import json
import os
from mathutils import Vector, Quaternion, Matrix
import bmesh

def should_skip_xz_scaling_analysis(bone_name):
    """
    Determine if X/Z scaling analysis should be skipped for this bone.
    Temporary solution for coordinate space scaling issues.
    
    Based on research: certain bones (neck, head, spine) have coordinate space
    issues where X/Z scaling detection fails while Y scaling works correctly.
    
    Args:
        bone_name (str): Name of the bone to check
        
    Returns:
        bool: True if X/Z analysis should be skipped (use Y-only scaling)
    """
    # Bones known to have X/Z scaling coordinate space issues
    problematic_bones = [
        'neck', 'head', 'spine', 'chest',
        'upper chest', 'lower chest'
    ]
    
    bone_lower = bone_name.lower()
    return any(problem in bone_lower for problem in problematic_bones)

def analyze_bone_xyz_scaling_from_mesh(original_meshes, modified_meshes, bone_name, bone_head_pos, bone_tail_pos):
    """
    Reverse-engineer XYZ scaling by analyzing vertex displacement patterns.
    IMPROVED: Only analyzes vertices with exclusive bone influence and spatial filtering.
    TEMPORARY FIX: Skip X/Z analysis for problematic bones (neck, head, spine)
    
    Args:
        original_meshes (list): List of original mesh objects
        modified_meshes (list): List of modified mesh objects  
        bone_name (str): Name of the bone to analyze
        bone_head_pos (Vector): Bone head position in world space
        bone_tail_pos (Vector): Bone tail position in world space
        
    Returns:
        tuple: (x_scale, z_scale, success) - Returns scaling factors and success flag
    """
    try:
        print(f"MESH ANALYSIS IMPROVED: Analyzing XYZ scaling for bone '{bone_name}'")
        
        # TEMPORARY FIX: Skip X/Z analysis for problematic bones
        if should_skip_xz_scaling_analysis(bone_name):
            print(f"SCALING FIX: Skipping X/Z analysis for '{bone_name}' - coordinate space issues detected")
            print(f"            Using Y-only scaling (X=1.0, Z=1.0) as temporary solution")
            print(f"            See X_Z_AXIS_SCALING_ANALYSIS.md for details")
            return 1.0, 1.0, False  # Force X=1.0, Z=1.0, success=False
        
        # Calculate bone geometry for reference points
        bone_center = (bone_head_pos + bone_tail_pos) / 2.0
        bone_vector = bone_tail_pos - bone_head_pos
        bone_length = bone_vector.length
        
        print(f"MESH ANALYSIS: Bone head: {bone_head_pos}")
        print(f"MESH ANALYSIS: Bone tail: {bone_tail_pos}")
        print(f"MESH ANALYSIS: Bone center: {bone_center}")
        print(f"MESH ANALYSIS: Bone length: {bone_length:.3f}")
        
        x_scale_samples = []
        z_scale_samples = []
        vertices_analyzed = 0
        exclusive_vertices_found = 0
        mixed_weight_vertices_skipped = 0
        
        # Find matching meshes (flexible name matching for Blender's duplicate naming)
        mesh_pairs = []
        for orig_mesh in original_meshes:
            for mod_mesh in modified_meshes:
                orig_base = orig_mesh.name
                mod_base = mod_mesh.name
                
                # Remove common Blender suffixes (.001, .002, .003, etc.)
                import re
                orig_base = re.sub(r'\.\d{3}$', '', orig_base)
                mod_base = re.sub(r'\.\d{3}$', '', mod_base)
                
                # Check for exact match, base name match, or similar names
                if (orig_mesh.name == mod_mesh.name or  # Exact match
                    orig_base == mod_base or  # Base name match (e.g., "Body all" matches "Body all")
                    (orig_base in mod_mesh.name and len(orig_base) > 5) or  # Original base in modified name
                    (mod_base in orig_mesh.name and len(mod_base) > 5)):  # Modified base in original name
                    mesh_pairs.append((orig_mesh, mod_mesh))
                    print(f"MESH ANALYSIS: Matched '{orig_mesh.name}' with '{mod_mesh.name}'")
                    break
        
        if not mesh_pairs:
            print(f"MESH ANALYSIS: No matching meshes found between original and modified")
            return 1.0, 1.0, False
        
        print(f"MESH ANALYSIS: Found {len(mesh_pairs)} mesh pairs to analyze")
        
        # Analyze each mesh pair
        for orig_mesh, mod_mesh in mesh_pairs:
            # Find vertex group for this bone
            target_vertex_group = None
            for vg in mod_mesh.vertex_groups:
                if vg.name == bone_name or bone_name.lower() in vg.name.lower():
                    target_vertex_group = vg
                    break
            
            if not target_vertex_group:
                print(f"MESH ANALYSIS: No vertex group found for bone '{bone_name}' in mesh '{mod_mesh.name}'")
                continue
                
            print(f"MESH ANALYSIS: Found vertex group '{target_vertex_group.name}' in mesh '{mod_mesh.name}'")
            
            # IMPROVED: Find vertices with EXCLUSIVE bone influence (weight=1.0 for target, 0.0 for others)
            exclusive_vertices = []
            
            for vertex_idx, vertex in enumerate(mod_mesh.data.vertices):
                # Check all vertex groups this vertex belongs to
                vertex_weights = {}
                for group in vertex.groups:
                    if group.group < len(mod_mesh.vertex_groups):
                        group_name = mod_mesh.vertex_groups[group.group].name
                        vertex_weights[group_name] = group.weight
                
                # Check if this vertex has exclusive influence from our target bone
                target_weight = vertex_weights.get(target_vertex_group.name, 0.0)
                
                # Debug output for first few vertices
                if vertex_idx < 5:
                    print(f"MESH DEBUG: Vertex {vertex_idx} weights: {vertex_weights}")
                
                # EXCLUSIVE FILTERING: Only vertices with full weight for target bone and no other influences
                if target_weight >= 0.99:  # Allow tiny floating point errors
                    # Check if vertex has no significant weight in other bones
                    other_weights = [w for name, w in vertex_weights.items() if name != target_vertex_group.name and w > 0.01]
                    
                    if not other_weights:  # No other bone influences
                        # SPATIAL FILTERING: Only vertices in middle 50% of bone (25%-75% along bone axis)
                        vertex_pos = mod_mesh.matrix_world @ vertex.co
                        
                        # Project vertex onto bone axis to find position along bone
                        bone_to_vertex = vertex_pos - bone_head_pos
                        if bone_length > 0:
                            projection_ratio = bone_to_vertex.dot(bone_vector) / (bone_length * bone_length)
                            
                            # Only use vertices in middle section of bone (avoids joint areas)
                            if 0.25 <= projection_ratio <= 0.75:
                                exclusive_vertices.append(vertex_idx)
                                exclusive_vertices_found += 1
                                print(f"MESH ANALYSIS: EXCLUSIVE vertex {vertex_idx} - weight: {target_weight:.3f}, position: {projection_ratio:.2f} along bone")
                            else:
                                print(f"MESH DEBUG: Vertex {vertex_idx} outside middle section: {projection_ratio:.2f}")
                        else:
                            # Zero-length bone, just use the vertex
                            exclusive_vertices.append(vertex_idx)
                            exclusive_vertices_found += 1
                    else:
                        mixed_weight_vertices_skipped += 1
                        if vertex_idx < 10:  # Debug first few mixed vertices
                            print(f"MESH DEBUG: Vertex {vertex_idx} MIXED WEIGHTS - target: {target_weight:.3f}, others: {other_weights}")
            
            print(f"MESH ANALYSIS: Found {len(exclusive_vertices)} exclusive vertices for '{bone_name}'")
            print(f"MESH ANALYSIS: Exclusive vertices found: {exclusive_vertices_found}")
            print(f"MESH ANALYSIS: Mixed weight vertices skipped: {mixed_weight_vertices_skipped}")
            
            if not exclusive_vertices:
                print(f"MESH ANALYSIS: No exclusive vertices found for bone '{bone_name}' - all vertices have mixed bone influences")
                continue
            
            # Prioritize vertices but use more if available (up to 50 for better accuracy)
            sample_vertices = exclusive_vertices[:50] if len(exclusive_vertices) > 50 else exclusive_vertices
            print(f"MESH ANALYSIS: Analyzing {len(sample_vertices)} exclusive vertex samples")
            
            for vert_idx in sample_vertices:
                if vert_idx >= len(orig_mesh.data.vertices):
                    continue  # Skip if vertex doesn't exist in original
                    
                # Get vertex positions in world space
                orig_pos = orig_mesh.matrix_world @ orig_mesh.data.vertices[vert_idx].co
                mod_pos = mod_mesh.matrix_world @ mod_mesh.data.vertices[vert_idx].co
                
                # Calculate distances from bone center (using absolute distance for scaling analysis)
                orig_x_dist = abs(orig_pos.x - bone_center.x)
                orig_z_dist = abs(orig_pos.z - bone_center.z)
                
                mod_x_dist = abs(mod_pos.x - bone_center.x)
                mod_z_dist = abs(mod_pos.z - bone_center.z)
                
                # Only analyze vertices that are far enough from bone center (avoid division by zero)
                if orig_x_dist > 0.005:  # 0.5cm minimum distance (more sensitive)
                    x_scale_ratio = mod_x_dist / orig_x_dist
                    x_scale_samples.append(x_scale_ratio)
                    print(f"MESH ANALYSIS: EXCLUSIVE Vertex {vert_idx} X-scale: {x_scale_ratio:.3f} (dist: {orig_x_dist:.3f} -> {mod_x_dist:.3f})")
                
                if orig_z_dist > 0.005:  # 0.5cm minimum distance (more sensitive)
                    z_scale_ratio = mod_z_dist / orig_z_dist
                    z_scale_samples.append(z_scale_ratio)
                    print(f"MESH ANALYSIS: EXCLUSIVE Vertex {vert_idx} Z-scale: {z_scale_ratio:.3f} (dist: {orig_z_dist:.3f} -> {mod_z_dist:.3f})")
                
                vertices_analyzed += 1
        
        # Calculate final scaling from samples with improved validation
        if not x_scale_samples and not z_scale_samples:
            print(f"MESH ANALYSIS: No valid scaling samples found for bone '{bone_name}'")
            print(f"MESH ANALYSIS: This is expected for bones with no exclusive vertices or no scaling")
            return 1.0, 1.0, False
        
        # IMPROVED outlier filtering with tighter tolerance for exclusive vertices
        def filter_outliers_strict(samples, tolerance=0.5):  # 50% tolerance instead of 200%
            if not samples:
                return []
            if len(samples) <= 2:
                return samples  # Don't filter if too few samples
                
            avg = sum(samples) / len(samples)
            median = sorted(samples)[len(samples)//2]
            
            # Use median-based filtering for better outlier detection
            filtered = [s for s in samples if abs(s - median) / median < tolerance]
            
            print(f"MESH DEBUG: Outlier filtering - original: {len(samples)}, filtered: {len(filtered)}")
            print(f"MESH DEBUG: Average: {avg:.3f}, Median: {median:.3f}")
            
            return filtered if filtered else samples  # Return originals if all filtered out
        
        x_scale_filtered = filter_outliers_strict(x_scale_samples, tolerance=0.3)  # 30% tolerance
        z_scale_filtered = filter_outliers_strict(z_scale_samples, tolerance=0.3)  # 30% tolerance
        
        # Calculate final scaling values with validation
        x_scale = sum(x_scale_filtered) / len(x_scale_filtered) if x_scale_filtered else 1.0
        z_scale = sum(z_scale_filtered) / len(z_scale_filtered) if z_scale_filtered else 1.0
        
        # VALIDATION: Check if results are reasonable
        x_valid = 0.1 <= x_scale <= 10.0  # Scaling should be between 10% and 1000%
        z_valid = 0.1 <= z_scale <= 10.0
        
        print(f"MESH ANALYSIS IMPROVED: Final results for '{bone_name}':")
        print(f"  X-scale: {x_scale:.3f} (from {len(x_scale_filtered)}/{len(x_scale_samples)} samples) - {'VALID' if x_valid else 'INVALID'}")
        print(f"  Z-scale: {z_scale:.3f} (from {len(z_scale_filtered)}/{len(z_scale_samples)} samples) - {'VALID' if z_valid else 'INVALID'}")
        print(f"  Exclusive vertices analyzed: {vertices_analyzed}")
        print(f"  Mixed weight vertices skipped: {mixed_weight_vertices_skipped}")
        
        # VALIDATION: Only return success if we have valid exclusive vertex data
        has_valid_samples = (len(x_scale_filtered) >= 2 or len(z_scale_filtered) >= 2)
        has_reasonable_values = x_valid and z_valid
        
        success = has_valid_samples and has_reasonable_values and exclusive_vertices_found > 0
        
        if not success:
            print(f"MESH ANALYSIS: FAILED validation for '{bone_name}' - falling back to matrix-based scaling")
            print(f"  Reason: exclusive_vertices={exclusive_vertices_found}, valid_samples={has_valid_samples}, reasonable_values={has_reasonable_values}")
            return 1.0, 1.0, False
            
        print(f"MESH ANALYSIS: SUCCESS - Using exclusive vertex analysis for '{bone_name}'")
        return x_scale, z_scale, success
        
    except Exception as e:
        print(f"MESH ANALYSIS ERROR for bone '{bone_name}': {e}")
        return 1.0, 1.0, False

def should_apply_precision_correction_export(bone_name, bone_data, all_transforms):
    """
    Export version of precision correction logic: Only finger bones with inherit_scale=NONE 
    that are children of hand/wrist bones with inherit_scale=FULL need precision data.
    """
    try:
        # Check if this bone has inherit_scale: "NONE"
        bone_inherit_scale = bone_data.get('inherit_scale', 'FULL')
        if bone_inherit_scale != 'NONE':
            return False
        
        # Find parent bone by searching transform data
        parent_bone_name = find_parent_bone_in_transforms(bone_name, all_transforms)
        
        if not parent_bone_name:
            return False
        
        # Check if parent is a hand/wrist bone with inherit_scale: "FULL"
        if parent_bone_name in all_transforms:
            parent_bone_data = all_transforms[parent_bone_name]
            parent_inherit_scale = parent_bone_data.get('inherit_scale', 'FULL')
            
            # Check if parent is a hand/wrist bone
            parent_name_lower = parent_bone_name.lower()
            is_hand_wrist = any(keyword in parent_name_lower for keyword in ['hand', 'wrist'])
            
            if parent_inherit_scale == 'FULL' and is_hand_wrist:
                print(f"DEBUG EXPORT: '{bone_name}' needs precision data (parent '{parent_bone_name}' is hand/wrist with FULL inheritance)")
                return True
        
        return False
        
    except Exception as e:
        print(f"ERROR checking precision correction need for {bone_name}: {e}")
        return False

def find_parent_bone_in_transforms(bone_name, all_transforms):
    """
    Find parent bone using VRChat naming patterns and transform data
    """
    # VRChat bone hierarchy patterns
    hierarchy_patterns = {
        'Index_Proximal_L': 'Left wrist',
        'Middle_Proximal_L': 'Left wrist',
        'Ring_Proximal_L': 'Left wrist', 
        'Little_Proximal_L': 'Left wrist',
        'Thumb_Proximal_L': 'Left wrist',
        'Index_Proximal_R': 'Right wrist',
        'Middle_Proximal_R': 'Right wrist',
        'Ring_Proximal_R': 'Right wrist',
        'Little_Proximal_R': 'Right wrist', 
        'Thumb_Proximal_R': 'Right wrist',
    }
    
    # Check direct pattern match first
    if bone_name in hierarchy_patterns:
        parent_name = hierarchy_patterns[bone_name]
        if parent_name in all_transforms:
            return parent_name
    
    # Check if bone has parent_name in transform data
    if 'parent_name' in all_transforms.get(bone_name, {}):
        return all_transforms[bone_name]['parent_name']
    
    return None
import numpy as np

# Import the updated transforms_different function (includes bone length detection)
from .armature_diff import transforms_different

def convert_head_tail_to_pose_transforms(original_transforms, modified_transforms):
    """
    Convert head/tail differences between armatures into standard pose transform format
    This allows the diff export to produce presets compatible with normal preset loader
    
    Returns: dict with bones in standard location/rotation_quaternion/scale format
    """
    pose_transforms = {}
    
    for bone_name in modified_transforms:
        if bone_name not in original_transforms:
            continue
            
        original_transform = original_transforms[bone_name]
        modified_transform = modified_transforms[bone_name]
        
        # Check if transforms are different
        if transforms_different(original_transform, modified_transform):
            # Check if this is a pure bone length change vs matrix change
            original_length = original_transform.get('bone_length', 0.0)
            modified_length = modified_transform.get('bone_length', 0.0)
            
            # Compare relative matrices for position/rotation changes  
            matrix1 = original_transform['relative_matrix']
            matrix2 = modified_transform['relative_matrix']
            matrix_different = False
            for i in range(4):
                for j in range(4):
                    if abs(matrix1[i][j] - matrix2[i][j]) > 0.01:
                        matrix_different = True
                        break
                if matrix_different:
                    break
            
            if not matrix_different and abs(original_length - modified_length) > 0.001:
                # PURE LENGTH CHANGE - convert directly to Y-scale
                length_ratio = modified_length / original_length if original_length > 0 else 1.0
                
                pose_transforms[bone_name] = {
                    'location': [0.0, 0.0, 0.0],  # No position change
                    'rotation_quaternion': [1.0, 0.0, 0.0, 0.0],  # No rotation change
                    'scale': [1.0, length_ratio, 1.0],  # Y-axis scaled by length ratio
                    'inherit_scale': modified_transform['inherit_scale']
                }
                
                print(f"DEBUG: Pure length change detected for '{bone_name}': {original_length:.6f} -> {modified_length:.6f} (Y-scale: {length_ratio:.6f})")
                
            else:
                # MATRIX CHANGE - use existing conversion logic
                pose_transform = matrix_to_pose_transform(
                    original_transform, 
                    modified_transform,
                    invert_direction=True  # Match the existing diff export logic
                )
                
                # INHERITANCE COMPENSATION: Fix scale values for broken inheritance chains
                compensated_scale = pose_transform['scale']
                bone_inherit_scale = modified_transform['inherit_scale']
                
                # Check if this bone has inherit_scale='FULL' but parent has inherit_scale='NONE'
                if bone_inherit_scale == 'FULL':
                    # Find parent bone in the transforms
                    parent_name = modified_transform.get('parent_name')
                    if parent_name and parent_name in modified_transforms:
                        parent_transform = modified_transforms[parent_name]
                        parent_inherit_scale = parent_transform['inherit_scale']
                        
                        if parent_inherit_scale == 'NONE':
                            # Parent breaks inheritance chain - compensate child scale
                            # Find parent's scale values in the pose_transforms we're building
                            if parent_name in pose_transforms:
                                parent_scale = pose_transforms[parent_name]['scale']
                                
                                # Calculate scale compensation factors
                                scale_compensation = [
                                    1.0 / parent_scale[0] if parent_scale[0] != 0 else 1.0,
                                    1.0 / parent_scale[1] if parent_scale[1] != 0 else 1.0,
                                    1.0 / parent_scale[2] if parent_scale[2] != 0 else 1.0
                                ]
                                
                                # Compensate scale: divide out parent's scaling
                                compensated_scale = [
                                    compensated_scale[0] * scale_compensation[0],
                                    compensated_scale[1] * scale_compensation[1],
                                    compensated_scale[2] * scale_compensation[2]
                                ]
                                
                                # POSITION COMPENSATION: Also compensate location for broken inheritance
                                # When parent scale changes, child positions need to be adjusted accordingly
                                compensated_location = pose_transform['location']
                                if any(abs(comp - 1.0) > 0.001 for comp in scale_compensation):
                                    # Apply inverse scaling to position to account for parent scale compensation
                                    compensated_location = [
                                        pose_transform['location'][0] * scale_compensation[0],
                                        pose_transform['location'][1] * scale_compensation[1], 
                                        pose_transform['location'][2] * scale_compensation[2]
                                    ]
                                    
                                    print(f"DEBUG EXPORT: Position compensation for '{bone_name}' - original: {pose_transform['location']}, compensated: {compensated_location}")
                                
                                print(f"DEBUG EXPORT: Inheritance compensation for '{bone_name}' - scale: {pose_transform['scale']} → {compensated_scale}")
                                
                                # Update the pose_transform with compensated values
                                pose_transform['location'] = compensated_location

                pose_transforms[bone_name] = {
                    'location': pose_transform['location'],
                    'rotation_quaternion': pose_transform['rotation_quaternion'], 
                    'scale': compensated_scale,
                    'inherit_scale': modified_transform['inherit_scale']
                }
                
                print(f"DEBUG: Matrix change detected for '{bone_name}' - using matrix conversion")
    
    return pose_transforms

def convert_head_tail_to_pose_transforms_filtered(original_transforms, modified_transforms, original_meshes=None, modified_meshes=None):
    """
    Convert head/tail differences between armatures into standard pose transform format
    REVERTED TO OLD LOGIC: Focus on fixing foot bone positioning issue only
    
    Returns: dict with bones in standard location/rotation_quaternion/scale format
    """
    pose_transforms = {}
    
    # COMPATIBILITY: Keep external parameter names, use better internal names
    baseline_transforms = original_transforms  # Better internal naming
    target_transforms = modified_transforms    # Better internal naming
    
    for bone_name in target_transforms:
        if bone_name not in baseline_transforms:
            continue
            
        baseline_transform = baseline_transforms[bone_name]
        target_transform = target_transforms[bone_name]
        
        # Check if transforms are different using smart filtering  
        if transforms_different(baseline_transform, target_transform):
            print(f"DEBUG EXPORT: Processing bone '{bone_name}' with actual differences")
            
            # Check if this is a pure bone length change vs matrix change
            baseline_length = baseline_transform.get('bone_length', 0.0)
            target_length = target_transform.get('bone_length', 0.0)
            
            # Compare relative matrices for position/rotation changes  
            matrix1 = baseline_transform['relative_matrix']
            matrix2 = target_transform['relative_matrix']
            matrix_different = False
            max_matrix_diff = 0.0
            for i in range(4):
                for j in range(4):
                    diff = abs(matrix1[i][j] - matrix2[i][j])
                    max_matrix_diff = max(max_matrix_diff, diff)
                    if diff > 0.01:
                        matrix_different = True
                        break
                if matrix_different:
                    break
            
            print(f"DEBUG EXPORT: '{bone_name}' - Matrix diff: {max_matrix_diff:.6f}, Length diff: {abs(baseline_length - target_length):.6f}")
            
            # IMPROVED LOGIC: Only treat as "pure length change" if matrix changes are truly minimal
            # If there are significant matrix changes (like XYZ scaling), always use matrix change path
            if not matrix_different and abs(baseline_length - target_length) > 0.001 and max_matrix_diff < 0.005:
                # PURE LENGTH CHANGE - but still check mesh analysis for XYZ scaling
                length_ratio = target_length / baseline_length if baseline_length > 0 else 1.0
                
                # MESH VERTEX ANALYSIS: Try to get accurate XYZ scaling even for "pure length change"
                mesh_x_scale, mesh_z_scale, mesh_analysis_success = 1.0, 1.0, False
                final_scale = [1.0, length_ratio, 1.0]  # Default Y-only scaling
                
                if original_meshes and modified_meshes:
                    target_abs_matrix = target_transform['absolute_matrix']
                    bone_head_pos = target_abs_matrix.translation
                    bone_tail_pos = target_abs_matrix @ Vector((0, target_length, 0, 1))
                    bone_tail_pos = bone_tail_pos.xyz
                    
                    mesh_x_scale, mesh_z_scale, mesh_analysis_success = analyze_bone_xyz_scaling_from_mesh(
                        original_meshes, modified_meshes, bone_name, bone_head_pos, bone_tail_pos
                    )
                    
                    if mesh_analysis_success:
                        print(f"MESH ANALYSIS SUCCESS (Pure Length): '{bone_name}' - X: {mesh_x_scale:.3f}, Y: {length_ratio:.3f}, Z: {mesh_z_scale:.3f}")
                        # Use mesh analysis results for X and Z, keep calculated Y from bone length
                        final_scale = [mesh_x_scale, length_ratio, mesh_z_scale]
                        print(f"DEBUG: Applied mesh-based XZ scaling to pure length change '{bone_name}': {final_scale}")
                    else:
                        print(f"MESH ANALYSIS FAILED (Pure Length): '{bone_name}' - using Y-only scaling")
                        if should_skip_xz_scaling_analysis(bone_name):
                            print(f"SCALING FIX: Applied Y-only scaling fix for '{bone_name}' (coordinate space issue)")
                else:
                    print(f"DEBUG: No meshes provided for pure length change '{bone_name}' - using Y-only scaling")
                
                # PRECISION DATA: Only calculate target positions for finger bones
                target_abs_matrix = target_transform['absolute_matrix']
                
                # Get pure global coordinates where this bone should end up
                target_head = target_abs_matrix.translation
                target_tail = target_abs_matrix @ Vector((0, target_length, 0, 1))
                target_tail = target_tail.xyz
                
                # Use inheritance chain logic to determine if precision data is needed
                # Only bones that need precision correction should get precision_data
                needs_precision_correction = should_apply_precision_correction_export(bone_name, target_transform, target_transforms)
                
                pose_transforms[bone_name] = {
                    'location': [0.0, 0.0, 0.0],  # No position change
                    'rotation_quaternion': [1.0, 0.0, 0.0, 0.0],  # No rotation change
                    'scale': final_scale,  # XYZ scaling from mesh analysis or Y-only fallback
                    'inherit_scale': baseline_transform['inherit_scale'],  # KEEP ORIGINAL inherit_scale
                }
                
                # ONLY add precision_data for bones that need precision correction
                if needs_precision_correction:
                    pose_transforms[bone_name]['precision_data'] = {
                        'target_head_position': [target_head.x, target_head.y, target_head.z],
                        'target_tail_position': [target_tail.x, target_tail.y, target_tail.z]
                    }
                    print(f"DEBUG PRECISION: Added precision data for finger bone '{bone_name}': head [{target_head.x:.6f}, {target_head.y:.6f}, {target_head.z:.6f}]")
                
                print(f"DEBUG: Pure length change detected for '{bone_name}': {baseline_length:.6f} -> {target_length:.6f} (Y-scale: {length_ratio:.6f})")
                print(f"DEBUG: Matrix changes minimal ({max_matrix_diff:.6f} < 0.005) - using Y-only scaling")
                print(f"DEBUG PRECISION: Target head position: [{target_head.x:.6f}, {target_head.y:.6f}, {target_head.z:.6f}]")
                
            else:
                # MATRIX CHANGE - use existing conversion logic but preserve length scaling
                print(f"DEBUG: Matrix change detected for '{bone_name}' (matrix diff: {max_matrix_diff:.6f}) - using full matrix conversion")
                pose_transform = matrix_to_pose_transform(
                    baseline_transform, 
                    target_transform,
                    invert_direction=True  # Match the existing diff export logic
                )
                
                # MESH VERTEX ANALYSIS: Try to get accurate XYZ scaling from mesh deformation
                mesh_x_scale, mesh_z_scale, mesh_analysis_success = 1.0, 1.0, False
                if original_meshes and modified_meshes:
                    bone_head_pos = target_transform['absolute_matrix'].translation
                    bone_tail_pos = target_transform['absolute_matrix'] @ Vector((0, target_length, 0, 1))
                    bone_tail_pos = bone_tail_pos.xyz
                    
                    mesh_x_scale, mesh_z_scale, mesh_analysis_success = analyze_bone_xyz_scaling_from_mesh(
                        original_meshes, modified_meshes, bone_name, bone_head_pos, bone_tail_pos
                    )
                    
                    if mesh_analysis_success:
                        print(f"MESH ANALYSIS SUCCESS: '{bone_name}' - X: {mesh_x_scale:.3f}, Z: {mesh_z_scale:.3f}")
                        # Override the matrix-based X and Z scaling with mesh analysis results
                        mesh_corrected_scale = [mesh_x_scale, pose_transform['scale'][1], mesh_z_scale]
                        pose_transform['scale'] = mesh_corrected_scale
                        print(f"DEBUG: Applied mesh-based XZ scaling to '{bone_name}': {mesh_corrected_scale}")
                    else:
                        print(f"MESH ANALYSIS FAILED: '{bone_name}' - falling back to matrix-based scaling")
                        if should_skip_xz_scaling_analysis(bone_name):
                            print(f"SCALING FIX: Applied Y-only scaling fix for '{bone_name}' (coordinate space issue)")
                            # Force X/Z to 1.0 for problematic bones even in matrix mode
                            matrix_corrected_scale = [1.0, pose_transform['scale'][1], 1.0]
                            pose_transform['scale'] = matrix_corrected_scale
                            print(f"DEBUG: Forced Y-only scaling for '{bone_name}': {matrix_corrected_scale}")
                else:
                    print(f"DEBUG: No meshes provided for '{bone_name}' - using matrix-based scaling only")
                
                # SMART SCALING FIX: Check for uniform vs non-uniform scaling before overriding Y-scale
                length_difference = abs(baseline_length - target_length)
                if length_difference > 0.001:  # Significant length change
                    length_ratio = target_length / baseline_length if baseline_length > 0 else 1.0
                    
                    # Check if this is uniform XYZ scaling (all axes have similar scale values)
                    original_scale = pose_transform['scale']
                    is_uniform_scaling = (
                        abs(original_scale[0] - original_scale[1]) < 0.1 and
                        abs(original_scale[1] - original_scale[2]) < 0.1 and
                        abs(original_scale[0] - original_scale[2]) < 0.1 and
                        abs(original_scale[1] - length_ratio) < 0.1  # Y-scale matches bone length change
                    )
                    
                    if is_uniform_scaling:
                        print(f"DEBUG: Detected uniform XYZ scaling for '{bone_name}': {original_scale} - preserving full XYZ scaling")
                        # Keep the original matrix scaling - don't override with bone length
                        corrected_scale = original_scale
                    else:
                        print(f"DEBUG: Overriding Y-scale for '{bone_name}' due to bone length change: {baseline_length:.6f} -> {target_length:.6f} (ratio: {length_ratio:.6f})")
                        # Override the Y-scale component while preserving X and Z scaling
                        corrected_scale = [pose_transform['scale'][0], length_ratio, pose_transform['scale'][2]]
                    
                    pose_transform['scale'] = corrected_scale
                
                # USE MODIFIED INHERIT_SCALE: Export the inherit_scale from the modified armature
                # This is correct - if user set finger bones to NONE, that's intentional
                inherit_scale_to_use = target_transform['inherit_scale']
                print(f"DEBUG: Using modified inherit_scale for '{bone_name}': {inherit_scale_to_use}")
                
                # INHERITANCE COMPENSATION: Fix scale values for broken inheritance chains
                compensated_scale = pose_transform['scale']
                
                # Check if this bone has inherit_scale='FULL' but parent has inherit_scale='NONE'
                if inherit_scale_to_use == 'FULL':
                    # Find parent bone in the transforms
                    parent_name = target_transform.get('parent_name')
                    if parent_name and parent_name in target_transforms:
                        parent_transform = target_transforms[parent_name]
                        parent_inherit_scale = parent_transform['inherit_scale']
                        
                        if parent_inherit_scale == 'NONE':
                            # Parent breaks inheritance chain - compensate child scale
                            # Find parent's scale values in the pose_transforms we're building
                            if parent_name in pose_transforms:
                                parent_scale = pose_transforms[parent_name]['scale']
                                
                                # Calculate scale compensation factors
                                scale_compensation = [
                                    1.0 / parent_scale[0] if parent_scale[0] != 0 else 1.0,
                                    1.0 / parent_scale[1] if parent_scale[1] != 0 else 1.0,
                                    1.0 / parent_scale[2] if parent_scale[2] != 0 else 1.0
                                ]
                                
                                # Compensate scale: divide out parent's scaling
                                compensated_scale = [
                                    compensated_scale[0] * scale_compensation[0],
                                    compensated_scale[1] * scale_compensation[1],
                                    compensated_scale[2] * scale_compensation[2]
                                ]
                                
                                # POSITION COMPENSATION: Also compensate location for broken inheritance
                                # When parent scale changes, child positions need to be adjusted accordingly
                                compensated_location = pose_transform['location']
                                if any(abs(comp - 1.0) > 0.001 for comp in scale_compensation):
                                    # Apply inverse scaling to position to account for parent scale compensation
                                    compensated_location = [
                                        pose_transform['location'][0] * scale_compensation[0],
                                        pose_transform['location'][1] * scale_compensation[1], 
                                        pose_transform['location'][2] * scale_compensation[2]
                                    ]
                                    
                                    print(f"DEBUG EXPORT FILTERED: Position compensation for '{bone_name}' - original: {pose_transform['location']}, compensated: {compensated_location}")
                                
                                print(f"DEBUG EXPORT FILTERED: Inheritance compensation for '{bone_name}' - scale: {pose_transform['scale']} → {compensated_scale}")
                                
                                # Update the pose_transform with compensated values
                                pose_transform['location'] = compensated_location

                # PRECISION DATA COLLECTION: Get target coordinates where bone should end up
                target_abs_matrix = target_transform['absolute_matrix']
                
                # Get pure global coordinates where this bone should end up
                target_head_matrix = target_abs_matrix.translation
                target_tail_matrix = target_abs_matrix @ Vector((0, target_length, 0, 1))
                target_tail_matrix = target_tail_matrix.xyz
                
                # Use inheritance chain logic to determine if precision data is needed
                needs_precision_correction = should_apply_precision_correction_export(bone_name, target_transform, target_transforms)
                
                pose_transforms[bone_name] = {
                    'location': pose_transform['location'],
                    'rotation_quaternion': pose_transform['rotation_quaternion'], 
                    'scale': compensated_scale,
                    'inherit_scale': inherit_scale_to_use,  # SMART inherit_scale handling
                }
                
                # ONLY add precision_data for bones that need precision correction
                if needs_precision_correction:
                    pose_transforms[bone_name]['precision_data'] = {
                        'target_head_position': [target_head_matrix.x, target_head_matrix.y, target_head_matrix.z],
                        'target_tail_position': [target_tail_matrix.x, target_tail_matrix.y, target_tail_matrix.z]
                    }
                    print(f"DEBUG PRECISION: Added precision data for finger bone '{bone_name}': head [{target_head_matrix.x:.6f}, {target_head_matrix.y:.6f}, {target_head_matrix.z:.6f}]")
                
                print(f"DEBUG: Matrix change detected for '{bone_name}' - using matrix conversion with smart inherit_scale")
    
    # INTELLIGENT CHILD FILTERING: Remove position offsets that are purely inherited from parent scaling
    pose_transforms = remove_inherited_child_positions(pose_transforms, baseline_transforms, target_transforms)
    
    # TARGETED FIX: Additional filtering for parent Y-scaling cases that slip through
    pose_transforms = filter_parent_scaling_offsets(pose_transforms, baseline_transforms, target_transforms)
    
    print(f"DEBUG: OLD LOGIC with smart inherit_scale + intelligent child filtering + targeted parent scaling fix - exported {len(pose_transforms)} bones")
    return pose_transforms

def remove_inherited_child_positions(pose_transforms, baseline_transforms, target_transforms):
    """
    Remove child bone position offsets that are purely the result of parent scaling in Edit Mode.
    
    In Edit Mode, when parent bones are scaled, child bones appear to move in absolute coordinates.
    However, in Pose Mode, these child bones should have (0,0,0) location because Blender 
    handles parent-child relationships automatically.
    
    This function identifies and removes these inherited position offsets while preserving
    any independent child bone transformations (like their own scaling).
    """
    print(f"DEBUG: Applying intelligent child position filtering...")
    
    # Build parent-child relationships map
    parent_child_map = {}
    for bone_name, transform in baseline_transforms.items():
        parent_name = transform.get('parent_name')
        if parent_name:
            if parent_name not in parent_child_map:
                parent_child_map[parent_name] = []
            parent_child_map[parent_name].append(bone_name)
    
    bones_filtered = 0
    
    # For each bone in pose_transforms, check if it's a child with inherited position offset
    for bone_name, transform_data in pose_transforms.items():
        # Get parent information
        parent_name = baseline_transforms.get(bone_name, {}).get('parent_name')
        
        if parent_name and parent_name in pose_transforms:
            parent_transform = pose_transforms[parent_name]
            parent_scale = parent_transform.get('scale', [1.0, 1.0, 1.0])
            
            # FIXED INHERITANCE LOGIC: Check if THIS CHILD has inherit_scale='NONE'
            child_inherit_scale = baseline_transforms.get(bone_name, {}).get('inherit_scale', 'FULL')
            if child_inherit_scale == 'NONE':
                # THIS CHILD has inherit_scale='NONE' -> doesn't inherit parent scaling
                # Child transformations are ALWAYS independent, never filter them
                print(f"       Child '{bone_name}' has inherit_scale='NONE' - doesn't inherit parent scaling, skipping child filtering")
                continue
            
            # Check if parent OR any ancestor has significant scaling
            has_ancestor_scaling = False
            current_parent = parent_name
            scaling_ancestor = None
            
            # Walk up the parent chain to find any scaled ancestors
            while current_parent and current_parent in pose_transforms:
                ancestor_scale = pose_transforms[current_parent].get('scale', [1.0, 1.0, 1.0])
                if abs(ancestor_scale[1] - 1.0) > 0.01:  # Y-axis scaling
                    has_ancestor_scaling = True
                    scaling_ancestor = current_parent
                    print(f"       Found scaling ancestor '{current_parent}' with Y-scale: {ancestor_scale[1]:.4f}")
                    break
                # Move to next parent
                current_parent = baseline_transforms.get(current_parent, {}).get('parent_name')
            
            if has_ancestor_scaling:
                child_location = transform_data.get('location', [0.0, 0.0, 0.0])
                
                # Check if child has position offset that looks like inherited movement
                has_position_offset = any(abs(loc) > 0.001 for loc in child_location)
                
                if has_position_offset:
                    # Check if this child should have independent transforms
                    child_orig = baseline_transforms.get(bone_name, {})
                    child_mod = target_transforms.get(bone_name, {})
                    
                    # Check if child has its own independent scaling or rotation changes
                    child_scale = transform_data.get('scale', [1.0, 1.0, 1.0]) 
                    has_own_scaling = any(abs(scale - 1.0) > 0.001 for scale in child_scale)
                    
                    # Check if child bone actually moved independently in the original diff
                    if child_orig and child_mod:
                        # Compare bone lengths to see if child itself was scaled
                        orig_length = child_orig.get('bone_length', 0.0)
                        mod_length = child_mod.get('bone_length', 0.0)
                        has_length_change = abs(orig_length - mod_length) > 0.001
                        
                        if has_length_change:
                            # Child has its own length change - keep some position but reduce magnitude
                            print(f"       Child '{bone_name}' has own length changes - keeping transforms but reducing inherited position")
                            # Keep the bone's own transforms but zero out likely inherited position
                            transform_data['location'] = [0.0, 0.0, 0.0]
                            bones_filtered += 1
                        else:
                            # Child has no independent changes - this is pure inheritance, remove position
                            print(f"       Child '{bone_name}' has pure inherited position: {child_location} -> [0,0,0]")
                            transform_data['location'] = [0.0, 0.0, 0.0]
                            bones_filtered += 1
                    else:
                        # No original/modified data available, assume inherited and remove
                        print(f"       Child '{bone_name}' removing inherited position: {child_location} -> [0,0,0]")
                        transform_data['location'] = [0.0, 0.0, 0.0]
                        bones_filtered += 1
                        
                    print(f"       Scaling ancestor '{scaling_ancestor}' scale: {pose_transforms[scaling_ancestor]['scale'][1]:.4f}, Child location was: {child_location}")
    
    print(f"DEBUG: Filtered {bones_filtered} child bones with inherited position offsets")
    return pose_transforms

def filter_parent_scaling_offsets(pose_transforms, baseline_transforms, target_transforms):
    """
    TARGETED FIX: Remove location offsets from child bones when parent has significant scaling on ANY axis
    
    This handles all scaling scenarios:
    - X-axis: scale=[0.5, 1.0, 1.0] → children move in X direction
    - Y-axis: scale=[1.0, 0.5, 1.0] → children move in Y direction  
    - Z-axis: scale=[1.0, 1.0, 0.5] → children move in Z direction
    - Multi-axis: scale=[0.5, 0.5, 1.0] → children move in multiple directions
    
    When a parent bone is scaled on any axis, children automatically move in pose mode.
    These inherited location offsets should NOT be stored as additional transforms.
    """
    print(f"DEBUG: Applying targeted parent scaling offset filtering (all axes)...")
    
    bones_filtered = 0
    
    for bone_name, transform_data in list(pose_transforms.items()):
        # Get parent information
        parent_name = baseline_transforms.get(bone_name, {}).get('parent_name')
        
        if parent_name and parent_name in pose_transforms:
            parent_transform = pose_transforms[parent_name]
            parent_scale = parent_transform.get('scale', [1.0, 1.0, 1.0])
            
            # Check if parent has significant scaling on ANY axis (X, Y, or Z)
            has_parent_scaling = any(abs(scale - 1.0) > 0.01 for scale in parent_scale)
            
            if has_parent_scaling:
                child_location = transform_data.get('location', [0.0, 0.0, 0.0])
                child_scale = transform_data.get('scale', [1.0, 1.0, 1.0])
                
                # Check if child has significant location offset but no significant scaling of its own
                has_location_offset = any(abs(loc) > 0.001 for loc in child_location)
                has_own_scaling = any(abs(scale - 1.0) > 0.01 for scale in child_scale)
                
                # Check inherit_scale setting
                child_inherit_scale = baseline_transforms.get(bone_name, {}).get('inherit_scale', 'FULL')
                
                if has_location_offset and not has_own_scaling and child_inherit_scale == 'FULL':
                    # This child has location offset but no scaling, and inherits from scaled parent
                    # This is likely an inherited position offset that should be removed
                    
                    print(f"       TARGETED FIX: Child '{bone_name}' has inherited position from parent '{parent_name}' scale {parent_scale}")
                    print(f"                     Removing location offset: {child_location} -> [0,0,0]")
                    
                    transform_data['location'] = [0.0, 0.0, 0.0]
                    bones_filtered += 1
                elif has_location_offset and has_own_scaling:
                    print(f"       KEEPING: Child '{bone_name}' has own scaling {child_scale}, preserving location {child_location}")
                elif child_inherit_scale == 'NONE':
                    print(f"       KEEPING: Child '{bone_name}' has inherit_scale='NONE', independent positioning")
    
    print(f"DEBUG: Targeted filtering removed {bones_filtered} inherited position offsets from parent scaling (all axes)")
    return pose_transforms

# OLD CASCADING FUNCTIONS REMOVED - These were causing incorrect child bone positioning
# The intelligent child filtering approach above is the correct solution

def calculate_head_tail_differences(original_transforms, modified_transforms):
    """
    Calculate direct head/tail differences between two armature transforms
    Returns dict with bone differences using head_tail_direct method
    """
    diff_data = {}
    bones_with_differences = 0
    
    # Compare edit bone matrices for each bone that exists in both armatures
    for bone_name in modified_transforms:
        if bone_name not in original_transforms:
            continue  # Skip bones that don't exist in original
        
        original_transform = original_transforms[bone_name]
        modified_transform = modified_transforms[bone_name]
        
        # Check if edit bone matrices are structurally different
        transform_changed = transforms_different(original_transform, modified_transform)
        
        if transform_changed:
            # DIRECT HEAD/TAIL APPROACH: Store the actual head/tail position changes
            orig_abs_matrix = original_transform['absolute_matrix']
            mod_abs_matrix = modified_transform['absolute_matrix']
            
            # Extract head and tail positions from absolute matrices
            orig_head = orig_abs_matrix.translation
            orig_tail = orig_abs_matrix @ Vector((0, orig_abs_matrix.to_scale().y, 0, 1))
            orig_tail = orig_tail.xyz  # Convert to 3D vector
            
            mod_head = mod_abs_matrix.translation  
            mod_tail = mod_abs_matrix @ Vector((0, mod_abs_matrix.to_scale().y, 0, 1))
            mod_tail = mod_tail.xyz  # Convert to 3D vector
            
            # Calculate head and tail differences
            head_diff = mod_head - orig_head
            tail_diff = mod_tail - orig_tail
            
            # Store as direct head/tail modifications instead of pose transforms
            diff_data[bone_name] = {
                'method': 'head_tail_direct',
                'head_difference': [head_diff.x, head_diff.y, head_diff.z],
                'tail_difference': [tail_diff.x, tail_diff.y, tail_diff.z],
                'inherit_scale': modified_transform['inherit_scale'],
                'original_length': (orig_tail - orig_head).length,
                'modified_length': (mod_tail - mod_head).length
            }
            bones_with_differences += 1
            
            parent_name = original_transform.get('parent_name', 'ROOT')
            print(f"DEBUG: Found HEAD/TAIL difference in bone '{bone_name}' (parent: {parent_name})")
            print(f"  Head diff: [{head_diff.x:.6f}, {head_diff.y:.6f}, {head_diff.z:.6f}]")
            print(f"  Tail diff: [{tail_diff.x:.6f}, {tail_diff.y:.6f}, {tail_diff.z:.6f}]")
            print(f"  Length: {(orig_tail - orig_head).length:.6f} → {(mod_tail - mod_head).length:.6f}")
            
            # FALLBACK: If head/tail approach fails, use pose transforms
            if (head_diff.length < 0.0001 and tail_diff.length < 0.0001):
                print(f"DEBUG: Head/tail differences too small, falling back to pose transforms for '{bone_name}'")
                # Convert relative matrix difference to pose transform components
                pose_transform = matrix_to_pose_transform(
                    original_transform, 
                    modified_transform,
                    invert_direction=True
                )
                
                diff_data[bone_name] = {
                    'method': 'pose_transform',
                    'location': pose_transform['location'],
                    'rotation_quaternion': pose_transform['rotation_quaternion'],
                    'scale': pose_transform['scale'],
                    'inherit_scale': modified_transform['inherit_scale']
                }
    
    return diff_data, bones_with_differences

# Import the updated transforms_different function from armature_diff (includes bone length detection)
from .armature_diff import transforms_different

def matrix_to_pose_transform(original_transform, modified_transform, invert_direction=False):
    """Convert edit bone relative matrix difference to pose transform components"""
    
    # Import Matrix at function level to avoid scoping issues
    from mathutils import Matrix
    
    # Use the relative matrices for calculation
    original_matrix = original_transform['relative_matrix']
    modified_matrix = modified_transform['relative_matrix']
    
    # Handle UI input order compensation
    # User was inputting armatures backwards, so we use original math when inverted=True
    if invert_direction:
        # Use original math (compensates for backwards UI input)
        relative_matrix = original_matrix.inverted() @ modified_matrix
        print("DEBUG: Using ORIGINAL math (compensating for backwards UI input)")
    else:
        # Use swapped math (if UI input was correct)
        relative_matrix = modified_matrix.inverted() @ original_matrix  
        print("DEBUG: Using SWAPPED math (assuming correct UI input)")
    
    # FIXED: Extract full XYZ scaling from the relative matrix
    # Don't override with length-based scaling - use the actual matrix scaling values
    print("DEBUG: Using full XYZ matrix scaling (no length override)")
    
    # Decompose into location, rotation, scale
    location, rotation, scale = relative_matrix.decompose()
    
    # Clean up tiny floating point values to prevent export noise
    def clean_tiny_values(values, threshold=1e-6):
        return [v if abs(v) > threshold else 0.0 for v in values]
    
    # Clean location (values smaller than 0.000001 become 0)
    clean_loc = clean_tiny_values([location.x, location.y, location.z])
    
    # Clean rotation quaternion (but preserve identity quaternion structure)
    clean_rot = clean_tiny_values([rotation.w, rotation.x, rotation.y, rotation.z])
    # Ensure identity quaternion if all rotations are tiny
    if all(abs(v) < 1e-6 for v in clean_rot[1:]):  # x,y,z components are tiny
        clean_rot = [1.0, 0.0, 0.0, 0.0]
    
    # Clean scale (values very close to 1.0 become exactly 1.0)
    clean_scale = []
    for s in [scale.x, scale.y, scale.z]:
        if abs(s - 1.0) < 1e-6:
            clean_scale.append(1.0)
        elif abs(s) < 1e-6:
            clean_scale.append(0.0) 
        else:
            clean_scale.append(s)
    
    # Debug output to verify transform direction
    print(f"DEBUG: Calculated pose transform - Location: {clean_loc}, Scale: {clean_scale}")
    if clean_scale[0] > 1.0 or clean_scale[1] > 1.0 or clean_scale[2] > 1.0:
        print("DEBUG: ✓ Scale > 1.0 detected - should LENGTHEN bones")
    elif clean_scale[0] < 1.0 or clean_scale[1] < 1.0 or clean_scale[2] < 1.0:
        print("DEBUG: ⚠ Scale < 1.0 detected - will SHRINK bones") 
    
    return {
        'location': clean_loc,
        'rotation_quaternion': clean_rot,
        'scale': clean_scale
    }

def apply_head_tail_transform_with_mesh_deformation(armature, bone_name, transform_data):
    """
    Apply head/tail direct transforms AND ensure mesh deformation
    This is the FIXED version that properly handles mesh transformation
    """
    try:
        print(f"DEBUG: FIXED method - Applying head/tail transform with mesh deformation to '{bone_name}'")
        
        # Store current state
        original_mode = bpy.context.mode
        
        # STEP 1: Apply head/tail differences in edit mode
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        if bone_name in armature.data.edit_bones:
            edit_bone = armature.data.edit_bones[bone_name]
            
            # Apply head and tail differences
            head_diff = Vector(transform_data['head_difference'])
            tail_diff = Vector(transform_data['tail_difference'])
            
            print(f"DEBUG: Applying head/tail to '{bone_name}': head_diff={head_diff}, tail_diff={tail_diff}")
            
            # Store original positions for mesh calculation
            original_head = edit_bone.head.copy()
            original_tail = edit_bone.tail.copy()
            
            # Update head and tail positions
            edit_bone.head += head_diff
            edit_bone.tail += tail_diff
            
            print(f"DEBUG: Applied head/tail transform to '{bone_name}' successfully")
            
            # STEP 2: Switch to pose mode and create equivalent pose transform for mesh deformation
            bpy.ops.object.mode_set(mode='POSE')
            
            if bone_name in armature.pose.bones:
                pose_bone = armature.pose.bones[bone_name]
                
                # Calculate the equivalent scale transform that would produce the same length change
                original_length = (original_tail - original_head).length
                new_length = (edit_bone.tail - edit_bone.head).length
                
                if original_length > 0.001:  # Avoid division by zero
                    scale_factor = new_length / original_length
                    print(f"DEBUG: Calculated scale factor: {scale_factor} for mesh deformation")
                    
                    # Apply the scale to the pose bone for mesh deformation
                    # This ensures the mesh deforms properly when "Apply as Rest Pose" is called
                    pose_bone.scale.y = scale_factor  # Y-axis is bone length in Blender
                    
                    print(f"DEBUG: Applied pose scale {scale_factor} to bone '{bone_name}' for mesh deformation")
            
            return True
        else:
            print(f"DEBUG: ERROR - Edit bone '{bone_name}' not found!")
            return False
            
    except Exception as e:
        print(f"DEBUG: Error applying head/tail transform with mesh deformation to '{bone_name}': {e}")
        return False
    finally:
        # Switch back to original mode
        if original_mode == 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        elif original_mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

def get_armature_transforms(armature):
    """Extract edit bone relative transforms and inherit_scale from an armature for structural comparison"""
    transforms = {}
    
    try:
        # Store current state
        original_active = bpy.context.view_layer.objects.active
        original_selected = bpy.context.selected_objects[:]
        original_mode = bpy.context.mode
        
        # Switch to object mode and select armature
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        
        # Get edit bone transforms (structural data)
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Extract edit bone matrices and calculate relative transforms
        for edit_bone in armature.data.edit_bones:
            # Get the edit bone's absolute matrix
            absolute_matrix = edit_bone.matrix.copy()
            
            # Calculate relative matrix (bone transform relative to its parent)
            if edit_bone.parent:
                # FIXED INHERITANCE LOGIC: Check the CHILD's inherit_scale setting, not parent's
                parent_matrix = edit_bone.parent.matrix.copy()
                
                if edit_bone.inherit_scale == 'NONE':
                    # THIS bone has inherit_scale='NONE' -> use unscaled parent matrix
                    # Extract only rotation and translation, set scale to (1,1,1)
                    parent_loc, parent_rot, parent_scale = parent_matrix.decompose()
                    
                    # Create new matrix with scale reset to (1,1,1)
                    from mathutils import Matrix
                    unscaled_parent_matrix = Matrix.LocRotScale(parent_loc, parent_rot, (1.0, 1.0, 1.0))
                    relative_matrix = unscaled_parent_matrix.inverted() @ absolute_matrix
                    
                    print(f"DEBUG: Child '{edit_bone.name}' has inherit_scale='NONE' - using unscaled parent matrix")
                else:
                    # Child has inherit_scale='FULL' or other - use full parent matrix
                    relative_matrix = parent_matrix.inverted() @ absolute_matrix
                    
                    if edit_bone.inherit_scale == 'FULL':
                        print(f"DEBUG: Child '{edit_bone.name}' has inherit_scale='FULL' - using full parent matrix from '{edit_bone.parent.name}'")
            else:
                # Root bone - use absolute matrix
                relative_matrix = absolute_matrix
            
            transforms[edit_bone.name] = {
                'relative_matrix': relative_matrix,
                'absolute_matrix': absolute_matrix,  # Keep for debugging
                'parent_name': edit_bone.parent.name if edit_bone.parent else None,
                'inherit_scale': edit_bone.inherit_scale
            }
        
        return transforms
        
    except Exception as e:
        print(f"Error extracting transforms from {armature.name}: {e}")
        return {}
    
    finally:
        # Restore original state
        try:
            if bpy.context.mode != original_mode:
                if original_mode == 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                elif original_mode == 'POSE':
                    bpy.ops.object.mode_set(mode='POSE')
            
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selected:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = original_active
        except:
            pass

def apply_armature_to_mesh_with_no_shape_keys(armature_obj, mesh_obj):
    """Apply armature deformation to mesh without shape keys"""
    print(f"Applying armature to mesh {mesh_obj.name} with no shape keys")
    
    # Store current active object
    original_active = bpy.context.view_layer.objects.active
    original_selected = bpy.context.selected_objects[:]
    
    try:
        # Make mesh active and selected
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
        
        # Add temporary armature modifier
        armature_mod = mesh_obj.modifiers.new('TempPoseToRest', 'ARMATURE')
        armature_mod.object = armature_obj
        mod_name = armature_mod.name
        print(f"Added modifier: {mod_name}")
        
        # Move to top of modifier stack
        if bpy.app.version >= (2, 90, 0):
            bpy.ops.object.modifier_move_to_index(modifier=mod_name, index=0)
        else:
            # For older Blender versions, move up manually
            armature_mod_index = len(mesh_obj.modifiers) - 1
            for _ in range(armature_mod_index):
                bpy.ops.object.modifier_move_up(modifier=mod_name)
        
        # Apply the modifier
        print(f"Applying modifier: {mod_name}")
        bpy.ops.object.modifier_apply(modifier=mod_name)
        print(f"Applied modifier successfully")
        
    finally:
        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = original_active

def apply_armature_to_mesh_with_shape_keys(armature_obj, mesh_obj):
    """Apply armature deformation to mesh with shape keys (CATS method)"""
    print(f"Applying armature to mesh {mesh_obj.name} with shape keys")
    
    # Store current active object and selection
    original_active = bpy.context.view_layer.objects.active
    original_selected = bpy.context.selected_objects[:]
    
    try:
        # Make mesh active
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
        
        # Save current state
        old_active_shape_key_index = mesh_obj.active_shape_key_index
        old_show_only_shape_key = mesh_obj.show_only_shape_key
        
        # Enable shape key pinning
        mesh_obj.show_only_shape_key = True
        
        # Store and temporarily disable shape key properties
        me = mesh_obj.data
        shape_key_vertex_groups = []
        shape_key_mutes = []
        key_blocks = me.shape_keys.key_blocks
        
        print(f"Processing {len(key_blocks)} shape keys")
        
        for shape_key in key_blocks:
            shape_key_vertex_groups.append(shape_key.vertex_group)
            shape_key.vertex_group = ''
            shape_key_mutes.append(shape_key.mute)
            shape_key.mute = False
        
        # Disable all existing modifiers temporarily
        mods_to_reenable_viewport = []
        for mod in mesh_obj.modifiers:
            if mod.show_viewport:
                mod.show_viewport = False
                mods_to_reenable_viewport.append(mod)
        
        # Add temporary armature modifier
        armature_mod = mesh_obj.modifiers.new('TempPoseToRest', 'ARMATURE')
        armature_mod.object = armature_obj
        print(f"Added temporary modifier: {armature_mod.name}")
        
        # Prepare for evaluation
        co_length = len(me.vertices) * 3
        eval_verts_cos_array = np.empty(co_length, dtype=np.single)
        depsgraph = None
        evaluated_mesh_obj = None
        
        def get_eval_cos_array():
            nonlocal depsgraph, evaluated_mesh_obj
            if depsgraph is None or evaluated_mesh_obj is None:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                evaluated_mesh_obj = mesh_obj.evaluated_get(depsgraph)
            else:
                depsgraph.update()
            evaluated_mesh_obj.data.vertices.foreach_get('co', eval_verts_cos_array)
            return eval_verts_cos_array
        
        # Apply armature deformation to each shape key
        for i, shape_key in enumerate(key_blocks):
            print(f"Processing shape key {i}: {shape_key.name}")
            # Set active shape key (with pinning, this shows only this shape key)
            mesh_obj.active_shape_key_index = i
            
            # Get evaluated vertex positions (shape key + armature deformation)
            evaluated_cos = get_eval_cos_array()
            
            # Update shape key with evaluated positions
            shape_key.data.foreach_set('co', evaluated_cos)
            
            # For basis shape key, also update mesh vertices
            if i == 0:
                mesh_obj.data.vertices.foreach_set('co', evaluated_cos)
        
        # Restore original state
        for mod in mods_to_reenable_viewport:
            mod.show_viewport = True
        mesh_obj.modifiers.remove(armature_mod)
        print("Removed temporary modifier")
        
        for shape_key, vertex_group, mute in zip(key_blocks, shape_key_vertex_groups, shape_key_mutes):
            shape_key.vertex_group = vertex_group
            shape_key.mute = mute
            
        mesh_obj.active_shape_key_index = old_active_shape_key_index
        mesh_obj.show_only_shape_key = old_show_only_shape_key
        print("Restored original shape key state")
        
    finally:
        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = original_active