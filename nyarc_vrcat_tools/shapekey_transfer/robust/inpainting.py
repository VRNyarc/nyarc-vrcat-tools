"""
Harmonic Inpainting (Stage 2)
Smooth interpolation of missing displacements using Laplacian energy minimization
"""

import numpy as np


def inpaint_displacements(
    target_verts, target_faces,
    matched_indices, matched_displacements,
    use_pointcloud=False
):
    """
    Inpaint missing displacements using harmonic energy minimization.

    Args:
        target_verts: (N, 3) target vertex coordinates
        target_faces: (F, 3) triangle indices
        matched_indices: (K,) indices of vertices with known displacements
        matched_displacements: (K, 3) known displacement vectors
        use_pointcloud: Use point cloud Laplacian (fallback for disconnected meshes)

    Returns:
        full_displacements: (N, 3) complete displacement field
    """
    try:
        import scipy.sparse as sp
        from scipy.sparse.linalg import spsolve

        N = len(target_verts)

        # Build Laplacian matrix
        print("Building Laplacian matrix...")
        if use_pointcloud:
            L, M = build_pointcloud_laplacian(target_verts)
        else:
            try:
                L, M = build_mesh_laplacian(target_verts, target_faces)
            except Exception as e:
                print(f"Mesh Laplacian failed: {e}, falling back to point cloud")
                L, M = build_pointcloud_laplacian(target_verts)

        # Build energy matrix Q = L^T M^(-1) L
        print("Constructing biharmonic energy matrix...")
        M_diag = M.diagonal()
        M_inv_diag = 1.0 / M_diag
        M_inv = sp.diags(M_inv_diag)

        Q = L.T @ M_inv @ L

        # Solve for each axis independently
        result = np.zeros((N, 3))

        for axis in range(3):
            print(f"Solving for {'XYZ'[axis]} axis...")

            known_values = matched_displacements[:, axis]

            try:
                result[:, axis] = solve_constrained_harmonic(
                    Q, matched_indices, known_values
                )
            except Exception as e:
                print(f"WARNING: Solve failed for axis {axis}: {e}")
                # Fallback: just use known values, zero elsewhere
                result[matched_indices, axis] = known_values

        return result

    except ImportError as e:
        print(f"ERROR: Missing scipy library: {e}")
        return None


def build_mesh_laplacian(vertices, faces):
    """
    Build cotangent Laplacian using robust-laplacian library.

    Returns:
        L: (N, N) Laplacian matrix (sparse)
        M: (N, N) mass matrix (sparse diagonal)
    """
    try:
        import robust_laplacian

        # Use robust-laplacian for geometry-aware weights
        L, M = robust_laplacian.mesh_laplacian(vertices, faces)

        # Negate for libigl convention
        L = -L

        return L, M

    except ImportError:
        print("WARNING: robust-laplacian not available, using simple Laplacian")
        return build_simple_mesh_laplacian(vertices, faces)


def build_simple_mesh_laplacian(vertices, faces):
    """
    Build simple uniform Laplacian (fallback if robust-laplacian unavailable).
    """
    import scipy.sparse as sp

    N = len(vertices)

    # Build adjacency from faces
    edges = set()
    for face in faces:
        edges.add((min(face[0], face[1]), max(face[0], face[1])))
        edges.add((min(face[1], face[2]), max(face[1], face[2])))
        edges.add((min(face[2], face[0]), max(face[2], face[0])))

    # Count neighbors
    valence = np.zeros(N)
    for i, j in edges:
        valence[i] += 1
        valence[j] += 1

    # Build Laplacian
    row = []
    col = []
    data = []

    for i, j in edges:
        # Off-diagonal: -1
        row.extend([i, j])
        col.extend([j, i])
        data.extend([-1.0, -1.0])

    # Diagonal: valence
    for i in range(N):
        row.append(i)
        col.append(i)
        data.append(valence[i])

    L = sp.csr_matrix((data, (row, col)), shape=(N, N))

    # Uniform mass matrix
    M = sp.identity(N)

    return L, M


def build_pointcloud_laplacian(vertices):
    """
    Build point cloud Laplacian using robust-laplacian library.
    More robust for disconnected components, but slower and less accurate.
    """
    try:
        import robust_laplacian

        L, M = robust_laplacian.point_cloud_laplacian(vertices)

        # Negate for libigl convention
        L = -L

        return L, M

    except ImportError:
        print("ERROR: robust-laplacian required for point cloud Laplacian")
        raise


def solve_constrained_harmonic(Q, known_indices, known_values):
    """
    Solve constrained quadratic problem: minimize x^T Q x subject to x[known] = known_values.

    Uses Schur complement method to eliminate constrained variables.
    """
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve

    N = Q.shape[0]

    # Separate known and unknown indices
    all_indices = np.arange(N)
    unknown_mask = np.ones(N, dtype=bool)
    unknown_mask[known_indices] = False
    unknown_indices = all_indices[unknown_mask]

    if len(unknown_indices) == 0:
        # All vertices matched - just return known values
        result = np.zeros(N)
        result[known_indices] = known_values
        return result

    # Extract submatrices
    # Q = [Q_uu  Q_uk]
    #     [Q_ku  Q_kk]
    Q_uu = Q[unknown_indices, :][:, unknown_indices]
    Q_uk = Q[unknown_indices, :][:, known_indices]

    # Right-hand side: -Q_uk * known_values
    rhs = -Q_uk @ known_values

    # Solve Q_uu * x_u = rhs
    x_unknown = spsolve(Q_uu, rhs)

    # Reconstruct full solution
    result = np.zeros(N)
    result[known_indices] = known_values
    result[unknown_indices] = x_unknown

    return result
