# Combined Flip Operator
# Handles both mesh and bone flipping in a single operation

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, EnumProperty

from ..utils.validation import validate_selected_objects, safe_mode_switch
from ..utils.detection import detect_mesh_armature_relationships, detect_bones_affecting_mesh, auto_detect_flip_candidates
from ..utils.naming import get_opposite_name, detect_axis_from_selection, detect_naming_pattern, detect_comprehensive_pattern


def _get_direction_items_for_axis(axis):
    """Get direction items based on axis"""
    if axis == 'X':
        return [
            ('LEFT_TO_RIGHT', "Left → Right", "Flip from left side to right side"),
            ('RIGHT_TO_LEFT', "Right → Left", "Flip from right side to left side")
        ]
    elif axis == 'Y':
        return [
            ('FRONT_TO_BACK', "Front → Back", "Flip from front side to back side"),
            ('BACK_TO_FRONT', "Back → Front", "Flip from back side to front side")
        ]
    elif axis == 'Z':
        return [
            ('UP_TO_DOWN', "Up → Down", "Flip from up side to down side"),
            ('DOWN_TO_UP', "Down → Up", "Flip from down side to up side")
        ]
    else:
        return [
            ('LEFT_TO_RIGHT', "Left → Right", "Flip from left side to right side"),
            ('RIGHT_TO_LEFT', "Right → Left", "Flip from right side to left side")
        ]


