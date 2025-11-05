"""
Mesh Data Extraction and Application
Handles Blender-specific mesh operations
"""

import bpy
import numpy as np


def extract_shape_key_displacements(obj, shape_key_name):
    """
    Extract displacement vectors from shape key.

    Returns:
        displacements: (N, 3) array of delta vectors
        basis_coords: (N, 3) array of basis shape coordinates
    """
    mesh = obj.data

    if not mesh.shape_keys:
        print(f"ERROR: Object {obj.name} has no shape keys")
        return None, None

    if shape_key_name not in mesh.shape_keys.key_blocks:
        print(f"ERROR: Shape key '{shape_key_name}' not found")
        return None, None

    # Get basis and target shape
    basis = mesh.shape_keys.key_blocks[0]  # Basis shape
    shape_key = mesh.shape_keys.key_blocks[shape_key_name]

    # Extract coordinates
    basis_verts = np.array([v.co for v in basis.data])
    shape_verts = np.array([v.co for v in shape_key.data])

    # Compute displacements
    displacements = shape_verts - basis_verts

    return displacements, basis_verts


def get_mesh_data_world_space(obj):
    """
    Extract mesh geometry in world space.

    Returns:
        vertices: (N, 3) vertex coordinates
        faces: (F, 3) triangle indices
        normals: (N, 3) vertex normals
    """
    # Get evaluated mesh (with modifiers applied if needed)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()

    try:
        # Ensure triangulation
        mesh.calc_loop_triangles()

        # Extract vertices in world space
        world_matrix = obj.matrix_world
        vertices = np.array([world_matrix @ v.co for v in mesh.vertices])

        # Extract triangulated faces
        triangles = np.array([
            [v for v in tri.vertices]
            for tri in mesh.loop_triangles
        ])

        # Calculate vertex normals in world space
        # Handle Blender 4.1+ API change (calc_normals_split removed)
        normals = np.zeros((len(mesh.vertices), 3))
        
        if bpy.app.version >= (4, 1, 0):
            # Blender 4.1+: Use corner_normals (automatically updated)
            corner_normals = mesh.corner_normals
            
            # Average corner normals for each vertex
            for tri in mesh.loop_triangles:
                for loop_idx in tri.loops:
                    vert_idx = mesh.loops[loop_idx].vertex_index
                    loop_normal = corner_normals[loop_idx].vector
                    world_normal = world_matrix.to_3x3() @ loop_normal
                    normals[vert_idx] += world_normal
        else:
            # Blender 3.x - 4.0: Use calc_normals_split
            mesh.calc_normals_split()
            
            # Average loop normals for each vertex
            for tri in mesh.loop_triangles:
                for loop_idx in tri.loops:
                    vert_idx = mesh.loops[loop_idx].vertex_index
                    loop_normal = mesh.loops[loop_idx].normal
                    world_normal = world_matrix.to_3x3() @ loop_normal
                    normals[vert_idx] += world_normal

        # Normalize
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normals = normals / norms

        return vertices, triangles, normals

    finally:
        # Clean up evaluated mesh
        obj_eval.to_mesh_clear()


def apply_shape_key_to_mesh(obj, shape_key_name, displacements):
    """
    Create or update shape key on target mesh with computed displacements.

    Args:
        obj: Blender object
        shape_key_name: Name for new/updated shape key
        displacements: (N, 3) displacement vectors
    """
    mesh = obj.data

    # Ensure basis shape key exists
    if not mesh.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)

    # Create or get shape key
    if shape_key_name in mesh.shape_keys.key_blocks:
        shape_key = mesh.shape_keys.key_blocks[shape_key_name]
    else:
        shape_key = obj.shape_key_add(name=shape_key_name, from_mix=False)

    # Apply displacements (in object space)
    basis_verts = np.array([v.co for v in mesh.vertices])
    new_verts = basis_verts + displacements

    for i, coord in enumerate(new_verts):
        shape_key.data[i].co = coord

    print(f"Applied shape key '{shape_key_name}' to {obj.name}")
