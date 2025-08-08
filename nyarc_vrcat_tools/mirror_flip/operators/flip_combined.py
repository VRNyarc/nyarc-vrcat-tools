# Combined Flip Operator - NEW CLEAN VERSION
# Simple, robust bone chain mirroring system

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, EnumProperty

from ..utils.validation import validate_selected_objects, safe_mode_switch
from ..utils.chain_analysis import analyze_mesh_chains, get_mesh_armature_pairs
from ..utils.bone_classification import classify_bone_chain, get_vrchat_opposite_bone
from ..utils.simple_mirroring import mirror_accessory_chain, mirror_base_armature_chain, mirror_vrchat_base_reparent_chain, update_vertex_groups


class OBJECT_OT_flip_mesh_and_bones_combined(Operator):
    """Flip both mesh objects and their associated bones using clean chain analysis"""
    bl_idname = "object.flip_mesh_and_bones_combined"
    bl_label = "Flip Mesh & Bones (Combined)"
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
        description="Automatically rename using .L/.R convention",
        default=True
    )
    
    keep_original_selected: BoolProperty(
        name="Keep Original Selected",
        description="Keep original objects selected after operation",
        default=False
    )
    
    mirror_axis: EnumProperty(
        name="Mirror Axis",
        description="Axis to mirror across",
        items=[
            ('X', "X-Axis", "Mirror across X-axis (left/right)"),
            ('Y', "Y-Axis", "Mirror across Y-axis (front/back)"),
            ('Z', "Z-Axis", "Mirror across Z-axis (up/down)")
        ],
        default='X'
    )
    
    # Manual mode toggle
    manual_mode: BoolProperty(
        name="Manual Mode",
        description="Override automatic axis and direction detection",
        default=False
    )
    
    # Manual direction (only used in manual mode)
    manual_direction: EnumProperty(
        name="Manual Direction", 
        description="Manually specify flip direction",
        items=[
            ('LEFT_TO_RIGHT', "Left → Right", "Flip from left side to right side"),
            ('RIGHT_TO_LEFT', "Right → Left", "Flip from right side to left side"),
            ('FRONT_TO_BACK', "Front → Back", "Flip from front side to back side"),
            ('BACK_TO_FRONT', "Back → Front", "Flip from back side to front side"),
            ('UP_TO_DOWN', "Up → Down", "Flip from up side to down side"),
            ('DOWN_TO_UP', "Down → Up", "Flip from down side to up side"),
            ('POSITIVE', "Positive → Negative", "Flip to negative side of axis"),
            ('NEGATIVE', "Negative → Positive", "Flip to positive side of axis")
        ],
        default='LEFT_TO_RIGHT'
    )
    
    @classmethod
    def poll(cls, context):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        result = (context.mode == 'OBJECT' and 
                context.selected_objects and
                any(obj.type == 'MESH' for obj in context.selected_objects))
        print(f"🔍 POLL_CHECK [{timestamp}] - Combined operator poll result: {result}")
        return result
    
    def execute(self, context):
        """Main execution - clean and simple"""
        import time
        import datetime
        import traceback
        
        # Add timestamp and call stack info
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.report({'INFO'}, f"🚀 EXECUTE_START [{timestamp}] - Combined flip operator starting")
        
        # Log call stack to see what triggered this
        stack = traceback.format_stack()
        self.report({'INFO'}, f"📋 CALL_STACK: Called from {len(stack)} levels deep")
        for i, frame in enumerate(stack[-3:]):  # Show last 3 stack frames
            self.report({'INFO'}, f"  [{i}] {frame.strip()}")
        
        # Safety check: prevent duplicate operations
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for mesh in selected_meshes:
            # Check if mirrored version already exists
            from ..utils.naming import get_opposite_name
            expected_mirror_name = get_opposite_name(mesh.name, self.mirror_axis)
            if bpy.data.objects.get(expected_mirror_name):
                self.report({'WARNING'}, f"🛡️ SAFETY_CHECK: Mirrored mesh '{expected_mirror_name}' already exists! Skipping operation to prevent duplicates.")
                return {'CANCELLED'}
        
        # Validate input
        errors, warnings = validate_selected_objects()
        
        if errors:
            for error in errors:
                self.report({'ERROR'}, error)
            return {'CANCELLED'}
        
        if warnings:
            for warning in warnings:
                self.report({'WARNING'}, warning)
        
        # Ensure object mode
        mode_error = safe_mode_switch('OBJECT')
        if mode_error:
            self.report({'ERROR'}, mode_error)
            return {'CANCELLED'}
        
        try:
            # Step 1: Store original meshes BEFORE mirroring
            original_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
            timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.report({'INFO'}, f"🔍 STEP_1 [{timestamp}] NEW_SYSTEM: Storing {len(original_meshes)} original meshes for bone analysis")
            
            # Step 2: Mirror meshes first
            mesh_result = self._mirror_meshes(context)
            if not mesh_result:
                return {'CANCELLED'}
            
            # Step 3: Analyze and mirror bone chains using ORIGINAL meshes
            bone_result = self._mirror_bone_chains_from_originals(context, original_meshes)
            
            total_meshes = mesh_result.get('count', 0)
            total_bones = bone_result.get('count', 0)
            
            self.report({'INFO'}, f"Successfully mirrored {total_meshes} mesh(es) and {total_bones} bone(s)")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Operation failed: {str(e)}")
            return {'CANCELLED'}
    
    def _mirror_meshes(self, context):
        """Mirror meshes directly without calling flip_mesh operator to avoid conflicts"""
        self.report({'INFO'}, "NEW_SYSTEM: Mirroring meshes directly...")
        
        # Get selected mesh objects
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_meshes:
            self.report({'ERROR'}, "No mesh objects selected")
            return None
        
        # Store original selection
        original_selection = context.selected_objects.copy()
        original_active = context.active_object
        
        # Track created objects
        created_objects = []
        
        try:
            for mesh_obj in selected_meshes:
                # Select only this mesh
                bpy.ops.object.select_all(action='DESELECT')
                mesh_obj.select_set(True)
                context.view_layer.objects.active = mesh_obj
                
                # Store original name
                original_name = mesh_obj.name
                
                # Duplicate the mesh
                bpy.ops.object.duplicate(linked=False)
                duplicated_obj = context.active_object
                created_objects.append(duplicated_obj)
                
                # Mirror the duplicated object
                constraint_axis = (
                    self.mirror_axis == 'X',
                    self.mirror_axis == 'Y', 
                    self.mirror_axis == 'Z'
                )
                
                bpy.ops.transform.mirror(
                    constraint_axis=constraint_axis,
                    orient_type='GLOBAL'
                )
                
                # Apply transforms if requested
                if self.apply_transforms:
                    bpy.ops.object.transform_apply(
                        location=True,
                        rotation=True,
                        scale=True
                    )
                
                # Handle naming
                if self.auto_rename:
                    from ..utils.naming import get_opposite_name, increment_name
                    new_name = get_opposite_name(original_name, self.mirror_axis)
                    
                    # Check if name already exists
                    if new_name in bpy.data.objects:
                        new_name = increment_name(new_name)
                    duplicated_obj.name = new_name
                
                self.report({'INFO'}, f"NEW_SYSTEM: Created mirrored mesh: {duplicated_obj.name}")
            
            # Handle selection after operation
            if not self.keep_original_selected:
                # Select only the new objects
                bpy.ops.object.select_all(action='DESELECT')
                for obj in created_objects:
                    obj.select_set(True)
                if created_objects:
                    context.view_layer.objects.active = created_objects[0]
            else:
                # Keep original selection and add new objects
                for obj in original_selection:
                    if obj:  # Check if object still exists
                        obj.select_set(True)
                for obj in created_objects:
                    obj.select_set(True)
                
                # Set active object
                if original_active and original_active in bpy.data.objects:
                    context.view_layer.objects.active = original_active
            
            return {'count': len(selected_meshes)}
            
        except Exception as e:
            self.report({'ERROR'}, f"Mesh mirroring failed: {str(e)}")
            
            # Try to clean up created objects on error
            for obj in created_objects:
                if obj and obj.name in bpy.data.objects:
                    try:
                        bpy.data.objects.remove(obj, do_unlink=True)
                    except:
                        pass
            
            return None
    
    def _mirror_bone_chains_from_originals(self, context, original_meshes):
        """Analyze original meshes and mirror their bone chains - NEW CLEAN SYSTEM"""
        import time
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.report({'INFO'}, f"🔧 BONE_CHAINS_START [{timestamp}] - Starting _mirror_bone_chains_from_originals")
        
        if not self.auto_detect_bones:
            self.report({'INFO'}, "NEW_SYSTEM: Bone auto-detection disabled")
            return {'count': 0}
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.report({'INFO'}, f"🔍 STEP_3 [{timestamp}] NEW_SYSTEM: Starting bone chain analysis from original meshes...")
        
        total_mirrored_bones = 0
        
        # Process each original mesh
        for original_mesh in original_meshes:
            self.report({'INFO'}, f"NEW_SYSTEM: Analyzing original mesh '{original_mesh.name}'")
            
            # Get armature relationships for this original mesh
            mesh_armature_pairs = get_mesh_armature_pairs([original_mesh])
            
            if not mesh_armature_pairs:
                self.report({'WARNING'}, f"NEW_SYSTEM: No armature relationship found for '{original_mesh.name}'")
                continue
            
            for mesh_obj, armature_obj in mesh_armature_pairs:
                self.report({'INFO'}, f"NEW_SYSTEM: Processing mesh '{mesh_obj.name}' with armature '{armature_obj.name}'")
                
                # Step 1: Analyze bone chains for this mesh
                bone_chains = analyze_mesh_chains(mesh_obj, armature_obj)
                
                if not bone_chains:
                    self.report({'WARNING'}, f"NEW_SYSTEM: No bone chains found for mesh '{mesh_obj.name}'")
                    continue
                
                # Step 2: Find the corresponding mirrored mesh
                mirrored_mesh = self._find_mirrored_mesh(original_mesh, context)
                if not mirrored_mesh:
                    self.report({'WARNING'}, f"NEW_SYSTEM: Could not find mirrored mesh for '{original_mesh.name}'")
                    continue
                
                # Step 3: Classify and mirror each chain
                for chain in bone_chains:
                    chain_type = classify_bone_chain(chain, self.mirror_axis)
                    mirrored_bones = []
                    
                    if chain_type == "accessory":
                        # Simple accessory mirroring
                        self.report({'INFO'}, f"NEW_SYSTEM: Mirroring accessory chain '{chain.root}'")
                        mirrored_bones = mirror_accessory_chain(chain, armature_obj, self.mirror_axis)
                        
                    elif chain_type == "vrchat_reparent":
                        # VRChat base bone reparenting (e.g., RightKnee → LeftKnee)
                        root_opposite = get_vrchat_opposite_bone(chain.root)
                        self.report({'INFO'}, f"NEW_SYSTEM: VRChat reparenting chain '{chain.root}' → '{root_opposite}'")
                        mirrored_bones = mirror_vrchat_base_reparent_chain(chain, armature_obj, original_mesh, self.mirror_axis, root_opposite)
                        
                    elif chain_type == "base_armature":
                        # Base armature attachment mirroring (fallback)
                        self.report({'INFO'}, f"NEW_SYSTEM: Mirroring base armature chain '{chain.root}'")
                        mirrored_bones = mirror_base_armature_chain(chain, armature_obj, original_mesh, self.mirror_axis)
                    
                    else:
                        self.report({'WARNING'}, f"NEW_SYSTEM: Unknown chain type '{chain_type}' for '{chain.root}'")
                        continue
                    
                    # Step 4: Update vertex groups on MIRRORED mesh and fix bone parenting
                    if mirrored_bones:
                        # Update vertex groups on mirrored mesh
                        update_vertex_groups(mirrored_mesh, chain.bones, mirrored_bones, self.mirror_axis)
                        
                        # Fix bone parenting relationships (SKIP for vrchat_reparent - already handled)
                        if chain_type != "vrchat_reparent":
                            self._fix_bone_parenting(chain.bones, mirrored_bones, armature_obj)
                            self.report({'INFO'}, f"NEW_SYSTEM: Fixed bone parenting for {chain_type} chain '{chain.root}'")
                        else:
                            self.report({'INFO'}, f"NEW_SYSTEM: Skipped bone parenting fix for vrchat_reparent chain '{chain.root}' - already handled by VRChat reparenting logic")
                        
                        # Update shape key names on mirrored mesh
                        self._update_shape_key_names(mirrored_mesh, chain.bones, mirrored_bones)
                        
                        total_mirrored_bones += len(mirrored_bones)
                        self.report({'INFO'}, f"NEW_SYSTEM: Chain '{chain.root}' → {len(mirrored_bones)} bones mirrored")
        
        self.report({'INFO'}, f"NEW_SYSTEM: Bone chain analysis complete - {total_mirrored_bones} bones mirrored")
        return {'count': total_mirrored_bones}
    
    def _find_mirrored_mesh(self, original_mesh, context):
        """Find the mirrored mesh object using improved logic"""
        from ..utils.naming import get_opposite_name
        
        # Use the same naming logic as the mesh mirroring
        expected_name = get_opposite_name(original_mesh.name, self.mirror_axis)
        
        # Check if the exact name exists
        mirrored_mesh = bpy.data.objects.get(expected_name)
        if mirrored_mesh and mirrored_mesh.type == 'MESH':
            self.report({'INFO'}, f"NEW_SYSTEM: Found mirrored mesh '{expected_name}' for '{original_mesh.name}'")
            return mirrored_mesh
        
        # Fallback 1: Check with incremented name (e.g., .001)
        from ..utils.naming import increment_name
        if expected_name in bpy.data.objects:
            incremented_name = increment_name(expected_name)
            mirrored_mesh = bpy.data.objects.get(incremented_name)
            if mirrored_mesh and mirrored_mesh.type == 'MESH':
                self.report({'INFO'}, f"NEW_SYSTEM: Found mirrored mesh '{incremented_name}' for '{original_mesh.name}'")
                return mirrored_mesh
        
        # Fallback 2: Look for any mesh that starts with the original name but is different
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                obj != original_mesh and 
                obj.name.startswith(original_mesh.name) and
                obj.name != original_mesh.name):
                self.report({'INFO'}, f"NEW_SYSTEM: Found potential mirrored mesh '{obj.name}' for '{original_mesh.name}' (fallback)")
                return obj
        
        self.report({'WARNING'}, f"NEW_SYSTEM: Could not find mirrored mesh for '{original_mesh.name}' (expected: '{expected_name}')")
        return None
    
    def _fix_bone_parenting(self, original_bones, mirrored_bones, armature_obj):
        """Fix bone parenting relationships for mirrored bones"""
        self.report({'INFO'}, f"NEW_SYSTEM: Fixing bone parenting for {len(mirrored_bones)} bones")
        
        # Create mapping from original to mirrored bone names
        bone_mapping = {orig: mir for orig, mir in zip(original_bones, mirrored_bones)}
        
        # Enter edit mode to modify bone parenting
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        try:
            edit_bones = armature_obj.data.edit_bones
            
            for orig_bone_name, mir_bone_name in bone_mapping.items():
                orig_bone = edit_bones.get(orig_bone_name)
                mir_bone = edit_bones.get(mir_bone_name)
                
                if orig_bone and mir_bone and orig_bone.parent:
                    # Get original parent name
                    orig_parent_name = orig_bone.parent.name
                    
                    # Find mirrored parent (try mapping first, then assume same name for base bones)
                    mir_parent_name = bone_mapping.get(orig_parent_name, orig_parent_name)
                    mir_parent = edit_bones.get(mir_parent_name)
                    
                    if mir_parent:
                        mir_bone.parent = mir_parent
                        self.report({'INFO'}, f"NEW_SYSTEM: Parented '{mir_bone_name}' to '{mir_parent_name}'")
                    else:
                        self.report({'WARNING'}, f"NEW_SYSTEM: Could not find parent '{mir_parent_name}' for '{mir_bone_name}'")
        
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
    
    def _update_shape_key_names(self, mirrored_mesh, original_bones, mirrored_bones):
        """Update shape key names on mirrored mesh to reference mirrored bone names"""
        if not mirrored_mesh.data.shape_keys:
            return
        
        self.report({'INFO'}, f"NEW_SYSTEM: Updating shape key names for '{mirrored_mesh.name}'")
        
        # Create mapping from original to mirrored bone names
        bone_mapping = {orig: mir for orig, mir in zip(original_bones, mirrored_bones)}
        
        shape_keys = mirrored_mesh.data.shape_keys.key_blocks
        updated_count = 0
        
        for shape_key in shape_keys:
            if shape_key.name == 'Basis':
                continue
                
            # Check if shape key name matches any original bone name
            for orig_bone_name, mir_bone_name in bone_mapping.items():
                if orig_bone_name in shape_key.name:
                    old_name = shape_key.name
                    new_name = shape_key.name.replace(orig_bone_name, mir_bone_name)
                    shape_key.name = new_name
                    self.report({'INFO'}, f"NEW_SYSTEM: Updated shape key '{old_name}' → '{new_name}'")
                    updated_count += 1
                    break
        
        self.report({'INFO'}, f"NEW_SYSTEM: Updated {updated_count} shape key names")

    def draw(self, context):
        """Operator UI"""
        layout = self.layout
        
        layout.prop(self, "mirror_axis")
        layout.prop(self, "auto_detect_bones")
        layout.prop(self, "apply_transforms")
        layout.prop(self, "auto_rename")
        layout.prop(self, "keep_original_selected")


# Registration
classes = (
    OBJECT_OT_flip_mesh_and_bones_combined,
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