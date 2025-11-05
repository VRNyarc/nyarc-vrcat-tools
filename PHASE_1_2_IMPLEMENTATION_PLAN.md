# Phase 1 & 2 Implementation Plan
## Systematic Implementation Strategy

**Branch:** `claude/review-project-structure-011CUq2CtqkX7tvaBpFMXbEG`
**Estimated Total Time:** 8-12 hours
**Approach:** Systematic, file-by-file implementation with verification

---

## 🎯 IMPLEMENTATION STRATEGY

### Principles
1. **One file at a time** - Complete each file before moving to next
2. **Test after each major change** - Ensure addon still loads
3. **Commit frequently** - Small, focused commits
4. **Preserve functionality** - Don't break existing features

### Order of Implementation
1. **Phase 1 First** - Fix bare excepts (foundation for good error handling)
2. **Phase 2.4** - Extract utilities (needed for validation)
3. **Phase 2.3** - Add validation (uses new utilities)
4. **Phase 2.1** - Add poll methods (uses validation)
5. **Phase 2.2** - Fix naming (cosmetic, safe to do last)

---

## 📋 PHASE 1: REPLACE BARE EXCEPT BLOCKS

### Files to Fix (25 files, 54 occurrences)

#### Priority 1: Operators (Highest Impact)
1. `bone_transforms/operators/apply_rest.py` - 4 occurrences
2. `bone_transforms/operators/inherit_scale.py` - 7 occurrences
3. `shapekey_transfer/operators/transfer_ops.py` - 1 occurrence
4. `mirror_flip/operators/flip_combined.py` - 2 occurrences
5. `mirror_flip/operators/flip_bones.py` - 2 occurrences
6. `mirror_flip/operators/flip_mesh.py` - 2 occurrences

#### Priority 2: Core Systems
7. `bone_transforms/pose_history/metadata_storage.py` - 6 occurrences
8. `bone_transforms/pose_history/operators.py` - 1 occurrence
9. `bone_transforms/precision/correction_engine.py` - 1 occurrence
10. `bone_transforms/diff_export/transforms_diff.py` - 1 occurrence

#### Priority 3: UI & Utils
11. `bone_transforms/ui/pose_controls.py` - 1 occurrence
12. `bone_transforms/presets/ui.py` - 2 occurrences
13. `shapekey_transfer/utils/preprocessing.py` - 1 occurrence
14. `mirror_flip/ui/panels.py` - 2 occurrences
15. `mirror_flip/utils/chain_analysis.py` - 1 occurrence
16. `mirror_flip/utils/simple_mirroring.py` - 4 occurrences

#### Priority 4: Module System
17. `__init__.py` - 2 occurrences
18. `modules.py` - 6 occurrences
19. `bone_transform_saver.py` - 1 occurrence
20. `details_companion_tools.py` - 1 occurrence

### Replacement Patterns

#### Pattern 1: Property Access
```python
# Before:
try:
    props = context.scene.nyarc_tools_props
except:
    props = None

# After:
try:
    props = context.scene.nyarc_tools_props
except (AttributeError, KeyError):
    props = None
```

#### Pattern 2: Blender Operations
```python
# Before:
try:
    bpy.ops.object.mode_set(mode='OBJECT')
except:
    pass

# After:
try:
    bpy.ops.object.mode_set(mode='OBJECT')
except (RuntimeError, TypeError) as e:
    print(f"Failed to set mode: {e}")
```

#### Pattern 3: Module Imports
```python
# Before:
try:
    from .some_module import function
except:
    function = None

# After:
try:
    from .some_module import function
except ImportError as e:
    print(f"Optional module not available: {e}")
    function = None
```

#### Pattern 4: Cleanup/Unregister
```python
# Before:
try:
    bpy.utils.unregister_class(cls)
except:
    pass

# After:
try:
    bpy.utils.unregister_class(cls)
except (RuntimeError, ValueError):
    pass  # Class not registered, safe to ignore
```

---

## 📋 PHASE 2.4: EXTRACT DUPLICATE CODE (Foundation)

### Create Core Utilities Module

