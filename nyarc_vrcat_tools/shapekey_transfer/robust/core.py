"""
Robust Shape Key Transfer - Core Pipeline
Main entry point for harmonic inpainting-based transfer
"""

import bpy
import numpy as np

from .mesh_data import (
    extract_shape_key_displacements,
    get_mesh_data_world_space,
    apply_shape_key_to_mesh
)
from .correspondence import find_geometric_correspondence
from .inpainting import inpaint_displacements
from .debug import create_match_quality_debug


def transfer_shape_key_robust(
    source_obj,
    target_obj,
    shape_key_name,
    distance_threshold=0.01,
    normal_threshold=0.5,
    use_pointcloud=False,
    smooth_iterations=0,
    show_debug=False,
    handle_islands=True,
    operator=None
):
    """
    Transfer shape key using robust harmonic inpainting.

    Args:
        source_obj: Blender object with shape keys
        target_obj: Blender object to receive shape key
        shape_key_name: Name of shape key to transfer
        distance_threshold: Maximum spatial distance for valid match (meters)
        normal_threshold: Minimum normal alignment (cosine, 0-1)
        use_pointcloud: Use point cloud Laplacian (slower, more robust)
        smooth_iterations: Additional smoothing passes (0 recommended)
        show_debug: Create vertex colors showing match quality
        handle_islands: Auto-enable Point Cloud Laplacian for islands with poor matches (default: True)
                        When enabled, detects disconnected islands and automatically uses
                        Point Cloud mode if they lack geometric correspondence
        operator: Blender operator for reporting (optional)

    Returns:
        bool: True if successful, False otherwise
    """

    def report(level, message):
        """Helper to report messages"""
        if operator:
            operator.report({level}, message)
        else:
            print(f"[{level}] {message}")

    try:
        report('INFO', "=== STAGE 1: GEOMETRIC CORRESPONDENCE ===")

        # Extract source shape key displacements
        report('INFO', f"Extracting shape key '{shape_key_name}' from {source_obj.name}...")
        source_displacements, source_basis = extract_shape_key_displacements(
            source_obj, shape_key_name
        )

        if source_displacements is None:
            report('ERROR', f"Failed to extract shape key '{shape_key_name}'")
            return False

        # Get mesh data in world space
        report('INFO', "Loading mesh geometry...")
        source_verts, source_faces, source_normals = get_mesh_data_world_space(source_obj)
        target_verts, target_faces, target_normals = get_mesh_data_world_space(target_obj)

        # Find geometric correspondence
        report('INFO', "Computing geometric correspondence...")
        result = find_geometric_correspondence(
            source_verts, source_faces, source_normals, source_displacements,
            target_verts, target_normals,
            distance_threshold, normal_threshold
        )

        if result is None:
            report('ERROR', "Failed to compute correspondence")
            return False

        matched_indices, matched_displacements, distances = result

        num_matched = len(matched_indices)
        match_percentage = 100.0 * num_matched / len(target_verts)
        report('INFO', f"Matched {num_matched}/{len(target_verts)} vertices ({match_percentage:.1f}%)")

        if num_matched == 0:
            report('ERROR', "No valid matches found! Try relaxing distance/normal thresholds")
            return False

        if match_percentage < 20.0:
            report('WARNING', f"Only {match_percentage:.1f}% matched - results may be poor")

        # Debug visualization
        if show_debug:
            report('INFO', "Creating match quality debug visualization...")
            create_match_quality_debug(target_obj, matched_indices, distances, distance_threshold)

        # STAGE 1.5: Handle disconnected islands with poor matches
        # Use Point Cloud Laplacian for islands instead of hard displacement override
        use_pointcloud_for_islands = use_pointcloud  # Start with user setting
        if handle_islands:
            report('INFO', "\n=== STAGE 1.5: MESH ISLAND HANDLING ===")
            try:
                from .island_handling import detect_mesh_islands, get_island_match_coverage

                islands = detect_mesh_islands(target_faces, len(target_verts))
                report('INFO', f"Found {len(islands)} mesh component(s)")

                # Check if any islands have poor coverage
                has_poor_islands = False
                for island in islands:
                    coverage = get_island_match_coverage(island, matched_indices)
                    if coverage < 0.1:
                        has_poor_islands = True
                        report('INFO', f"  Island with {len(island)} verts has {coverage*100:.1f}% matches")

                # Enable point cloud mode for disconnected components
                if has_poor_islands:
                    use_pointcloud_for_islands = True
                    report('INFO', "Enabling Point Cloud Laplacian for island handling")
                else:
                    report('INFO', "All islands have adequate match coverage")

            except Exception as e:
                report('WARNING', f"Island detection failed: {e}, continuing without island handling")
                import traceback
                traceback.print_exc()

        report('INFO', "\n=== STAGE 2: HARMONIC INPAINTING ===")

        # Inpaint missing displacements (use point cloud if islands need it)
        if use_pointcloud_for_islands and not use_pointcloud:
            report('INFO', "Using Point Cloud Laplacian for disconnected islands...")
        else:
            report('INFO', "Running harmonic inpainting...")

        full_displacements = inpaint_displacements(
            target_verts, target_faces,
            matched_indices, matched_displacements,
            use_pointcloud_for_islands
        )

        if full_displacements is None:
            report('ERROR', "Harmonic inpainting failed")
            return False

        # Optional post-smoothing
        if smooth_iterations > 0:
            report('INFO', f"Applying {smooth_iterations} post-smoothing iterations...")
            from .smoothing import smooth_unmatched_vertices
            adjacency = get_adjacency_list(target_faces, len(target_verts))
            matched_mask = np.zeros(len(target_verts), dtype=bool)
            matched_mask[matched_indices] = True

            full_displacements = smooth_unmatched_vertices(
                full_displacements, target_verts, matched_mask, adjacency, smooth_iterations
            )

        # Apply to target mesh
        report('INFO', f"Applying shape key to {target_obj.name}...")
        apply_shape_key_to_mesh(target_obj, shape_key_name, full_displacements)

        report('INFO', "Robust transfer complete!")
        return True

    except ImportError as e:
        report('ERROR', f"Missing dependency: {e}")
        report('ERROR', "Install required libraries: numpy, scipy, scikit-learn, robust-laplacian")
        return False

    except Exception as e:
        report('ERROR', f"Robust transfer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_adjacency_list(faces, num_vertices):
    """Build adjacency list from triangle connectivity"""
    adjacency = {i: set() for i in range(num_vertices)}

    for face in faces:
        a, b, c = face
        adjacency[a].update([b, c])
        adjacency[b].update([a, c])
        adjacency[c].update([a, b])

    return {k: list(v) for k, v in adjacency.items()}
