# Detection Utilities - SIMPLIFIED VERSION
# Basic mesh-armature relationships only

import bpy


def detect_mesh_armature_relationships():
    """Detect relationships between selected meshes and armatures - SIMPLIFIED"""
    relationships = {}
    
    selected_objects = bpy.context.selected_objects
    mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
    
    for mesh_obj in mesh_objects:
        mesh_relationships = []
        
        # Check armature modifiers
        for modifier in mesh_obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object:
                armature_obj = modifier.object
                mesh_relationships.append({
                    'armature': armature_obj,
                    'modifier': modifier,
                    'type': 'modifier'
                })
        
        # Check parent relationships
        if mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
            mesh_relationships.append({
                'armature': mesh_obj.parent,
                'modifier': None,
                'type': 'parent'
            })
        
        if mesh_relationships:
            relationships[mesh_obj.name] = mesh_relationships
    
    return relationships


def auto_detect_flip_candidates():
    """Auto-detect objects for flipping - SIMPLIFIED"""
    candidates = {
        'meshes': [],
        'bones': [],
        'relationships': {}
    }
    
    # Get mesh-armature relationships
    relationships = detect_mesh_armature_relationships()
    candidates['relationships'] = relationships
    
    # Simply add all selected meshes as candidates
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    for mesh_obj in selected_meshes:
        candidates['meshes'].append(mesh_obj.name)
    
    # Note: Bone detection is now handled by chain_analysis.py
    
    return candidates