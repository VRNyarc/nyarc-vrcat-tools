# Post-Transfer Boundary Smoothing Utilities
# Weight-based approach: Generate editable vertex group mask, then apply smoothing

import bpy
import bmesh
from mathutils import Vector


def blur_vertex_group_weights(target_obj, vertex_group_name, blur_iterations=2):
    """
    Apply blur/smoothing to vertex group weights for softer transitions.

    Args:
        target_obj: Target mesh object
        vertex_group_name: Name of vertex group to blur
        blur_iterations: Number of blur passes (1-5)

    Returns:
        bool: True if blur was applied, False if failed
    """
    if not target_obj or target_obj.type != 'MESH':
        print(f"[Blur Weights] Error: Invalid target object")
        return False

    vgroup = target_obj.vertex_groups.get(vertex_group_name)
    if not vgroup:
        print(f"[Blur Weights] Error: Vertex group '{vertex_group_name}' not found")
        return False

    print(f"[Blur Weights] Applying {blur_iterations} blur iterations to '{vertex_group_name}'...")

    bm = bmesh.new()
    bm.from_mesh(target_obj.data)
    bm.verts.ensure_lookup_table()

    try:
        for iteration in range(blur_iterations):
            # Read current weights
            current_weights = {}
            for vert in bm.verts:
                try:
                    weight = vgroup.weight(vert.index)
                    current_weights[vert.index] = weight
                except RuntimeError:
                    current_weights[vert.index] = 0.0

            # Calculate blurred weights
            blurred_weights = {}
            for vert in bm.verts:
                current_weight = current_weights.get(vert.index, 0.0)
                neighbor_sum = 0.0
                neighbor_count = 0

                # Add neighbors
                for edge in vert.link_edges:
                    neighbor = edge.other_vert(vert)
                    neighbor_sum += current_weights.get(neighbor.index, 0.0)
                    neighbor_count += 1

                # Blend current with average of neighbors (60% current, 40% neighbors for smoother transitions)
                if neighbor_count > 0:
                    avg_neighbor = neighbor_sum / neighbor_count
                    blurred_weights[vert.index] = current_weight * 0.6 + avg_neighbor * 0.4
                else:
                    # No neighbors (isolated vertex) - keep current weight
                    blurred_weights[vert.index] = current_weight

            # Apply blurred weights back to vertex group
            for vert_idx, weight in blurred_weights.items():
                vgroup.add([vert_idx], weight, 'REPLACE')

            print(f"[Blur Weights] Completed blur iteration {iteration + 1}/{blur_iterations}")

        print(f"[Blur Weights] Successfully blurred '{vertex_group_name}'")
        return True

    except Exception as e:
        print(f"[Blur Weights] Error during blur: {e}")
        return False

    finally:
        bm.free()


