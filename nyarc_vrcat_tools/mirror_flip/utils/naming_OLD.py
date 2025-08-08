# Naming Convention Utilities
# Handles .L/.R naming conventions for bones and objects

import re

def detect_word_based_pattern(name, axis='X'):
    """Detect word-based naming patterns (Right/Left, Front/Back, etc.)"""
    name_lower = name.lower()
    
    if axis == 'X':  # Left/Right
        if 'right' in name_lower:
            return 'right', 'left', axis
        elif 'left' in name_lower:
            return 'left', 'right', axis
    elif axis == 'Y':  # Front/Back
        if 'front' in name_lower:
            return 'front', 'back', axis
        elif 'back' in name_lower:
            return 'back', 'front', axis
    elif axis == 'Z':  # Up/Down
        if 'upper' in name_lower or 'top' in name_lower:
            return 'upper', 'lower', axis
        elif 'lower' in name_lower or 'bottom' in name_lower:
            return 'lower', 'upper', axis
    
    return None, None, axis

def detect_naming_pattern(name, axis='X'):
    """Detect naming pattern based on mirror axis - checks both suffix and word-based patterns"""
    # First check for word-based patterns
    word_current, word_opposite, word_axis = detect_word_based_pattern(name, axis)
    
    axis_patterns = {
        'X': [  # Left/Right
            (r'\.L$', '.L', '.R'),      # bone.L -> bone.R
            (r'\.R$', '.R', '.L'),      # bone.R -> bone.L  
            (r'_L$', '_L', '_R'),       # bone_L -> bone_R
            (r'_R$', '_R', '_L'),       # bone_R -> bone_L
            (r'\.l$', '.l', '.r'),      # bone.l -> bone.r (lowercase)
            (r'\.r$', '.r', '.l'),      # bone.r -> bone.l (lowercase)
            (r'_l$', '_l', '_r'),       # bone_l -> bone_r (lowercase)
            (r'_r$', '_r', '_l'),       # bone_r -> bone_l (lowercase)
            (r'\.Left$', '.Left', '.Right'),    # bone.Left -> bone.Right
            (r'\.Right$', '.Right', '.Left'),   # bone.Right -> bone.Left
            (r'_Left$', '_Left', '_Right'),     # bone_Left -> bone_Right
            (r'_Right$', '_Right', '_Left'),    # bone_Right -> bone_Left
        ],
        'Y': [  # Front/Back
            (r'\.F$', '.F', '.B'),      # bone.F -> bone.B
            (r'\.B$', '.B', '.F'),      # bone.B -> bone.F
            (r'_F$', '_F', '_B'),       # bone_F -> bone_B
            (r'_B$', '_B', '_F'),       # bone_B -> bone_F
            (r'\.f$', '.f', '.b'),      # bone.f -> bone.b (lowercase)
            (r'\.b$', '.b', '.f'),      # bone.b -> bone.f (lowercase)
            (r'_f$', '_f', '_b'),       # bone_f -> bone_b (lowercase)
            (r'_b$', '_b', '_f'),       # bone_b -> bone_f (lowercase)
            (r'\.Front$', '.Front', '.Back'),   # bone.Front -> bone.Back
            (r'\.Back$', '.Back', '.Front'),    # bone.Back -> bone.Front
            (r'_Front$', '_Front', '_Back'),    # bone_Front -> bone_Back
            (r'_Back$', '_Back', '_Front'),     # bone_Back -> bone_Front
            (r'\.Fwd$', '.Fwd', '.Aft'),       # bone.Fwd -> bone.Aft
            (r'\.Aft$', '.Aft', '.Fwd'),       # bone.Aft -> bone.Fwd
        ],
        'Z': [  # Up/Down
            (r'\.U$', '.U', '.D'),      # bone.U -> bone.D
            (r'\.D$', '.D', '.U'),      # bone.D -> bone.U
            (r'_U$', '_U', '_D'),       # bone_U -> bone_D
            (r'_D$', '_D', '_U'),       # bone_D -> bone_U
            (r'\.u$', '.u', '.d'),      # bone.u -> bone.d (lowercase)
            (r'\.d$', '.d', '.u'),      # bone.d -> bone.u (lowercase)
            (r'_u$', '_u', '_d'),       # bone_u -> bone_d (lowercase)
            (r'_d$', '_d', '_u'),       # bone_d -> bone_u (lowercase)
            (r'\.Up$', '.Up', '.Down'), # bone.Up -> bone.Down
            (r'\.Down$', '.Down', '.Up'),   # bone.Down -> bone.Up
            (r'_Up$', '_Up', '_Down'),      # bone_Up -> bone_Down
            (r'_Down$', '_Down', '_Up'),    # bone_Down -> bone_Up
            (r'\.Top$', '.Top', '.Bot'),    # bone.Top -> bone.Bot
            (r'\.Bot$', '.Bot', '.Top'),    # bone.Bot -> bone.Top
            (r'\.Bottom$', '.Bottom', '.Top'),  # bone.Bottom -> bone.Top
            (r'_Top$', '_Top', '_Bot'),     # bone_Top -> bone_Bot
            (r'_Bot$', '_Bot', '_Top'),     # bone_Bot -> bone_Top
            (r'_Bottom$', '_Bottom', '_Top'),   # bone_Bottom -> bone_Top
            (r'\.Upper$', '.Upper', '.Lower'),  # bone.Upper -> bone.Lower
            (r'\.Lower$', '.Lower', '.Upper'),  # bone.Lower -> bone.Upper
            (r'_Upper$', '_Upper', '_Lower'),   # bone_Upper -> bone_Lower
            (r'_Lower$', '_Lower', '_Upper'),   # bone_Lower -> bone_Upper
        ]
    }
    
    patterns = axis_patterns.get(axis, axis_patterns['X'])
    
    # Check suffix patterns first
    for pattern, current, opposite in patterns:
        if re.search(pattern, name):
            return current, opposite, axis
    
    return None, None, axis

