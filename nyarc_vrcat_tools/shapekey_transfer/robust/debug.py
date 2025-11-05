"""
Debug Visualization
Create vertex colors showing match quality for parameter tuning
"""

import bpy
import numpy as np


def create_match_quality_debug(target_obj, matched_indices, distances, distance_threshold):
    """
    Create vertex color layer showing match quality.

    Colors:
    - Blue: Perfect matches (distance < 0.001)
    - Green: Good matches (distance < 0.005)
    - Yellow: Acceptable matches (distance < threshold)
    - Red: Unmatched vertices (will be inpainted)
    """
    mesh = target_obj.data

    # Create or get vertex color layer
    vcol_name = "RobustTransfer_MatchQuality"
    if vcol_name not in mesh.vertex_colors:
        vcol_layer = mesh.vertex_colors.new(name=vcol_name)
    else:
        vcol_layer = mesh.vertex_colors[vcol_name]

    # Build color map
    N = len(mesh.vertices)
    matched_mask = np.zeros(N, dtype=bool)
    matched_mask[matched_indices] = True

    color_map = np.zeros((N, 4))

    for i in range(N):
        if matched_mask[i]:
            dist = distances[matched_indices.tolist().index(i)]

            if dist < 0.001:
                # Perfect match: Blue
                color_map[i] = [0.0, 0.5, 1.0, 1.0]
            elif dist < 0.005:
                # Good match: Green
                color_map[i] = [0.0, 1.0, 0.0, 1.0]
            else:
                # Acceptable match: Yellow
                color_map[i] = [1.0, 1.0, 0.0, 1.0]
        else:
            # Unmatched (will be inpainted): Red
            color_map[i] = [1.0, 0.0, 0.0, 1.0]

    # Apply to vertex color layer
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            loop = mesh.loops[loop_idx]
            vert_idx = loop.vertex_index
            vcol_layer.data[loop_idx].color = color_map[vert_idx]

    # Set as active for viewing
    mesh.vertex_colors.active = vcol_layer

    # Switch viewport shading to show vertex colors
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.color_type = 'VERTEX'

    print(f"Created debug visualization: {vcol_name}")
    print("  Blue = perfect, Green = good, Yellow = acceptable, Red = inpainted")
