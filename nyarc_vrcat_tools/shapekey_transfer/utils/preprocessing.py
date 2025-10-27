# Shape Key Transfer Pre-Processing Utilities
# Optional quality enhancement modifiers that work on temporary copies
# Based on Rinvo's Blendshape Transfer approach (MIT License)

import bpy


def create_preprocessed_source(source_obj, context, use_subdivision=False,
                               subdivision_levels=1, subdivision_simple=False,
                               use_displace=False, displace_strength=0.01,
                               displace_midlevel=0.8, displace_direction='NORMAL'):
    """
    Create temporary copy of source with optional pre-processing modifiers.

    This function creates a temporary duplicate of the source object and applies
    optional modifiers to improve shape key transfer quality:

    - Subdivision: Adds more geometry for Surface Deform to sample from
    - Displace: Moves geometry closer to target before transfer

    IMPORTANT: The original source object is never modified. All changes happen
    on a temporary copy that should be deleted after use.

    Args:
        source_obj: Source mesh object to preprocess
        context: Blender context
        use_subdivision: Enable subdivision surface modifier
        subdivision_levels: Number of subdivision levels (0-6)
        subdivision_simple: Use simple subdivision instead of Catmull-Clark
        use_displace: Enable displace modifier
        displace_strength: Displacement strength
        displace_midlevel: Displacement midlevel (0.0-1.0)
        displace_direction: Displacement direction ('X', 'Y', 'Z', 'NORMAL')

    Returns:
        tuple: (working_source, is_temp_copy)
            - working_source: Object to use for transfer (original or temp copy)
            - is_temp_copy: True if a temp copy was created, False otherwise
    """

    # If no preprocessing needed, return original
    if not use_subdivision and not use_displace:
        return source_obj, False

    # Create temporary copy of source
    temp_source = source_obj.copy()
    temp_source.data = source_obj.data.copy()
    temp_source.name = f"TEMP_Preprocessing_{source_obj.name}"
    context.collection.objects.link(temp_source)

    # Store original active and mode
    original_active = context.view_layer.objects.active
    original_mode = context.mode

    # Ensure object mode
    if context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Set temp source as active
    context.view_layer.objects.active = temp_source

    try:
        # Add Subdivision modifier (NOT applied, just evaluated during Surface Deform)
        if use_subdivision:
            subdiv_mod = temp_source.modifiers.new(name="Temp_Subdivision", type='SUBSURF')
            subdiv_mod.levels = subdivision_levels
            subdiv_mod.render_levels = subdivision_levels

            if subdivision_simple:
                subdiv_mod.subdivision_type = 'SIMPLE'

            print(f"Added Subdivision modifier to temp source (levels: {subdivision_levels})")

        # Add Displace modifier (applied as shape key, then modifier removed)
        if use_displace:
            displace_mod = temp_source.modifiers.new(name="Temp_Displace", type='DISPLACE')
            displace_mod.strength = displace_strength
            displace_mod.mid_level = displace_midlevel
            displace_mod.direction = displace_direction

            # Apply as shape key (non-destructive)
            bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=displace_mod.name)

            # Rename and activate the displacement shape key
            if temp_source.data.shape_keys and temp_source.data.shape_keys.key_blocks:
                displacement_key = temp_source.data.shape_keys.key_blocks[-1]
                displacement_key.name = "Temp_Displacement"
                displacement_key.value = 1.0  # Activate displacement

            # Remove the modifier (shape key remains active)
            temp_source.modifiers.remove(displace_mod)

            print(f"Applied Displace as shape key on temp source (strength: {displace_strength})")

    finally:
        # Restore original active object
        if original_active:
            context.view_layer.objects.active = original_active

    return temp_source, True


def cleanup_preprocessed_source(temp_source, context):
    """
    Remove temporary preprocessed source object.

    Args:
        temp_source: Temporary source object to remove
        context: Blender context
    """

    if not temp_source:
        return

    try:
        # Store current selection/active
        original_active = context.view_layer.objects.active
        original_selected = context.selected_objects.copy()

        # Ensure object mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')

        # Select and delete the temp object
        temp_source.select_set(True)
        context.view_layer.objects.active = temp_source
        bpy.ops.object.delete()

        print(f"Cleaned up temporary preprocessed source")

        # Restore selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selected:
            if obj and obj.name in context.scene.objects:
                obj.select_set(True)

        if original_active and original_active.name in context.scene.objects:
            context.view_layer.objects.active = original_active

    except Exception as e:
        print(f"Error cleaning up preprocessed source: {e}")
        # Try direct removal as fallback
        try:
            bpy.data.objects.remove(temp_source, do_unlink=True)
        except:
            pass


def get_classes():
    """Get all preprocessing classes for registration (none for preprocessing)"""
    return []