def detect_comprehensive_pattern(name, axis='X'):
    """Detect comprehensive naming pattern - returns both suffix and word patterns"""
    # Get word-based pattern
    word_current, word_opposite, word_axis = detect_word_based_pattern(name, axis)
    
    # Get suffix pattern  
    current_suffix, opposite_suffix, detected_axis = detect_naming_pattern(name, axis)
    
    return {
        'suffix_current': current_suffix,
        'suffix_opposite': opposite_suffix,
        'word_current': word_current,
        'word_opposite': word_opposite,
        'axis': axis,
        'has_suffix': current_suffix is not None,
        'has_word': word_current is not None
    }

def get_opposite_name(name, axis='X'):
    """Get the opposite side name based on axis - handles both word and suffix patterns"""
    pattern_info = detect_comprehensive_pattern(name, axis)
    
    new_name = name
    
    # Handle word-based pattern first
    if pattern_info['has_word']:
        word_current = pattern_info['word_current']
        word_opposite = pattern_info['word_opposite']
        
        if word_current == 'right':
            new_name = re.sub(r'\bright\b', word_opposite, new_name, flags=re.IGNORECASE)
        elif word_current == 'left':
            new_name = re.sub(r'\bleft\b', word_opposite, new_name, flags=re.IGNORECASE)
        elif word_current == 'front':
            new_name = re.sub(r'\bfront\b', word_opposite, new_name, flags=re.IGNORECASE)
        elif word_current == 'back':
            new_name = re.sub(r'\bback\b', word_opposite, new_name, flags=re.IGNORECASE)
        elif word_current == 'upper':
            new_name = re.sub(r'\bupper\b', word_opposite, new_name, flags=re.IGNORECASE)
        elif word_current == 'lower':
            new_name = re.sub(r'\blower\b', word_opposite, new_name, flags=re.IGNORECASE)
    
    # Handle suffix pattern
    if pattern_info['has_suffix']:
        current_suffix = pattern_info['suffix_current']
        opposite_suffix = pattern_info['suffix_opposite']
        new_name = new_name.replace(current_suffix, opposite_suffix)
        return new_name
    
    # If we had word pattern but no suffix, return the word-converted name
    if pattern_info['has_word']:
        return new_name
    
    # No pattern detected - add default suffix based on axis
    default_suffixes = {
        'X': '.R',      # Default to Right for X-axis
        'Y': '.B',      # Default to Back for Y-axis  
        'Z': '.D'       # Default to Down for Z-axis
    }
    return name + default_suffixes.get(axis, '.R')

def is_left_side(name):
    """Check if name represents left side (X-axis)"""
    left_patterns = [r'\.L$', r'_L$', r'\.l$', r'_l$', r'\.Left$', r'_Left$']
    return any(re.search(pattern, name) for pattern in left_patterns)