#### File 1: `core/validation.py`
```python
"""Shared validation utilities for all operators."""

def validate_scene_props(context, operator=None):
    """Validate scene properties exist."""
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        if operator:
            operator.report({'ERROR'}, "Addon properties not initialized")
        return None
    return props

def validate_armature(armature_obj, operator=None, check_valid=True):
    """Validate armature object."""
    if not armature_obj:
        if operator:
            operator.report({'ERROR'}, "No armature selected")
        return False

    if check_valid and armature_obj.name not in bpy.data.objects:
        if operator:
            operator.report({'ERROR'}, "Armature no longer exists")
        return False

    if armature_obj.type != 'ARMATURE':
        if operator:
            operator.report({'ERROR'}, f"Object '{armature_obj.name}' is not an armature")
        return False

    return True

def validate_mesh(mesh_obj, operator=None, check_valid=True):
    """Validate mesh object."""
    if not mesh_obj:
        if operator:
            operator.report({'ERROR'}, "No mesh selected")
        return False

    if check_valid and mesh_obj.name not in bpy.data.objects:
        if operator:
            operator.report({'ERROR'}, "Mesh no longer exists")
        return False

    if mesh_obj.type != 'MESH':
        if operator:
            operator.report({'ERROR'}, f"Object '{mesh_obj.name}' is not a mesh")
        return False

    return True
```

#### File 2: `core/mode_utils.py`
```python
"""Safe mode switching utilities."""
import bpy
from contextlib import contextmanager

@contextmanager
def safe_mode_switch(obj, target_mode):
    """Context manager for safe mode switching."""
    if not obj:
        yield False
        return

    original_mode = obj.mode if hasattr(obj, 'mode') else None
    original_active = bpy.context.view_layer.objects.active

    try:
        # Set as active and switch mode
        bpy.context.view_layer.objects.active = obj
        if target_mode != obj.mode:
            bpy.ops.object.mode_set(mode=target_mode)
        yield True
    except (RuntimeError, TypeError, AttributeError) as e:
        print(f"Mode switch failed: {e}")
        yield False
    finally:
        # Restore original state
        try:
            if original_mode and obj.mode != original_mode:
                bpy.ops.object.mode_set(mode=original_mode)
            if original_active:
                bpy.context.view_layer.objects.active = original_active
        except (RuntimeError, TypeError, AttributeError):
            pass  # Best effort restoration
```

#### File 3: `core/bone_utils.py`
```python
"""Bone iteration and common bone operations."""

def iter_bones(armature, mode='EDIT'):
    """Iterate over bones in armature (mode-aware)."""
    if not armature or armature.type != 'ARMATURE':
        return []

    if mode == 'EDIT':
        return armature.data.edit_bones
    elif mode == 'POSE':
        return armature.pose.bones
    else:  # DATA
        return armature.data.bones

def get_bone(armature, bone_name, mode='EDIT'):
    """Get bone by name (mode-aware)."""
    bones = iter_bones(armature, mode)
    return bones.get(bone_name) if bones else None
```

---

## 📋 PHASE 2.3: ADD INPUT VALIDATION

### Validation Checklist for Each Operator

#### Standard Validation Pattern
```python
def execute(self, context):
    # 1. Validate scene properties
    props = validate_scene_props(context, self)
    if not props:
        return {'CANCELLED'}

    # 2. Validate required objects
    armature = props.bone_armature_object
    if not validate_armature(armature, self):
        return {'CANCELLED'}

    # 3. Validate specific requirements
    if not armature.data.bones:
        self.report({'ERROR'}, "Armature has no bones")
        return {'CANCELLED'}

    # 4. Proceed with operation
    ...
```

