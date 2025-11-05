"""
Mesh Island Detection and Special Handling
Handles small disconnected mesh components (buttons, patches, etc.)
"""

import numpy as np
from collections import deque


def detect_mesh_islands(faces, num_vertices):
    """
    Detect disconnected mesh islands using BFS on face adjacency.

    Args:
        faces: Triangle faces (Nx3 array)
        num_vertices: Total number of vertices

    Returns:
        List of islands, where each island is a set of vertex indices
    """
    # Build vertex-to-vertex adjacency from faces
    adjacency = {i: set() for i in range(num_vertices)}

    for face in faces:
        a, b, c = face
        adjacency[a].update([b, c])
        adjacency[b].update([a, c])
        adjacency[c].update([a, b])

    # Find connected components using BFS
    visited = set()
    islands = []

    for start_vertex in range(num_vertices):
        if start_vertex in visited:
            continue

        # BFS from this vertex
        island = set()
        queue = deque([start_vertex])

        while queue:
            vertex = queue.popleft()
            if vertex in visited:
                continue

            visited.add(vertex)
            island.add(vertex)

            # Add neighbors to queue
            for neighbor in adjacency[vertex]:
                if neighbor not in visited:
                    queue.append(neighbor)

        islands.append(island)

    return islands


def classify_islands(islands, num_vertices, small_threshold=0.05):
    """
    Classify islands as small or large based on size threshold.

    Args:
        islands: List of island vertex sets
        num_vertices: Total vertex count
        small_threshold: Max % of mesh to qualify as small (default: 5%)

    Returns:
        (small_islands, large_islands) tuple of lists
    """
    max_small_size = int(num_vertices * small_threshold)

    small_islands = []
    large_islands = []

    for island in islands:
        if len(island) <= max_small_size:
            small_islands.append(island)
        else:
            large_islands.append(island)

    return small_islands, large_islands


def get_island_match_coverage(island, matched_indices):
    """
    Calculate what % of an island has matched vertices.

    Args:
        island: Set of vertex indices
        matched_indices: Array of matched vertex indices

    Returns:
        Match coverage ratio (0.0 to 1.0)
    """
    if len(island) == 0:
        return 0.0

    matched_set = set(matched_indices)
    island_matched = island & matched_set

    return len(island_matched) / len(island)


def copy_nearest_displacement_to_island(
    island,
    target_verts,
    matched_indices,
    matched_displacements
):
    """
    Copy displacement from nearest matched vertex to entire island.

    Strategy: Find the matched vertex closest to the island's centroid,
    then apply its displacement to all vertices in the island.

    Args:
        island: Set of vertex indices in the island
        target_verts: Target mesh vertices (Nx3)
        matched_indices: Indices of matched vertices
        matched_displacements: Displacements for matched vertices (Mx3)

    Returns:
        Array of displacements for the island vertices
    """
    island_list = list(island)

    # Compute island centroid
    island_verts = target_verts[island_list]
    centroid = np.mean(island_verts, axis=0)

    # Find nearest matched vertex to centroid
    matched_verts = target_verts[matched_indices]
    distances = np.linalg.norm(matched_verts - centroid, axis=1)
    nearest_idx = np.argmin(distances)

    # Get displacement of nearest matched vertex
    nearest_displacement = matched_displacements[nearest_idx]

    # Apply same displacement to all island vertices
    island_displacements = np.tile(nearest_displacement, (len(island), 1))

    return island_list, island_displacements


def handle_small_islands(
    target_verts,
    target_faces,
    matched_indices,
    matched_displacements,
    small_island_threshold=0.05,
    min_match_coverage=0.1
):
    """
    Detect and handle small mesh islands with poor match coverage.

    This is the main entry point for island handling. It:
    1. Detects disconnected mesh components
    2. Identifies small islands with low match coverage
    3. Copies nearest matched displacement to those islands

    Args:
        target_verts: Target mesh vertices (Nx3)
        target_faces: Target mesh faces (Fx3)
        matched_indices: Indices of matched vertices
        matched_displacements: Displacements for matched vertices
        small_island_threshold: Max % to qualify as small island (default: 5%)
        min_match_coverage: Min % matches to avoid special handling (default: 10%)

    Returns:
        Dictionary mapping vertex indices to displacement vectors for
        small islands that need special handling
    """
    num_vertices = len(target_verts)

    # Detect all mesh islands
    islands = detect_mesh_islands(target_faces, num_vertices)

    # Classify by size
    small_islands, large_islands = classify_islands(
        islands, num_vertices, small_island_threshold
    )

    print(f"ISLAND DETECTION: Found {len(islands)} components "
          f"({len(small_islands)} small, {len(large_islands)} large)")

    # Find small islands with poor match coverage
    island_displacements = {}

    for island in small_islands:
        coverage = get_island_match_coverage(island, matched_indices)

        if coverage < min_match_coverage:
            print(f"  Small island ({len(island)} verts) with {coverage*100:.1f}% matches "
                  f"- copying nearest displacement")

            # Copy displacement from nearest matched vertex
            island_verts, displacements = copy_nearest_displacement_to_island(
                island, target_verts, matched_indices, matched_displacements
            )

            # Add to result dictionary
            for vert_idx, displacement in zip(island_verts, displacements):
                island_displacements[vert_idx] = displacement

    return island_displacements