def is_right_side(name):
    """Check if name represents right side (X-axis)"""
    right_patterns = [r'\.R$', r'_R$', r'\.r$', r'_r$', r'\.Right$', r'_Right$']
    return any(re.search(pattern, name) for pattern in right_patterns)

def is_front_side(name):
    """Check if name represents front side (Y-axis)"""
    front_patterns = [r'\.F$', r'_F$', r'\.f$', r'_f$', r'\.Front$', r'_Front$', r'\.Fwd$', r'_Fwd$']
    return any(re.search(pattern, name) for pattern in front_patterns)

def is_back_side(name):
    """Check if name represents back side (Y-axis)"""
    back_patterns = [r'\.B$', r'_B$', r'\.b$', r'_b$', r'\.Back$', r'_Back$', r'\.Aft$', r'_Aft$']
    return any(re.search(pattern, name) for pattern in back_patterns)

def is_up_side(name):
    """Check if name represents up side (Z-axis)"""
    up_patterns = [r'\.U$', r'_U$', r'\.u$', r'_u$', r'\.Up$', r'_Up$', r'\.Top$', r'_Top$', r'\.Upper$', r'_Upper$']
    return any(re.search(pattern, name) for pattern in up_patterns)

def is_down_side(name):
    """Check if name represents down side (Z-axis)"""
    down_patterns = [r'\.D$', r'_D$', r'\.d$', r'_d$', r'\.Down$', r'_Down$', r'\.Bot$', r'_Bot$', r'\.Bottom$', r'_Bottom$', r'\.Lower$', r'_Lower$']
    return any(re.search(pattern, name) for pattern in down_patterns)

def detect_axis_from_selection(names):
    """Auto-detect which axis to use based on naming patterns in selection"""
    x_axis_count = sum(1 for name in names if is_left_side(name) or is_right_side(name))
    y_axis_count = sum(1 for name in names if is_front_side(name) or is_back_side(name))
    z_axis_count = sum(1 for name in names if is_up_side(name) or is_down_side(name))
    
    # Return axis with most matches, default to X
    if y_axis_count > x_axis_count and y_axis_count > z_axis_count:
        return 'Y'
    elif z_axis_count > x_axis_count and z_axis_count > y_axis_count:
        return 'Z'
    else:
        return 'X'

def get_side_type(name, axis='X'):
    """Get which side of the axis this name represents"""
    if axis == 'X':
        if is_left_side(name): return 'LEFT'
        if is_right_side(name): return 'RIGHT'
    elif axis == 'Y':
        if is_front_side(name): return 'FRONT'
        if is_back_side(name): return 'BACK'
    elif axis == 'Z':
        if is_up_side(name): return 'UP'
        if is_down_side(name): return 'DOWN'
    
    return 'NONE'

def suggest_naming_fix(name, axis='X'):
    """Suggest proper naming convention for bone/object based on axis"""
    current_suffix, _, _ = detect_naming_pattern(name, axis)
    if not current_suffix:
        # No pattern detected - suggest adding appropriate suffix
        default_suffixes = {
            'X': '.L',      # Suggest Left for X-axis
            'Y': '.F',      # Suggest Front for Y-axis
            'Z': '.U'       # Suggest Up for Z-axis
        }
        return f"{name}{default_suffixes.get(axis, '.L')}"
    return name  # Already follows convention

def get_base_name(name, axis='X'):
    """Get base name without side suffix or word pattern"""
    pattern_result = detect_naming_pattern(name, axis)
    
    base_name = name
    
    # Handle different return formats
    if len(pattern_result) >= 3:
        current_suffix = pattern_result[0]
        
        # Remove suffix if present
        if current_suffix:
            base_name = base_name.replace(current_suffix, '')
        
        # Remove word pattern if present (for mixed patterns)
        if len(pattern_result) == 5:
            word_current = pattern_result[3]
            if word_current and not current_suffix:  # Word-only pattern
                # Remove the word pattern - this is more complex
                # For now, just return the original name since we can't easily extract base
                # from word patterns like "Right knee" -> "knee"
                pass
    
    return base_name

def increment_name(name):
    """Add numerical suffix if no L/R pattern (fallback naming)"""
    # Check if name already has a number suffix
    match = re.search(r'\.(\d+)$', name)
    if match:
        current_num = int(match.group(1))
        new_num = current_num + 1
        return re.sub(r'\.\d+$', f'.{new_num:03d}', name)
    else:
        return f"{name}.001"