def generate_smoothing_weights(target_obj, shape_key_name, boundary_width=3, displacement_threshold=0.001, auto_blur=True, blur_iterations=2, island_threshold=0.05, partial_island_mode='NONE'):
    """
    Generate a vertex group mask showing where smoothing should be applied.

    Creates a vertex group with weights:
    - 1.0 (red) = Boundary vertices requiring smoothing
    - 0.5-0.8 (orange/yellow) = Transition rings
    - 0.0 (blue) = Moved vertices (preserve exact displacement) + far unmoved (no change)

    User can then edit this mask in Weight Paint mode before applying smoothing.

    Args:
        target_obj: Target mesh object with shape keys
        shape_key_name: Name of the shape key to analyze
        boundary_width: Number of vertex rings to expand boundary (1-5)
        displacement_threshold: Minimum displacement to consider "moved" (default: 0.001)
        auto_blur: Automatically blur the mask after generation (default: True)
        blur_iterations: Number of blur passes if auto_blur is enabled (default: 2)
        island_threshold: Max island size as percentage of unmoved verts (default: 0.05 = 5%)
        partial_island_mode: 'NONE', 'EXCLUDE', or 'AVERAGE' - controls island detection

    Returns:
        str: Name of created vertex group, or None if failed
    """

    if not target_obj or target_obj.type != 'MESH':
        print(f"[Smoothing Mask] Error: Invalid target object")
        return None

    # Check if object has shape keys
    if not target_obj.data.shape_keys or not target_obj.data.shape_keys.key_blocks:
        print(f"[Smoothing Mask] Error: Target object has no shape keys")
        return None

    # Get the shape key
    shape_key = target_obj.data.shape_keys.key_blocks.get(shape_key_name)
    if not shape_key:
        print(f"[Smoothing Mask] Error: Shape key '{shape_key_name}' not found")
        return None

    # Get basis shape key
    basis_key = target_obj.data.shape_keys.key_blocks.get("Basis")
    if not basis_key:
        print(f"[Smoothing Mask] Error: Basis shape key not found")
        return None

    print(f"[Smoothing Mask] Analyzing displacement for '{shape_key_name}'...")

    # Create vertex group name
    vgroup_name = f"Smooth_{shape_key_name}"

    # Remove existing vertex group if it exists
    if vgroup_name in target_obj.vertex_groups:
        target_obj.vertex_groups.remove(target_obj.vertex_groups[vgroup_name])

    # Create new vertex group
    vgroup = target_obj.vertex_groups.new(name=vgroup_name)

    # Create BMesh from target mesh
    bm = bmesh.new()
    bm.from_mesh(target_obj.data)
    bm.verts.ensure_lookup_table()

    try:
        # Step 1: Calculate displacement for each vertex
        moved_verts = set()
        unmoved_verts = set()

        for i, vert in enumerate(bm.verts):
            basis_pos = Vector(basis_key.data[i].co)
            shape_pos = Vector(shape_key.data[i].co)
            displacement = (shape_pos - basis_pos).length

            if displacement > displacement_threshold:
                moved_verts.add(vert)
            else:
                unmoved_verts.add(vert)

        print(f"[Smoothing Mask] Found {len(moved_verts)} moved vertices, {len(unmoved_verts)} unmoved vertices")

        # Step 2: Find boundary vertices (unmoved adjacent to moved)
        boundary_verts = set()

        for vert in unmoved_verts:
            for edge in vert.link_edges:
                neighbor = edge.other_vert(vert)
                if neighbor in moved_verts:
                    boundary_verts.add(vert)
                    break

        if not boundary_verts:
            print(f"[Smoothing Mask] No boundary detected - creating empty vertex group")
            bm.free()
            return vgroup_name

        print(f"[Smoothing Mask] Found {len(boundary_verts)} boundary vertices")

        # Step 3: Detect mesh islands in unmoved area (buttons, pockets, etc.)
        # Only do island detection if partial_island_mode is not NONE
        excluded_island_verts = set()

        if partial_island_mode != 'NONE':
            def get_connected_component(start_vert, region_verts):
                """Find all vertices connected to start_vert within region_verts"""
                visited = set()
                stack = [start_vert]

                while stack:
                    vert = stack.pop()
                    if vert in visited:
                        continue

                    visited.add(vert)

                    # Add connected neighbors that are in the region
                    for edge in vert.link_edges:
                        neighbor = edge.other_vert(vert)
                        if neighbor in region_verts and neighbor not in visited:
                            stack.append(neighbor)

                return visited

            # Find all islands in unmoved region
            islands = []
            unprocessed = unmoved_verts.copy()

            while unprocessed:
                start_vert = next(iter(unprocessed))
                island = get_connected_component(start_vert, unmoved_verts)
                islands.append(island)
                unprocessed -= island

            print(f"[Smoothing Mask] Detected {len(islands)} mesh islands in unmoved region")

            # Step 4: Identify small isolated islands (buttons, pockets) - exclude completely
            # Only exclude islands < island_threshold % of unmoved vertices to avoid false positives (neck, etc.)
            for island in islands:
                # Very small islands (< threshold % of unmoved) are likely buttons/decorations
                if len(island) < len(unmoved_verts) * island_threshold:
                    excluded_island_verts.update(island)
                    print(f"[Smoothing Mask] Excluding small island: {len(island)} vertices (< {island_threshold*100}% threshold)")
        else:
            print(f"[Smoothing Mask] Island detection disabled (mode = NONE)")

        # Step 5: Assign weights - boundary vertices and expansion rings
        # Exclude small islands from ring expansion
        vertex_weights = {}

        # Boundary vertices get full weight (1.0 = red) - but not if they're in excluded islands
        for vert in boundary_verts:
            if vert not in excluded_island_verts:
                vertex_weights[vert.index] = 1.0

        # Expand rings with decreasing weights into unmoved area
        current_ring = boundary_verts - excluded_island_verts
        for ring_num in range(1, boundary_width + 1):
            next_ring = set()

            for vert in current_ring:
                for edge in vert.link_edges:
                    neighbor = edge.other_vert(vert)

                    # Only expand into unmoved vertices not yet assigned, and NOT in excluded islands
                    if (neighbor in unmoved_verts and
                        neighbor.index not in vertex_weights and
                        neighbor not in excluded_island_verts):
                        # Exponential falloff: Ring 1 = 0.44, Ring 2 = 0.11, Ring 3 = 0.03
                        weight = max(0.0, (1.0 - (ring_num / (boundary_width + 1))) ** 2)
                        vertex_weights[neighbor.index] = weight
                        next_ring.add(neighbor)

            current_ring = next_ring
            if not current_ring:
                break

        print(f"[Smoothing Mask] Assigned weights to {len(vertex_weights)} vertices (boundary + {boundary_width} rings)")
        print(f"[Smoothing Mask] Excluded {len(excluded_island_verts)} vertices in small islands")

        # Step 6: Apply weights to vertex group
        for vert_idx, weight in vertex_weights.items():
            vgroup.add([vert_idx], weight, 'REPLACE')

        print(f"[Smoothing Mask] Created vertex group '{vgroup_name}'")

        # Step 7: Auto-blur the mask if requested
        if auto_blur and blur_iterations > 0:
            blur_success = blur_vertex_group_weights(target_obj, vgroup_name, blur_iterations)
            if not blur_success:
                print(f"[Smoothing Mask] Warning: Auto-blur failed, but mask was created")

        return vgroup_name

    except Exception as e:
        print(f"[Smoothing Mask] Error during weight generation: {e}")
        return None

    finally:
        bm.free()


