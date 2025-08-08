# Naming Utilities - SIMPLIFIED VERSION
# Simple suffix logic only

import bpy


def detect_axis_from_selection():
    """Detect primary axis from selected objects - SIMPLIFIED"""
    selected_objects = bpy.context.selected_objects
    
    if not selected_objects:
        return 'X'  # Default fallback
    
    # Simple heuristic: check object names for L/R indicators
    for obj in selected_objects:
        name_lower = obj.name.lower()
        if any(indicator in name_lower for indicator in ['.l', '_l', 'left', '.r', '_r', 'right']):
            return 'X'  # Left/Right detected
        elif any(indicator in name_lower for indicator in ['.f', '_f', 'front', '.b', '_b', 'back']):
            return 'Y'  # Front/Back detected
        elif any(indicator in name_lower for indicator in ['.u', '_u', 'up', '.d', '_d', 'down']):
            return 'Z'  # Up/Down detected
    
    # Default to X-axis if no clear indicators
    return 'X'


def get_opposite_name(name, axis='X'):
    """Get opposite name using simple suffix logic"""
    if not name:
        return name
    
    name_lower = name.lower()
    
    # Simple word replacement first
    if axis == 'X':
        if 'right' in name_lower:
            return name.lower().replace('right', 'left').title()
        elif 'left' in name_lower:
            return name.lower().replace('left', 'right').title()
    
    # Simple suffix logic
    suffix_maps = {
        'X': {'.l': '.r', '.r': '.l', '_l': '_r', '_r': '_l'},
        'Y': {'.f': '.b', '.b': '.f', '_f': '_b', '_b': '_f'},
        'Z': {'.u': '.d', '.d': '.u', '_u': '_d', '_d': '_u'}
    }
    
    if axis in suffix_maps:
        for old_suffix, new_suffix in suffix_maps[axis].items():
            if name_lower.endswith(old_suffix):
                return name[:-len(old_suffix)] + new_suffix
    
    # If no pattern found, just add default suffix
    default_suffixes = {'X': '.L', 'Y': '.B', 'Z': '.D'}
    return name + default_suffixes.get(axis, '.L')


def increment_name(name):
    """Add incremental suffix if name already exists"""
    if not name:
        return name
    
    base_name = name
    counter = 1
    
    # Try common Blender incremental patterns
    while bpy.data.objects.get(base_name):
        base_name = f"{name}.{counter:03d}"
        counter += 1
        
        # Safety limit
        if counter > 999:
            break
    
    return base_name


# Legacy function stubs for compatibility
def detect_naming_pattern(name, axis='X'):
    """Legacy function - returns simple pattern info"""
    if not name:
        return None, None, axis
    
    name_lower = name.lower()
    
    # Check for simple suffixes
    suffix_patterns = {
        'X': ['.l', '.r', '_l', '_r'],
        'Y': ['.f', '.b', '_f', '_b'], 
        'Z': ['.u', '.d', '_u', '_d']
    }
    
    for check_axis, patterns in suffix_patterns.items():
        for pattern in patterns:
            if name_lower.endswith(pattern):
                opposite_pattern = get_opposite_suffix(pattern)
                return pattern, opposite_pattern, check_axis
    
    return None, None, axis


def get_opposite_suffix(suffix):
    """Get opposite suffix"""
    opposites = {
        '.l': '.r', '.r': '.l',
        '_l': '_r', '_r': '_l',
        '.f': '.b', '.b': '.f',
        '_f': '_b', '_b': '_f',
        '.u': '.d', '.d': '.u',
        '_u': '_d', '_d': '_u'
    }
    return opposites.get(suffix.lower(), suffix)