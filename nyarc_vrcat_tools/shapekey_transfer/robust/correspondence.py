"""
Geometric Correspondence (Stage 1)
Find closest points and validate matches using distance and normal thresholds
"""

import numpy as np


def find_geometric_correspondence(
    source_verts, source_faces, source_normals, source_displacements,
    target_verts, target_normals,
    distance_threshold, normal_threshold
):
    """
    Find and validate geometric correspondence between source and target.

    Returns:
        matched_indices: (K,) indices of matched target vertices
        matched_displacements: (K, 3) displacement vectors at matched vertices
        distances: (K,) distances for matched vertices
    """
    try:
        # Import here to avoid Blender startup dependency
        import scipy.spatial

        # Build BVH tree for closest point queries
        print("Building BVH tree for source mesh...")
        tree = scipy.spatial.cKDTree(source_verts)

        # Find closest source vertex for each target vertex
        print("Querying closest points...")
        distances, closest_indices = tree.query(target_verts)

        # Get closest source normals and displacements
        closest_normals = source_normals[closest_indices]
        closest_displacements = source_displacements[closest_indices]

        # Validate matches using distance and normal criteria
        print("Validating matches...")
        valid_mask = validate_matches(
            target_verts, target_normals,
            source_verts, closest_normals,
            distances, closest_indices,
            distance_threshold, normal_threshold
        )

        # Extract matched data
        matched_indices = np.where(valid_mask)[0]
        matched_displacements = closest_displacements[valid_mask]
        matched_distances = distances[valid_mask]

        return matched_indices, matched_displacements, matched_distances

    except ImportError as e:
        print(f"ERROR: Missing scipy library: {e}")
        return None


def validate_matches(
    target_verts, target_normals,
    source_verts, source_normals,
    distances, closest_indices,
    distance_threshold, normal_threshold
):
    """
    Validate matches using distance and normal alignment criteria.

    Returns:
        valid_mask: (N,) boolean array, True = valid match
    """
    N = len(target_verts)
    valid_mask = np.zeros(N, dtype=bool)

    # Distance check
    distance_valid = distances < distance_threshold

    # Normal alignment check (bidirectional for flipped normals)
    cos_angles = np.sum(target_normals * source_normals, axis=1)
    normal_valid = np.abs(cos_angles) > normal_threshold

    # Combined validation
    valid_mask = distance_valid & normal_valid

    return valid_mask