class OBJECT_OT_flip_mesh_and_bones(Operator):
    """Flip both mesh objects and their associated bones to the opposite side"""
    bl_idname = "object.flip_mesh_and_bones"
    bl_label = "Flip Mesh & Bones"
    bl_description = "Duplicate and mirror both mesh objects and their associated bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Operator properties
    auto_detect_bones: BoolProperty(
        name="Auto-detect Bones",
        description="Automatically detect bones associated with selected meshes",
        default=True
    )
    
    apply_transforms: BoolProperty(
        name="Apply Transforms",
        description="Apply location, rotation, and scale after mirroring",
        default=True
    )
    
    auto_rename: BoolProperty(
        name="Auto-rename",
        description="Automatically rename bones and objects using appropriate naming convention",
        default=True
    )
    
    mirror_axis: EnumProperty(
        name="Mirror Axis",
        description="Axis to mirror across",
        items=[
            ('X', "X-Axis (Left ↔ Right)", "Mirror across X-axis"),
            ('Y', "Y-Axis (Front ↔ Back)", "Mirror across Y-axis"),
            ('Z', "Z-Axis (Up ↔ Down)", "Mirror across Z-axis")
        ],
        default='X'
    )
    
    manual_mode: BoolProperty(
        name="Manual Mode",
        description="Override automatic axis and direction detection",
        default=False
    )
    
    manual_direction: EnumProperty(
        name="Manual Direction",
        description="Manually specify flip direction", 
        items=lambda self, context: _get_direction_items_for_axis(self.mirror_axis),
        default=0
    )
    
    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT' and 
                context.selected_objects and
                (any(obj.type == 'MESH' for obj in context.selected_objects) or
                 any(obj.type == 'ARMATURE' for obj in context.selected_objects)))
    
    def execute(self, context):
        # Validate input
        errors, warnings = validate_selected_objects()
        
        if errors:
            for error in errors:
                self.report({'ERROR'}, error)
            return {'CANCELLED'}
        
        if warnings:
            for warning in warnings:
                self.report({'WARNING'}, warning)
        
        # Ensure we're in object mode
        mode_error = safe_mode_switch('OBJECT')
        if mode_error:
            self.report({'ERROR'}, mode_error)
            return {'CANCELLED'}
        
        # Analyze selection
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        armature_objects = [obj for obj in context.selected_objects if obj.type == 'ARMATURE']
        
        if not mesh_objects and not armature_objects:
            self.report({'ERROR'}, "No mesh or armature objects selected")
            return {'CANCELLED'}
        
        # Detect relationships and candidates
        try:
            flip_data = self._analyze_flip_candidates(mesh_objects, armature_objects)
            
            if not flip_data['meshes'] and not flip_data['bones']:
                self.report({'ERROR'}, "No suitable objects found for flipping")
                return {'CANCELLED'}
            
            # Execute the flip operations
            results = self._execute_flip_operations(context, flip_data)
            
            # Report results
            if results['meshes_flipped'] > 0 or results['bones_flipped'] > 0:
                message = f"Flipped {results['meshes_flipped']} mesh(es) and {results['bones_flipped']} bone(s)"
                self.report({'INFO'}, message)
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "No objects were successfully flipped")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Flip operation failed: {str(e)}")
            return {'CANCELLED'}
    
    def _analyze_flip_candidates(self, mesh_objects, armature_objects):
        """Analyze which objects and bones should be flipped"""
        flip_data = {
            'meshes': [],
            'bones': [],
            'relationships': {},
            'armatures': [],
            'detected_axis': self.mirror_axis
        }
        
        # Auto-detect axis from selection if not in manual mode
        if not self.manual_mode:
            all_names = [obj.name for obj in mesh_objects + armature_objects]
            detected_axis = detect_axis_from_selection(all_names)
            flip_data['detected_axis'] = detected_axis
            self.report({'INFO'}, f"Auto-detected axis: {detected_axis}")
        else:
            # Manual mode - use manual_direction to determine direction override
            flip_data['manual_direction'] = self.manual_direction
            self.report({'INFO'}, f"Manual mode: axis={self.mirror_axis}, direction={self.manual_direction}")
        
        # Auto-detect candidates if enabled
        if self.auto_detect_bones and mesh_objects:
            self.report({'INFO'}, f"AUTO-DETECT: Starting with {len(mesh_objects)} mesh(es), {len(armature_objects)} armature(s)")
            
            candidates = auto_detect_flip_candidates()
            self.report({'INFO'}, f"AUTO-DETECT: Primary detection found {len(candidates.get('meshes', []))} mesh(es), {len(candidates.get('bones', []))} bone(s)")
            flip_data.update(candidates)
            
            # CRITICAL FIX: Auto-detect armatures from mesh relationships if bones were found but no armatures selected
            if flip_data['bones'] and not armature_objects:
                self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Found {len(flip_data['bones'])} bone(s) but no armatures selected - detecting from relationships")
                self.report({'INFO'}, f"AUTO-DETECT ARMATURES: DEBUG CHECKPOINT 1 - Starting armature detection")
                
                # Get armatures from the relationships that were used to find bones
                related_armatures = set()
                self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Checking {len(flip_data['meshes'])} meshes for relationships")
                self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Available relationships: {list(flip_data['relationships'].keys())}")
                
                for mesh_name in flip_data['meshes']:
                    mesh_obj = bpy.data.objects.get(mesh_name)
                    self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Mesh '{mesh_name}' exists: {mesh_obj is not None}")
                    if mesh_obj and mesh_name in flip_data['relationships']:
                        relationships = flip_data['relationships'][mesh_name]
                        self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Mesh '{mesh_name}' has {len(relationships)} relationship(s)")
                        for relationship in relationships:
                            armature_obj = relationship['armature']
                            self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Adding armature '{armature_obj.name}' to related_armatures")
                            related_armatures.add(armature_obj)
                    else:
                        self.report({'WARNING'}, f"AUTO-DETECT ARMATURES: Mesh '{mesh_name}' not found in relationships")
                
                flip_data['armatures'] = list(related_armatures)
                self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Final armatures: {[arm.name for arm in flip_data['armatures']]}")
                self.report({'INFO'}, f"AUTO-DETECT ARMATURES: Found {len(flip_data['armatures'])} related armature(s)")
            
            # FALLBACK: If auto-detection found no bones but we have armatures, 
            # detect bones from mesh-armature relationships
            elif not flip_data['bones'] and armature_objects:
                self.report({'INFO'}, f"AUTO-DETECT FALLBACK: No bones found, checking {len(mesh_objects)} mesh(es) against {len(armature_objects)} armature(s)")
                
                for mesh_obj in mesh_objects:
                    self.report({'INFO'}, f"AUTO-DETECT FALLBACK: Checking mesh '{mesh_obj.name}' for bone relationships")
                    for armature_obj in armature_objects:
                        self.report({'INFO'}, f"AUTO-DETECT FALLBACK: Checking armature '{armature_obj.name}'")
                        detected_bones = detect_bones_affecting_mesh(mesh_obj, armature_obj)
                        self.report({'INFO'}, f"AUTO-DETECT FALLBACK: Found {len(detected_bones)} affecting bones: {detected_bones}")
                        flip_data['bones'].extend(detected_bones)
                
                # Remove duplicates
                flip_data['bones'] = list(set(flip_data['bones']))
                
                if flip_data['bones']:
                    self.report({'INFO'}, f"Auto-detection fallback found {len(flip_data['bones'])} bone(s) from mesh relationships: {flip_data['bones']}")
                else:
                    self.report({'WARNING'}, "Auto-detection fallback found no bones with vertex weights")
        else:
            # Use manual selection
            flip_data['meshes'] = [obj.name for obj in mesh_objects]
            
            # In manual mode, detect bones affecting selected meshes
            if armature_objects and not flip_data['bones']:
                for mesh_obj in mesh_objects:
                    for armature_obj in armature_objects:
                        # Get ALL bones that affect this mesh (via vertex weights)
                        affecting_bones = detect_bones_affecting_mesh(mesh_obj, armature_obj)
                        flip_data['bones'].extend(affecting_bones)
                
                # If no bones found via vertex weights, include bones with side suffixes as fallback
                if not flip_data['bones']:
                    for armature_obj in armature_objects:
                        all_bones = [bone.name for bone in armature_obj.data.bones]
                        mirrored_bones = [bone_name for bone_name in all_bones 
                                        if any(suffix in bone_name for suffix in ['.L', '.R', '_L', '_R', '.l', '.r', '_l', '_r'])]
                        flip_data['bones'].extend(mirrored_bones)
                
                # Remove duplicates
                flip_data['bones'] = list(set(flip_data['bones']))
                
                if flip_data['bones']:
                    self.report({'INFO'}, f"Manual mode detected {len(flip_data['bones'])} bone(s): {', '.join(flip_data['bones'][:3])}{'...' if len(flip_data['bones']) > 3 else ''}")
        
        # Always include selected armatures (but preserve auto-detected ones)
        if not flip_data.get('armatures'):
            flip_data['armatures'] = armature_objects
        elif armature_objects:
            # Merge manually selected with auto-detected
            existing_armatures = set(flip_data['armatures'])
            existing_armatures.update(armature_objects)
            flip_data['armatures'] = list(existing_armatures)
        
        # Detect mesh-armature relationships
        relationships = detect_mesh_armature_relationships()
        flip_data['relationships'].update(relationships)
        
        return flip_data
    
    def _execute_flip_operations(self, context, flip_data):
        """Execute the actual flip operations"""
        results = {
            'meshes_flipped': 0,
            'bones_flipped': 0,
            'errors': []
        }
        
        # Phase 1: Flip mesh objects
        if flip_data['meshes']:
            mesh_result = self._flip_meshes(context, flip_data)
            results['meshes_flipped'] = mesh_result['count']
            results['errors'].extend(mesh_result['errors'])
            
            # Store information about created meshes for bone creation
            flip_data['created_meshes'] = mesh_result.get('created_meshes', [])
        
        # Phase 2: Flip bones
        self.report({'INFO'}, f"BONE PHASE CHECK: bones={len(flip_data['bones'])}, armatures={len(flip_data['armatures'])}")
        self.report({'INFO'}, f"BONE PHASE: bones list: {flip_data['bones']}")
        self.report({'INFO'}, f"BONE PHASE: armatures list: {[arm.name for arm in flip_data['armatures']]}")
        
        if flip_data['bones'] and flip_data['armatures']:
            self.report({'INFO'}, f"BONE PHASE: Starting bone flip with {len(flip_data['bones'])} bones and {len(flip_data['armatures'])} armatures")
            bone_result = self._flip_bones(context, flip_data)
            results['bones_flipped'] = bone_result['count']
            results['errors'].extend(bone_result['errors'])
            self.report({'INFO'}, f"BONE PHASE RESULT: flipped {bone_result['count']} bones, {len(bone_result['errors'])} errors")
        else:
            self.report({'WARNING'}, f"BONE PHASE SKIPPED: bones={len(flip_data.get('bones', []))}, armatures={len(flip_data.get('armatures', []))}")
        
        # Report any errors
        for error in results['errors']:
            self.report({'WARNING'}, error)
        
        return results
    
    def _flip_meshes(self, context, flip_data):
        """Flip mesh objects using the mesh flip operator"""
        result = {'count': 0, 'errors': [], 'created_meshes': []}
        
        try:
            # Get mesh objects by name
            mesh_objects = [bpy.data.objects.get(name) for name in flip_data['meshes']]
            mesh_objects = [obj for obj in mesh_objects if obj and obj.type == 'MESH']
            
            for mesh_obj in mesh_objects:
                try:
                    # Store current object count to detect new objects
                    before_objects = set(bpy.context.scene.objects)
                    
                    # Select only this mesh
                    bpy.ops.object.select_all(action='DESELECT')
                    mesh_obj.select_set(True)
                    context.view_layer.objects.active = mesh_obj
                    
                    # Call mesh flip operator with manual direction override if specified
                    flip_axis = flip_data['detected_axis']
                    
                    # Check if we need to pass manual direction to mesh operator
                    if flip_data.get('manual_direction'):
                        # The mesh operator needs to know about manual direction for proper naming
                        bpy.ops.object.flip_mesh(
                            apply_transforms=self.apply_transforms,
                            auto_rename=self.auto_rename,
                            keep_original_selected=False,
                            mirror_axis=flip_axis,
                            manual_mode=True,
                            manual_direction=flip_data['manual_direction']
                        )
                    else:
                        bpy.ops.object.flip_mesh(
                            apply_transforms=self.apply_transforms,
                            auto_rename=self.auto_rename,
                            keep_original_selected=False,
                            mirror_axis=flip_axis
                        )
                    
                    # Detect newly created objects
                    after_objects = set(bpy.context.scene.objects)
                    new_objects = after_objects - before_objects
                    
                    for new_obj in new_objects:
                        if new_obj.type == 'MESH':
                            result['created_meshes'].append(new_obj.name)
                            self.report({'INFO'}, f"Detected new mesh: '{new_obj.name}'")
                    
                    result['count'] += 1
                    
                except Exception as e:
                    result['errors'].append(f"Failed to flip mesh '{mesh_obj.name}': {str(e)}")
        
        except Exception as e:
            result['errors'].append(f"Mesh flip phase failed: {str(e)}")
        
        return result
    
    def _flip_bones(self, context, flip_data):
        """Flip bones using the bone flip operator"""
        result = {'count': 0, 'errors': []}
        
        self.report({'INFO'}, f"FLIP_BONES: Starting with {len(flip_data['armatures'])} armatures")
        
        try:
            for armature_obj in flip_data['armatures']:
                self.report({'INFO'}, f"FLIP_BONES: Processing armature '{armature_obj.name if armature_obj else 'None'}' type={armature_obj.type if armature_obj else 'None'}")
                if not armature_obj or armature_obj.type != 'ARMATURE':
                    self.report({'WARNING'}, f"FLIP_BONES: Skipping invalid armature")
                    continue
                
                try:
                    # Switch to the armature
                    bpy.ops.object.select_all(action='DESELECT')
                    armature_obj.select_set(True)
                    context.view_layer.objects.active = armature_obj
                    
                    # Switch to edit mode
                    bpy.ops.object.mode_set(mode='EDIT')
                    
                    # Process bones individually for better error handling
                    bones_processed = 0
                    
                    # PROPER BLENDER 4.2.1 BONE MIRRORING WORKFLOW - NEVER RENAME ORIGINAL BONES
                    bones_to_process = []
                    
                    # Step 1: Pre-process parent bones to ensure mappings exist for pattern-less children
                    self.report({'INFO'}, f"FLIP_BONES: Pre-processing parent bones for mapping")
                    all_parents = set()
                    for bone_name in flip_data['bones']:
                        bone = armature_obj.data.edit_bones.get(bone_name)
                        if bone and bone.parent:
                            all_parents.add(bone.parent.name)
                    
                    # Process parent bones that have patterns to create mappings
                    for parent_name in all_parents:
                        if parent_name not in flip_data['bones']:  # Only process if not already in main list
                            pattern_info = detect_comprehensive_pattern(parent_name, flip_data['detected_axis'])
                            if pattern_info['has_word'] or pattern_info['has_suffix']:
                                opposite_name = get_opposite_name(parent_name, flip_data['detected_axis'])
                                existing_opposite = self._find_existing_base_bone(opposite_name, armature_obj)
                                
                                if existing_opposite:
                                    # Store parent mapping for pattern-less children
                                    if not hasattr(flip_data, 'parent_mapping'):
                                        flip_data['parent_mapping'] = {}
                                    flip_data['parent_mapping'][parent_name] = existing_opposite
                                    self.report({'INFO'}, f"Pre-mapped parent '{parent_name}' → '{existing_opposite}' for pattern-less children")
                    
                    # Step 2: Check which bones are valid for mirroring (have naming patterns)
                    self.report({'INFO'}, f"FLIP_BONES: Processing {len(flip_data['bones'])} bones: {flip_data['bones']}")
                    
                    for bone_name in flip_data['bones']:
                        bone = armature_obj.data.edit_bones.get(bone_name)
                        self.report({'INFO'}, f"FLIP_BONES: Looking for bone '{bone_name}' - found: {bone is not None}")
                        if not bone:
                            result['errors'].append(f"Bone '{bone_name}' not found in armature '{armature_obj.name}'")
                            continue
                        
                        # Check if bone has a valid naming pattern (suffix or word-based)
                        from ..utils.naming import detect_comprehensive_pattern
                        pattern_info = detect_comprehensive_pattern(bone_name, flip_data['detected_axis'])
                        
                        has_suffix_pattern = pattern_info['has_suffix']
                        has_word_pattern = pattern_info['has_word']
                        
                        if has_suffix_pattern or has_word_pattern:
                            # Bone has a valid pattern - can be mirrored
                            bones_to_process.append(bone_name)
                            
                            if has_suffix_pattern and has_word_pattern:
                                self.report({'INFO'}, f"Bone '{bone_name}' has mixed pattern (suffix + word) - will mirror properly")
                            elif has_suffix_pattern:
                                self.report({'INFO'}, f"Bone '{bone_name}' has suffix pattern '{pattern_info['suffix_current']}' - ready for mirroring")
                            elif has_word_pattern:
                                # Word-only pattern like "Right knee" - check if this bone should be created
                                opposite_name = get_opposite_name(bone_name, flip_data['detected_axis'])
                                
                                # Check if this bone is part of the mesh's bone chain
                                should_create = self._should_create_bone(bone_name, flip_data)
                                
                                if should_create:
                                    # Check if opposite bone already exists (with different case variations)
                                    existing_opposite = self._find_existing_base_bone(opposite_name, armature_obj)
                                    
                                    if existing_opposite:
                                        self.report({'INFO'}, f"Found existing base bone '{existing_opposite}' for '{bone_name}' - will use existing instead of creating '{opposite_name}'")
                                        # Store the mapping for later parenting use
                                        if not hasattr(flip_data, 'base_bone_mapping'):
                                            flip_data['base_bone_mapping'] = {}
                                        flip_data['base_bone_mapping'][opposite_name] = existing_opposite
                                        
                                        # Also store direct parent mapping for pattern-less children
                                        if not hasattr(flip_data, 'parent_mapping'):
                                            flip_data['parent_mapping'] = {}
                                        flip_data['parent_mapping'][bone_name] = existing_opposite
                                        
                                        bones_processed += 1
                                    elif not armature_obj.data.edit_bones.get(opposite_name):
                                        self.report({'INFO'}, f"Bone '{bone_name}' has word-only pattern - will create '{opposite_name}' manually")
                                        
                                        # Duplicate the bone manually
                                        new_bone = armature_obj.data.edit_bones.new(opposite_name)
                                        new_bone.head = bone.head.copy()
                                        new_bone.tail = bone.tail.copy()
                                        new_bone.roll = bone.roll
                                        
                                        # Mirror the position across the appropriate axis
                                        if flip_data['detected_axis'] == 'X':
                                            new_bone.head.x = -new_bone.head.x
                                            new_bone.tail.x = -new_bone.tail.x
                                        elif flip_data['detected_axis'] == 'Y':
                                            new_bone.head.y = -new_bone.head.y
                                            new_bone.tail.y = -new_bone.tail.y
                                        elif flip_data['detected_axis'] == 'Z':
                                            new_bone.head.z = -new_bone.head.z
                                            new_bone.tail.z = -new_bone.tail.z
                                        
                                        # Set parent - prefer existing base bone over creating new parent
                                        if bone.parent:
                                            parent_opposite_name = get_opposite_name(bone.parent.name, flip_data['detected_axis'])
                                            # Check for existing parent base bone first
                                            existing_parent = self._find_existing_base_bone(parent_opposite_name, armature_obj)
                                            if existing_parent:
                                                parent_opposite = armature_obj.data.edit_bones.get(existing_parent)
                                                if parent_opposite:
                                                    new_bone.parent = parent_opposite
                                                    self.report({'INFO'}, f"Parented '{opposite_name}' to existing base bone '{existing_parent}'")
                                            else:
                                                parent_opposite = armature_obj.data.edit_bones.get(parent_opposite_name)
                                                if parent_opposite:
                                                    new_bone.parent = parent_opposite
                                                    self.report({'INFO'}, f"Parented '{opposite_name}' to created '{parent_opposite_name}'")
                                                else:
                                                    self.report({'INFO'}, f"Skipping parent creation for '{opposite_name}' - parent '{parent_opposite_name}' not in mesh chain")
                                        
                                        # Store direct parent mapping for pattern-less children
                                        if not hasattr(flip_data, 'parent_mapping'):
                                            flip_data['parent_mapping'] = {}
                                        flip_data['parent_mapping'][bone_name] = opposite_name
                                        
                                        bones_processed += 1
                                        self.report({'INFO'}, f"Created opposite bone '{opposite_name}' for word-pattern bone '{bone_name}'")
                                    else:
                                        self.report({'INFO'}, f"Opposite bone '{opposite_name}' already exists")
                                else:
                                    self.report({'INFO'}, f"Skipping bone '{bone_name}' - not part of mesh bone chain")
                        else:
                            # IMPORTANT: Bone has no pattern - we'll handle this during mesh processing
                            # Store bones that need suffix creation for later
                            self.report({'INFO'}, f"Bone '{bone_name}' has no pattern - will create mirrored bone based on mesh needs")
                            bones_to_process.append(bone_name)
                    
                    # Step 2: Use Blender's symmetrize for suffix-based patterns only
                    suffix_bones = []
                    for bone_name in bones_to_process:
                        pattern_info = detect_comprehensive_pattern(bone_name, flip_data['detected_axis'])
                        if pattern_info['has_suffix']:
                            suffix_bones.append(bone_name)
                    
                    if suffix_bones:
                        bpy.ops.armature.select_all(action='DESELECT')
                        
                        selected_bones = 0
                        for bone_name in suffix_bones:
                            bone = armature_obj.data.edit_bones.get(bone_name)
                            if bone:
                                bone.select = True
                                bone.select_head = True
                                bone.select_tail = True
                                selected_bones += 1
                        
                        if selected_bones > 0:
                            try:
                                # Use Blender's built-in symmetrize for suffix-based patterns
                                self.report({'INFO'}, f"Symmetrizing {selected_bones} suffix-pattern bone(s) using bpy.ops.armature.symmetrize()")
                                bpy.ops.armature.symmetrize()
                                
                                bones_processed += selected_bones
                                result['count'] += bones_processed
                                
                                self.report({'INFO'}, f"Successfully symmetrized {bones_processed} suffix-pattern bone(s) in '{armature_obj.name}'")
                                
                            except Exception as e:
                                result['errors'].append(f"Symmetrize operation failed: {str(e)}")
                        else:
                            result['errors'].append("No valid suffix-pattern bones found for symmetrizing")
                    
                    # Step 3: Create bones for pattern-less bones based on created meshes
                    if flip_data.get('created_meshes'):
                        self.report({'INFO'}, f"Creating specific bones for {len(flip_data['created_meshes'])} created meshes")
                        
                        # Find bones that need specific side creation
                        pattern_less_bones = []
                        for bone_name in bones_to_process:
                            pattern_info = detect_comprehensive_pattern(bone_name, flip_data['detected_axis'])
                            if not pattern_info['has_suffix'] and not pattern_info['has_word']:
                                pattern_less_bones.append(bone_name)
                        
                        # For each created mesh, create the needed bones
                        for mesh_name in flip_data['created_meshes']:
                            mesh_pattern_info = detect_comprehensive_pattern(mesh_name, flip_data['detected_axis'])
                            
                            if mesh_pattern_info['has_suffix']:
                                # Use manual direction override if specified
                                if flip_data.get('manual_direction'):
                                    target_suffix = self._get_target_suffix(flip_data)
                                    self.report({'INFO'}, f"Mesh '{mesh_name}' needs bones with manual direction suffix '{target_suffix}' (override: {flip_data['manual_direction']})")
                                else:
                                    target_suffix = mesh_pattern_info['suffix_current']
                                    self.report({'INFO'}, f"Mesh '{mesh_name}' needs bones with suffix '{target_suffix}'")
                                
                                # Create bones with the target suffix for pattern-less bones
                                for bone_name in pattern_less_bones:
                                    target_bone_name = bone_name + target_suffix
                                    
                                    if not armature_obj.data.edit_bones.get(target_bone_name):
                                        original_bone = armature_obj.data.edit_bones.get(bone_name)
                                        if original_bone:
                                            new_bone = armature_obj.data.edit_bones.new(target_bone_name)
                                            new_bone.head = original_bone.head.copy()
                                            new_bone.tail = original_bone.tail.copy()
                                            new_bone.roll = original_bone.roll
                                            
                                            # Mirror position across the detected axis
                                            if flip_data['detected_axis'] == 'X':
                                                new_bone.head.x = -new_bone.head.x
                                                new_bone.tail.x = -new_bone.tail.x
                                            elif flip_data['detected_axis'] == 'Y':
                                                new_bone.head.y = -new_bone.head.y
                                                new_bone.tail.y = -new_bone.tail.y
                                            elif flip_data['detected_axis'] == 'Z':
                                                new_bone.head.z = -new_bone.head.z
                                                new_bone.tail.z = -new_bone.tail.z
                                            
                                            # Set parent relationship - use simple parent mapping
                                            if original_bone.parent:
                                                original_parent_name = original_bone.parent.name
                                                parent_mapping = getattr(flip_data, 'parent_mapping', {})
                                                
                                                # Check if we have a direct mapping for this parent
                                                if original_parent_name in parent_mapping:
                                                    # Use the mapped parent bone
                                                    mapped_parent_name = parent_mapping[original_parent_name]
                                                    parent_target = armature_obj.data.edit_bones.get(mapped_parent_name)
                                                    if parent_target:
                                                        new_bone.parent = parent_target
                                                        self.report({'INFO'}, f"Parented '{target_bone_name}' to mapped parent '{mapped_parent_name}' (from '{original_parent_name}')")
                                                    else:
                                                        new_bone.parent = original_bone.parent
                                                        self.report({'INFO'}, f"Using original parent for '{target_bone_name}' (mapped parent '{mapped_parent_name}' not found)")
                                                else:
                                                    # Try pattern-less parent naming (parent + suffix)
                                                    parent_target_name = original_parent_name + target_suffix
                                                    parent_target = armature_obj.data.edit_bones.get(parent_target_name)
                                                    if parent_target:
                                                        new_bone.parent = parent_target
                                                        self.report({'INFO'}, f"Parented '{target_bone_name}' to pattern-less parent '{parent_target_name}'")
                                                    else:
                                                        new_bone.parent = original_bone.parent
                                                        self.report({'INFO'}, f"Using original parent for '{target_bone_name}' (no mapping or pattern-less parent found)")
                                            
                                            bones_processed += 1
                                            self.report({'INFO'}, f"Created bone '{target_bone_name}' for mesh '{mesh_name}'")
                    
                    # Total result count includes both manual and symmetrize operations
                    result['count'] += bones_processed
                    
                    # Return to object mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    # NOW update vertex groups - bones are finalized in Object Mode
                    if result['count'] > 0:  # Only if bones were successfully processed
                        # Update vertex groups for created meshes specifically
                        if flip_data.get('created_meshes'):
                            self._update_mesh_vertex_groups_targeted(flip_data, bones_to_process, pattern_less_bones, flip_data['detected_axis'])
                        else:
                            self._update_mesh_vertex_groups(flip_data, bones_to_process, flip_data['detected_axis'])
                    
                except Exception as e:
                    result['errors'].append(f"Failed to flip bones in '{armature_obj.name}': {str(e)}")
                    # Try to return to object mode
                    try:
                        bpy.ops.object.mode_set(mode='OBJECT')
                    except:
                        pass
        
        except Exception as e:
            result['errors'].append(f"Bone flip phase failed: {str(e)}")
        
        return result
    
    def draw(self, context):
        layout = self.layout
        
        # Detection options
        box = layout.box()
        box.label(text="Detection:", icon='VIEWZOOM')
        box.prop(self, "auto_detect_bones")
        
        # Axis and direction options
        box = layout.box()
        box.label(text="Mirror Options:", icon='MOD_MIRROR')
        box.prop(self, "mirror_axis")
        box.prop(self, "manual_mode")
        
        if self.manual_mode:
            sub_box = box.box()
            sub_box.label(text="Manual Override:", icon='HAND')
            sub_box.prop(self, "manual_direction")
        
        # Transform options
        box = layout.box()
        box.label(text="Transform Options:", icon='ORIENTATION_GLOBAL')
        box.prop(self, "apply_transforms")
        box.prop(self, "auto_rename")
    
    def _update_mesh_vertex_groups(self, flip_data, bones_processed, axis):
        """Update vertex groups on mirrored meshes to reference new bone names"""
        try:
            # Find all mirrored meshes (those ending with .R, .L, etc.)
            all_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
            
            for mesh_obj in all_meshes:
                mesh_name = mesh_obj.name
                
                # Check if this is a mirrored mesh by looking for side patterns
                from ..utils.naming import detect_comprehensive_pattern
                pattern_info = detect_comprehensive_pattern(mesh_name, axis)
                
                has_suffix_pattern = pattern_info['has_suffix']
                has_word_pattern = pattern_info['has_word']
                
                if not has_suffix_pattern and not has_word_pattern:
                    continue  # Not a mirrored mesh
                
                current_suffix = pattern_info['suffix_current'] if has_suffix_pattern else None
                
                self.report({'INFO'}, f"Updating vertex groups for mesh '{mesh_name}'")
                
                # Update vertex groups to match mirrored bone names
                vertex_groups_to_update = []
                for vg in mesh_obj.vertex_groups:
                    if vg.name in bones_processed:
                        vertex_groups_to_update.append(vg)
                
                for vg in vertex_groups_to_update:
                    old_bone_name = vg.name
                    
                    # SIMPLE RULE: Mesh side suffix should match bone side suffix
                    # Examples:
                    # - Mesh "Hair.R" should use bone "HairPin_Root.R" 
                    # - Mesh "Hair.L" should use bone "HairPin_Root.L"
                    # - Mesh "Hair.F" should use bone "HairPin_Root.F" (front)
                    # - Mesh "Hair.B" should use bone "HairPin_Root.B" (back)
                    
                    # Determine the proper bone name for this mesh
                    if has_suffix_pattern and current_suffix:
                        # Mesh has suffix pattern - vertex group should reference bone with same suffix
                        from ..utils.naming import get_base_name
                        base_bone_name = get_base_name(old_bone_name, axis)
                        new_bone_name = base_bone_name + current_suffix
                        self.report({'INFO'}, f"VG UPDATE: '{old_bone_name}' -> '{new_bone_name}' (matching mesh suffix '{current_suffix}')")
                    elif has_word_pattern:
                        # Mesh has word-based pattern - create appropriate bone name
                        new_bone_name = get_opposite_name(old_bone_name, axis)
                        self.report({'INFO'}, f"VG UPDATE: '{old_bone_name}' -> '{new_bone_name}' (word-based pattern)")
                    else:
                        # Mesh has no pattern - keep original bone name
                        new_bone_name = old_bone_name
                    
                    # Check if the new bone actually exists
                    armature_obj = None
                    
                    # First try to find relationships for this mesh
                    relationships = flip_data.get('relationships', {}).get(mesh_name, [])
                    if relationships:
                        armature_obj = relationships[0]['armature']
                    else:
                        # If no relationships found (e.g., for mirrored meshes), 
                        # use the armatures from flip_data directly
                        if flip_data.get('armatures'):
                            armature_obj = flip_data['armatures'][0]
                            self.report({'INFO'}, f"🔗 Using armature '{armature_obj.name}' from flip_data for mesh '{mesh_name}'")
                    
                    if armature_obj:
                        # DEBUG: List all bones in the armature
                        all_bones = [bone.name for bone in armature_obj.data.bones]
                        self.report({'INFO'}, f"🔍 DEBUG: Armature '{armature_obj.name}' has {len(all_bones)} bones: {all_bones}")
                        self.report({'INFO'}, f"🔍 DEBUG: Looking for bone '{new_bone_name}' in armature '{armature_obj.name}'")
                        
                        if armature_obj.data.bones.get(new_bone_name):
                            vg.name = new_bone_name
                            self.report({'INFO'}, f"✅ Updated vertex group '{old_bone_name}' -> '{new_bone_name}' on mesh '{mesh_name}'")
                        else:
                            self.report({'WARNING'}, f"❌ Bone '{new_bone_name}' not found in armature '{armature_obj.name}', keeping vertex group '{old_bone_name}'")
                    else:
                        self.report({'WARNING'}, f"❌ No armature found for mesh '{mesh_name}'")
                        
        except Exception as e:
            self.report({'WARNING'}, f"Failed to update vertex groups: {str(e)}")
    
    def _update_mesh_vertex_groups_targeted(self, flip_data, bones_processed, pattern_less_bones, axis):
        """Update vertex groups for created meshes specifically"""
        try:
            from ..utils.naming import detect_comprehensive_pattern
            
            # Only update vertex groups for the created meshes
            for mesh_name in flip_data.get('created_meshes', []):
                mesh_obj = bpy.data.objects.get(mesh_name)
                if not mesh_obj or mesh_obj.type != 'MESH':
                    continue
                
                mesh_pattern_info = detect_comprehensive_pattern(mesh_name, axis)
                if not mesh_pattern_info['has_suffix']:
                    continue
                
                target_suffix = mesh_pattern_info['suffix_current']
                self.report({'INFO'}, f"Updating vertex groups for created mesh '{mesh_name}' with suffix '{target_suffix}'")
                
                # Update vertex groups to reference the new bones
                for vg in mesh_obj.vertex_groups:
                    old_bone_name = vg.name
                    
                    # If this bone was pattern-less, update to use the new suffixed name
                    if old_bone_name in pattern_less_bones:
                        new_bone_name = old_bone_name + target_suffix
                        
                        # Check if the new bone exists
                        armature_obj = None
                        if flip_data.get('armatures'):
                            armature_obj = flip_data['armatures'][0]
                        
                        if armature_obj and armature_obj.data.bones.get(new_bone_name):
                            vg.name = new_bone_name
                            self.report({'INFO'}, f"✅ Updated vertex group '{old_bone_name}' -> '{new_bone_name}' on mesh '{mesh_name}'")
                        else:
                            self.report({'WARNING'}, f"❌ Bone '{new_bone_name}' not found, keeping vertex group '{old_bone_name}'")
                            
        except Exception as e:
            self.report({'WARNING'}, f"Failed to update targeted vertex groups: {str(e)}")
    
    def _should_create_bone(self, bone_name, flip_data):
        """Check if a bone should be created based on mesh vertex groups and bone chains"""
        try:
            # Get original mesh names to check vertex groups
            original_meshes = flip_data.get('meshes', [])
            
            for mesh_name in original_meshes:
                mesh_obj = bpy.data.objects.get(mesh_name)
                if not mesh_obj or mesh_obj.type != 'MESH':
                    continue
                
                # Get all vertex group names from this mesh
                vertex_group_names = [vg.name for vg in mesh_obj.vertex_groups]
                
                # Check if this bone has a vertex group in the mesh
                if bone_name in vertex_group_names:
                    self.report({'INFO'}, f"✅ Bone '{bone_name}' has vertex group in mesh '{mesh_name}' - should create")
                    return True
                
                # Check if this bone is a DIRECT parent of bones that have vertex groups (for end bones)
                if flip_data.get('armatures'):
                    armature_obj = flip_data['armatures'][0]
                    if armature_obj and armature_obj.data.bones.get(bone_name):
                        bone = armature_obj.data.bones[bone_name]
                        
                        # Only check DIRECT children for end bones (not deep hierarchy)
                        for child in bone.children:
                            if child.name in vertex_group_names:
                                self.report({'INFO'}, f"✅ Bone '{bone_name}' is direct parent of vertex group bone '{child.name}' - should create")
                                return True
                        
                        # Check if any DIRECT children have vertex groups AND are in the bone list
                        # This catches end bones like "Shackles_Chain.005_end"
                        bones_list = flip_data.get('bones', [])
                        for child in bone.children:
                            if child.name in bones_list:
                                self.report({'INFO'}, f"✅ Bone '{bone_name}' is parent of detected bone '{child.name}' - should create")
                                return True
            
            self.report({'INFO'}, f"❌ Bone '{bone_name}' not connected to mesh vertex groups - skip creation")
            return False
            
        except Exception as e:
            self.report({'WARNING'}, f"Error checking bone creation for '{bone_name}': {str(e)}")
            return False  # Default to not creating if there's an error
    
    def _find_existing_base_bone(self, target_name, armature_obj):
        """Find existing base bone with case variations (Left knee vs left knee)"""
        try:
            # Check exact match first
            if armature_obj.data.edit_bones.get(target_name):
                return target_name
            
            # Check case variations for common base bones
            target_lower = target_name.lower()
            
            for bone in armature_obj.data.edit_bones:
                bone_lower = bone.name.lower()
                
                # Check if this is the same bone with different capitalization
                if bone_lower == target_lower:
                    self.report({'INFO'}, f"Found case variation: '{target_name}' exists as '{bone.name}'")
                    return bone.name
                
                # Check common base bone patterns (more flexible matching)
                # For example: "left knee" should match "Left knee", "LEFT_KNEE", etc.
                if self._is_same_base_bone(target_name, bone.name):
                    self.report({'INFO'}, f"Found base bone match: '{target_name}' matches existing '{bone.name}'")
                    return bone.name
            
            return None
            
        except Exception as e:
            self.report({'WARNING'}, f"Error finding existing base bone for '{target_name}': {str(e)}")
            return None
    
    def _is_same_base_bone(self, name1, name2):
        """Check if two bone names refer to the same base bone (ignoring case and separators)"""
        # Normalize names: lowercase, replace separators with spaces
        def normalize(name):
            import re
            # Replace underscores, dots, dashes with spaces
            normalized = re.sub(r'[_.\-]', ' ', name.lower())
            # Remove extra spaces
            normalized = ' '.join(normalized.split())
            return normalized
        
        norm1 = normalize(name1)
        norm2 = normalize(name2)
        
        # Check if they're the same when normalized
        if norm1 == norm2:
            return True
        
        # Check common base bone variations
        base_bone_aliases = {
            'left knee': ['left_knee', 'leftknee', 'l_knee', 'knee_l', 'knee.l'],
            'right knee': ['right_knee', 'rightknee', 'r_knee', 'knee_r', 'knee.r'],
            'left ankle': ['left_ankle', 'leftankle', 'l_ankle', 'ankle_l', 'ankle.l'],
            'right ankle': ['right_ankle', 'rightankle', 'r_ankle', 'ankle_r', 'ankle.r'],
        }
        
        for canonical, aliases in base_bone_aliases.items():
            if norm1 == canonical and norm2 in aliases:
                return True
            if norm2 == canonical and norm1 in aliases:
                return True
        
        return False
    
    def _get_target_suffix(self, flip_data):
        """Get the target suffix based on manual direction or auto-detection"""
        axis = flip_data['detected_axis']
        
        # Check if manual direction is specified
        manual_direction = flip_data.get('manual_direction')
        
        if manual_direction:
            # Manual direction override
            if manual_direction == 'RIGHT_TO_LEFT':
                if axis == 'X':
                    return '.L'  # Right (.R) -> Left (.L)
                elif axis == 'Y':
                    return '.B'  # Front (.F) -> Back (.B)
                elif axis == 'Z':
                    return '.D'  # Up (.U) -> Down (.D)
            elif manual_direction == 'LEFT_TO_RIGHT':
                if axis == 'X':
                    return '.R'  # Left (.L) -> Right (.R)
                elif axis == 'Y':
                    return '.F'  # Back (.B) -> Front (.F)
                elif axis == 'Z':
                    return '.U'  # Down (.D) -> Up (.U)
        
        # Default auto-detection behavior
        if axis == 'X':
            return '.R'  # Default to Right
        elif axis == 'Y':
            return '.B'  # Default to Back
        elif axis == 'Z':
            return '.D'  # Default to Down
        
        return '.R'  # Fallback
    
    def invoke(self, context, event):
        # Show options dialog
        return context.window_manager.invoke_props_dialog(self)


# Registration
classes = (
    OBJECT_OT_flip_mesh_and_bones,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass