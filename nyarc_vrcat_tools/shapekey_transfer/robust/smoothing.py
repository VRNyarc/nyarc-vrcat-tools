"""
Optional Post-Smoothing
Iterative smoothing for unmatched vertices (usually unnecessary with inpainting)
"""

import numpy as np


def smooth_unmatched_vertices(displacements, vertices, matched_mask, adjacency, iterations=3):
    """
    Apply iterative smoothing to unmatched vertices only.

    Args:
        displacements: (N, 3) current displacement field
        vertices: (N, 3) mesh coordinates (for edge length weighting)
        matched_mask: (N,) boolean, True = matched vertex (fixed)
        adjacency: dict of neighbor lists
        iterations: Number of smoothing passes

    Returns:
        smoothed_displacements: (N, 3) updated field
    """
    result = displacements.copy()
    unmatched_indices = np.where(~matched_mask)[0]

    for iteration in range(iterations):
        for i in unmatched_indices:
            neighbors = adjacency.get(i, [])

            if len(neighbors) == 0:
                continue

            # Compute edge-length weights
            weights = []
            neighbor_displacements = []

            for j in neighbors:
                edge_length = np.linalg.norm(vertices[i] - vertices[j])
                weight = 1.0 / (1.0 + edge_length)
                weights.append(weight)
                neighbor_displacements.append(result[j])

            # Weighted average
            weights = np.array(weights)
            weights /= weights.sum()

            result[i] = sum(w * d for w, d in zip(weights, neighbor_displacements))

    return result