### Files Requiring Validation (Priority Order)
1. All bone_transforms/operators/*.py files
2. All shapekey_transfer/operators/*.py files
3. All mirror_flip/operators/*.py files

---

## 📋 PHASE 2.1: ADD POLL METHODS

### Poll Method Templates

#### Template 1: Armature Required
```python
@classmethod
def poll(cls, context):
    """Only available when armature is selected."""
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        return False

    armature = props.bone_armature_object
    return (armature is not None and
            armature.type == 'ARMATURE' and
            armature.name in bpy.data.objects)
```

#### Template 2: Mesh Required
```python
@classmethod
def poll(cls, context):
    """Only available when mesh is selected."""
    props = getattr(context.scene, 'nyarc_tools_props', None)
    if not props:
        return False

    mesh = props.shapekey_source_object
    return (mesh is not None and
            mesh.type == 'MESH' and
            mesh.name in bpy.data.objects)
```

#### Template 3: Specific Mode Required
```python
@classmethod
def poll(cls, context):
    """Only available in OBJECT mode."""
    return context.mode == 'OBJECT'
```

#### Template 4: Pose Mode + Armature
```python
@classmethod
def poll(cls, context):
    """Only available in pose mode with armature."""
    if context.mode != 'POSE':
        return False

    obj = context.active_object
    return obj is not None and obj.type == 'ARMATURE'
```

### Operators Needing Poll Methods (47 total)
- bone_transforms/operators/: ~20 operators
- shapekey_transfer/operators/: ~10 operators
- mirror_flip/operators/: ~8 operators
- bone_transforms/pose_history/: ~4 operators
- bone_transforms/presets/: ~5 operators

---

## 📋 PHASE 2.2: FIX NAMING INCONSISTENCY

### Files to Update

#### Python Files (Use "VRChat" everywhere)
1. `__init__.py` - bl_info name and description
2. `blender_manifest.toml` - Already correct
3. All UI strings mentioning "VRCat"
4. All comments and docstrings

#### Search and Replace Pattern
```bash
# Find all occurrences
grep -r "VRCat" --include="*.py" nyarc_vrcat_tools/

# Replace (case-sensitive)
VRCat → VRChat
vrcat → vrchat (in comments/strings only, NOT in file/package names)
```

#### KEEP UNCHANGED
- Package name: `nyarc_vrcat_tools` (breaking change)
- Directory name: `nyarc_vrcat_tools/` (breaking change)
- Import statements: `from nyarc_vrcat_tools`

#### UPDATE
- User-visible strings: "Nyarc VRChat Tools"
- Comments: "for VRChat avatars"
- Documentation: "VRChat compatibility"
- bl_info['name']: "Nyarc VRChat Tools"

---

## 🔄 IMPLEMENTATION ORDER

### Day 1 (4-5 hours)
1. ✅ Create core utilities (validation.py, mode_utils.py, bone_utils.py)
2. ✅ Fix bare excepts in operators (Priority 1 files)
3. ✅ Test: Addon loads, operators work
4. ✅ Commit: "refactor: add core utilities and fix bare excepts in operators"

### Day 2 (3-4 hours)
5. ✅ Fix remaining bare excepts (Priority 2-4 files)
6. ✅ Add validation to bone_transforms operators
7. ✅ Test: Bone operations work correctly
8. ✅ Commit: "fix: complete bare except replacement and add operator validation"

### Day 3 (2-3 hours)
9. ✅ Add poll methods to bone_transforms operators
10. ✅ Add validation + poll to shapekey_transfer operators
11. ✅ Test: UI correctly enables/disables operators
12. ✅ Commit: "feat: add poll methods and validation to operators"

### Day 4 (2-3 hours)
13. ✅ Add poll methods to mirror_flip operators
14. ✅ Fix VRCat → VRChat naming throughout
15. ✅ Test: Full addon functionality
16. ✅ Commit: "style: standardize naming to VRChat throughout"

### Day 5 (1-2 hours)
17. ✅ Final testing and verification
18. ✅ Update CHANGELOG.md
19. ✅ Final commit: "docs: update changelog for Phase 1 & 2 completion"

---

## ✅ VERIFICATION CHECKLIST

### After Each Major Change
- [ ] Addon loads without errors
- [ ] No registration errors in console
- [ ] Operators appear in correct contexts
- [ ] Error messages are helpful
- [ ] No crashes on invalid input

### Final Verification
- [ ] All 54 bare excepts replaced
- [ ] All 47 operators have poll methods
- [ ] All operators validate inputs
- [ ] Core utilities working correctly
- [ ] Consistent VRChat naming
- [ ] No regression in functionality

---

## 📝 COMMIT STRATEGY

### Small, Focused Commits
1. `refactor: create core validation utilities`
2. `fix: replace bare excepts in bone_transforms operators`
3. `fix: replace bare excepts in shapekey_transfer`
4. `fix: replace bare excepts in mirror_flip`
5. `fix: replace remaining bare excepts in core modules`
6. `feat: add input validation to bone_transforms operators`
7. `feat: add poll methods to bone_transforms operators`
8. `feat: add validation and poll methods to shapekey_transfer`
9. `feat: add validation and poll methods to mirror_flip`
10. `style: standardize VRChat naming throughout codebase`
11. `docs: update changelog for Phase 1 & 2 completion`

---

## 🎯 SUCCESS CRITERIA

### Phase 1 Complete When:
- ✅ Zero bare `except:` blocks remain
- ✅ All exceptions are specific types
- ✅ Error messages are logged/reported
- ✅ Addon loads without errors

### Phase 2 Complete When:
- ✅ All operators have poll methods
- ✅ Operators only enabled in valid contexts
- ✅ All operators validate inputs before executing
- ✅ Helpful error messages on invalid input
- ✅ Consistent "VRChat" naming everywhere
- ✅ Core utilities extracted and reusable

---

**Ready to begin systematic implementation!**