def apply_vertex_group_smoothing(target_obj, shape_key_name, vertex_group_name, smooth_iterations=3):
    """
    Apply Laplacian smoothing to a shape key based on vertex group weights.

    Vertices with higher weights get more smoothing applied.
    Vertices with weight 0.0 are unchanged.

    Args:
        target_obj: Target mesh object with shape keys
        shape_key_name: Name of the shape key to smooth
        vertex_group_name: Name of vertex group containing smoothing weights
        smooth_iterations: Number of Laplacian smoothing passes (1-10)

    Returns:
        bool: True if smoothing was applied, False if failed
    """

    if not target_obj or target_obj.type != 'MESH':
        print(f"[Apply Smoothing] Error: Invalid target object")
        return False

    # Check vertex group exists
    vgroup = target_obj.vertex_groups.get(vertex_group_name)
    if not vgroup:
        print(f"[Apply Smoothing] Error: Vertex group '{vertex_group_name}' not found")
        return False

    # Check shape keys
    if not target_obj.data.shape_keys or not target_obj.data.shape_keys.key_blocks:
        print(f"[Apply Smoothing] Error: Target object has no shape keys")
        return False

    shape_key = target_obj.data.shape_keys.key_blocks.get(shape_key_name)
    if not shape_key:
        print(f"[Apply Smoothing] Error: Shape key '{shape_key_name}' not found")
        return False

    basis_key = target_obj.data.shape_keys.key_blocks.get("Basis")
    if not basis_key:
        print(f"[Apply Smoothing] Error: Basis shape key not found")
        return False

    print(f"[Apply Smoothing] Applying smoothing to '{shape_key_name}' using vertex group '{vertex_group_name}'...")

    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(target_obj.data)
    bm.verts.ensure_lookup_table()

    try:
        # Step 1: Read vertex group weights
        vertex_weights = {}
        vgroup_index = vgroup.index

        for vert in bm.verts:
            try:
                weight = vgroup.weight(vert.index)
                if weight > 0.0:
                    vertex_weights[vert.index] = weight
            except RuntimeError:
                # Vertex not in group = weight 0.0
                pass

        if not vertex_weights:
            print(f"[Apply Smoothing] Warning: No vertices with weight > 0 in vertex group")
            bm.free()
            return False

        print(f"[Apply Smoothing] Found {len(vertex_weights)} vertices with smoothing weights")

        # Step 2: Calculate displacement vectors for all vertices
        displacement_vectors = {}
        for i in range(len(bm.verts)):
            basis_pos = Vector(basis_key.data[i].co)
            shape_pos = Vector(shape_key.data[i].co)
            displacement_vectors[i] = shape_pos - basis_pos

        # Step 3: Apply Laplacian smoothing iterations
        for iteration in range(smooth_iterations):
            smoothed_displacements = {}

            for vert in bm.verts:
                vert_idx = vert.index

                # Skip if no weight assigned
                if vert_idx not in vertex_weights:
                    continue

                weight = vertex_weights[vert_idx]

                # Calculate average displacement from neighbors
                neighbor_sum = Vector((0.0, 0.0, 0.0))
                neighbor_count = 0

                for edge in vert.link_edges:
                    neighbor = edge.other_vert(vert)
                    if neighbor.index in displacement_vectors:
                        neighbor_sum += displacement_vectors[neighbor.index]
                        neighbor_count += 1

                if neighbor_count > 0:
                    # Laplacian smoothing: blend current with neighbor average
                    avg_neighbor = neighbor_sum / neighbor_count
                    current = displacement_vectors[vert_idx]

                    # Blend ratio: 20% current, 80% neighbors (aggressive smoothing for better results)
                    smoothed = current * 0.2 + avg_neighbor * 0.8

                    # Interpolate between original and smoothed based on weight
                    # Weight 1.0 = full smoothing, Weight 0.0 = no change
                    # Use sqrt curve to make weights more effective while preserving control
                    effective_weight = weight ** 0.5  # Less aggressive power curve
                    final_displacement = current.lerp(smoothed, effective_weight)

                    smoothed_displacements[vert_idx] = final_displacement

            # Update displacement vectors
            displacement_vectors.update(smoothed_displacements)

            print(f"[Apply Smoothing] Completed iteration {iteration + 1}/{smooth_iterations}")

        # Step 4: Reconstruct shape key positions from smoothed displacement vectors
        for vert_idx in vertex_weights.keys():
            basis_pos = Vector(basis_key.data[vert_idx].co)
            new_shape_pos = basis_pos + displacement_vectors[vert_idx]
            shape_key.data[vert_idx].co = new_shape_pos

        print(f"[Apply Smoothing] Successfully applied {smooth_iterations} smoothing iterations")

        # Update mesh data
        target_obj.data.update()

        return True

    except Exception as e:
        print(f"[Apply Smoothing] Error during smoothing: {e}")
        return False

    finally:
        bm.free()


def process_partially_moved_islands(target_obj, shape_key_name, mode='EXCLUDE', displacement_threshold=0.001, island_threshold=0.05):
    """
    Detect and process small mesh islands that are partially moved.

    This prevents mesh destruction on small details (buttons, pockets, etc.) where
    only part of the island gets deformed, creating ugly cutoffs.

    Args:
        target_obj: Target mesh object with shape keys
        shape_key_name: Name of the shape key to analyze
        mode: 'EXCLUDE' (reset to basis) or 'AVERAGE' (uniform displacement)
        displacement_threshold: Minimum displacement to consider "moved" (default: 0.001)
        island_threshold: Max island size as percentage of total mesh (default: 0.05 = 5%)

    Returns:
        tuple: (int: number of islands processed, set: vertex indices processed in AVERAGE mode)
               Returns (count, set()) if mode != AVERAGE
               Returns (-1, set()) if failed
    """

    if not target_obj or target_obj.type != 'MESH':
        print(f"[Island Exclusion] Error: Invalid target object")
        return (-1, set())

    # Check shape keys
    if not target_obj.data.shape_keys or not target_obj.data.shape_keys.key_blocks:
        print(f"[Island Exclusion] Error: Target object has no shape keys")
        return (-1, set())

    shape_key = target_obj.data.shape_keys.key_blocks.get(shape_key_name)
    if not shape_key:
        print(f"[Island Exclusion] Error: Shape key '{shape_key_name}' not found")
        return (-1, set())

    basis_key = target_obj.data.shape_keys.key_blocks.get("Basis")
    if not basis_key:
        print(f"[Island Exclusion] Error: Basis shape key not found")
        return (-1, set())

    mode_text = "Excluding" if mode == 'EXCLUDE' else "Averaging"
    print(f"[Island Processing] {mode_text} partially moved islands in '{shape_key_name}'...")

    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(target_obj.data)
    bm.verts.ensure_lookup_table()

    try:
        # Step 1: Calculate displacement for each vertex
        moved_verts = set()
        unmoved_verts = set()

        for i, vert in enumerate(bm.verts):
            basis_pos = Vector(basis_key.data[i].co)
            shape_pos = Vector(shape_key.data[i].co)
            displacement = (shape_pos - basis_pos).length

            if displacement > displacement_threshold:
                moved_verts.add(vert)
            else:
                unmoved_verts.add(vert)

        print(f"[Island Processing] Found {len(moved_verts)} moved, {len(unmoved_verts)} unmoved vertices")

        # Step 2: Find all mesh islands
        def get_connected_component(start_vert, all_verts):
            """Find all vertices connected to start_vert"""
            visited = set()
            stack = [start_vert]

            while stack:
                vert = stack.pop()
                if vert in visited:
                    continue

                visited.add(vert)

                for edge in vert.link_edges:
                    neighbor = edge.other_vert(vert)
                    if neighbor in all_verts and neighbor not in visited:
                        stack.append(neighbor)

            return visited

        # Find all islands in the entire mesh
        all_verts = set(bm.verts)
        islands = []
        unprocessed = all_verts.copy()

        while unprocessed:
            start_vert = next(iter(unprocessed))
            island = get_connected_component(start_vert, all_verts)
            islands.append(island)
            unprocessed -= island

        print(f"[Island Processing] Detected {len(islands)} mesh islands total")

        # Step 3: Find and process partially moved islands
        processed_count = 0
        processed_verts = set()  # BMesh verts for tracking
        averaged_vert_indices = set()  # Vertex indices for AVERAGE mode (for mask painting)

        for island in islands:
            # Count how many vertices in this island are moved vs unmoved
            island_moved = island & moved_verts
            island_unmoved = island & unmoved_verts

            moved_count = len(island_moved)
            unmoved_count = len(island_unmoved)
            total_count = len(island)

            # Skip large islands (> threshold % of total mesh)
            if total_count > len(bm.verts) * island_threshold:
                continue

            # Check if island is partially moved (both moved and unmoved vertices exist)
            if moved_count > 0 and unmoved_count > 0:
                # Calculate percentage moved
                moved_percentage = moved_count / total_count

                # If island is small and partially moved (not fully moved), process it
                # We only process if less than 80% of vertices are moved
                if moved_percentage < 0.8:
                    processed_verts.update(island)
                    processed_count += 1

                    if mode == 'EXCLUDE':
                        # Mode 1: Reset entire island to basis (no deformation)
                        for vert in island:
                            basis_pos = Vector(basis_key.data[vert.index].co)
                            shape_key.data[vert.index].co = basis_pos
                        print(f"[Island Processing] Excluded island: {total_count} verts, {moved_percentage*100:.1f}% moved")

                    elif mode == 'AVERAGE':
                        # Mode 2: Calculate average displacement from MOVED vertices only
                        # Then apply that average to ALL vertices in the island
                        total_displacement = Vector((0.0, 0.0, 0.0))
                        moved_in_island = island & moved_verts

                        # Calculate average from moved vertices only
                        for vert in moved_in_island:
                            basis_pos = Vector(basis_key.data[vert.index].co)
                            shape_pos = Vector(shape_key.data[vert.index].co)
                            displacement = shape_pos - basis_pos
                            total_displacement += displacement

                        # If there are moved vertices, calculate average and apply to entire island
                        if len(moved_in_island) > 0:
                            avg_displacement = total_displacement / len(moved_in_island)

                            # Apply average displacement to ALL vertices in island (moved and unmoved)
                            for vert in island:
                                basis_pos = Vector(basis_key.data[vert.index].co)
                                new_pos = basis_pos + avg_displacement
                                shape_key.data[vert.index].co = new_pos
                                # Store vertex index for mask painting
                                averaged_vert_indices.add(vert.index)

                            print(f"[Island Processing] Averaged island: {total_count} verts total, {len(moved_in_island)} moved, avg displacement: {avg_displacement.length:.4f}")
                        else:
                            print(f"[Island Processing] WARNING: Island has no moved vertices (shouldn't happen)")

        # Step 4: Report results
        if processed_verts:
            mode_verb = "Excluded" if mode == 'EXCLUDE' else "Averaged"
            print(f"[Island Processing] {mode_verb} {processed_count} partially moved islands ({len(processed_verts)} vertices)")
            if mode == 'AVERAGE' and averaged_vert_indices:
                print(f"[Island Processing] Returning {len(averaged_vert_indices)} vertex indices for mask painting")
            target_obj.data.update()
        else:
            print(f"[Island Processing] No partially moved islands found")

        return (processed_count, averaged_vert_indices)

    except Exception as e:
        print(f"[Island Processing] Error: {e}")
        return (-1, set())

    finally:
        bm.free()


def paint_averaged_islands_in_mask(target_obj, shape_key_name, averaged_vert_indices, weight=0.0):
    """
    Paint averaged island vertices into the smoothing mask.

    When AVERAGE mode moves islands uniformly, they need to be marked in the mask
    so they can be smoothed if desired.

    Args:
        target_obj: Target mesh object
        shape_key_name: Name of the shape key
        averaged_vert_indices: Set of vertex indices that were averaged
        weight: Weight to paint (0.0 = blue/preserved, 1.0 = red/smoothed)

    Returns:
        bool: True if successful, False otherwise
    """
    if not averaged_vert_indices:
        return False

    vgroup_name = f"Smooth_{shape_key_name}"
    vgroup = target_obj.vertex_groups.get(vgroup_name)

    if not vgroup:
        print(f"[Mask Painting] WARNING: Smoothing mask '{vgroup_name}' not found")
        return False

    # Paint the averaged vertices with the specified weight
    for vert_idx in averaged_vert_indices:
        vgroup.add([vert_idx], weight, 'REPLACE')

    print(f"[Mask Painting] Painted {len(averaged_vert_indices)} averaged island vertices with weight {weight}")
    return True


def get_classes():
    """Get all boundary smoothing classes for registration"""
    return []
