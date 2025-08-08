# Validation utilities for Shape Key Transfer
# Handles mesh validation and compatibility checking

import bpy
import bmesh


def validate_mesh_for_surface_deform(obj):
    """
    Validate if a mesh is suitable for surface deform operations.
    
    Args:
        obj: Blender mesh object to validate
        
    Returns:
        tuple: (is_compatible: bool, issues: list[str])
    """
    
    if not obj or obj.type != 'MESH':
        return False, ["Object is not a mesh"]
    
    if not obj.data:
        return False, ["Mesh has no data"]
    
    issues = []
    is_compatible = True
    
    try:
        # Create bmesh for analysis
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        
        # Check for faces that could cause Surface Deform issues
        # N-gons (faces with more than 4 vertices)
        ngons = [face for face in bm.faces if len(face.verts) > 4]
        if ngons:
            issues.append(f"Found {len(ngons)} N-gons (faces with >4 vertices)")
            is_compatible = False
        
        # All non-triangles (quads and N-gons) - Surface Deform works best with triangles
        non_triangles = [face for face in bm.faces if len(face.verts) > 3]
        if non_triangles:
            issues.append(f"Found {len(non_triangles)} non-triangle faces (may cause concave polygon issues)")
            is_compatible = False
        
        # Check for non-manifold edges
        non_manifold_edges = [edge for edge in bm.edges if not edge.is_manifold]
        if non_manifold_edges:
            issues.append(f"Found {len(non_manifold_edges)} non-manifold edges")
            is_compatible = False
        
        # Check for degenerate faces (zero area)
        degenerate_faces = [face for face in bm.faces if face.calc_area() < 1e-6]
        if degenerate_faces:
            issues.append(f"Found {len(degenerate_faces)} degenerate faces")
            is_compatible = False
        
        # Check for loose vertices
        loose_verts = [vert for vert in bm.verts if not vert.link_edges]
        if loose_verts:
            issues.append(f"Found {len(loose_verts)} loose vertices")
            # This is a warning, not necessarily incompatible
        
        bm.free()
        
        # Check vertex count (Surface Deform has practical limits)
        vert_count = len(obj.data.vertices)
        if vert_count > 100000:
            issues.append(f"High vertex count ({vert_count}) may cause performance issues")
        elif vert_count < 3:
            issues.append("Insufficient vertices for shape key transfer")
            is_compatible = False
        
        if is_compatible and not issues:
            issues.append("Mesh is compatible")
            
    except Exception as e:
        is_compatible = False
        issues.append(f"Validation error: {str(e)[:50]}")
    
    return is_compatible, issues


def get_classes():
    """Get all validation classes for registration (none for validation)"""
    return []