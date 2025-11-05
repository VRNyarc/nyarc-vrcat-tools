# Dependency Bundling Guide

**For Developers**: How to bundle scipy and robust-laplacian with the addon

---

## User Experience (Automatic)

Users don't need to do anything manually! When they:
1. Enable "Use Robust Transfer"
2. If dependencies missing → See "Install Dependencies" button
3. Click button → Waits 30-60 seconds
4. Restart Blender → Ready to use!

The installer downloads and bundles dependencies locally - no system-wide installation.

---

## How It Works (Technical)

### 1. Local Dependencies Folder

Dependencies are stored in:
```
shapekey_transfer/robust/deps/
├── scipy/
├── robust_laplacian/
└── ... (their dependencies)
```

### 2. sys.path Setup

`robust/__init__.py` adds `deps/` to Python path:
```python
deps_path = os.path.join(os.path.dirname(__file__), 'deps')
if os.path.exists(deps_path) and deps_path not in sys.path:
    sys.path.insert(0, deps_path)
```

### 3. Conditional Import

Only imports functionality if dependencies available:
```python
if not missing_deps:
    from .core import transfer_shape_key_robust
    DEPENDENCIES_AVAILABLE = True
else:
    DEPENDENCIES_AVAILABLE = False
```

### 4. Installer Operator

`robust/installer.py` provides one-click installation:
```python
subprocess.check_call([
    sys.executable,
    "-m", "pip", "install",
    "--target", deps_dir,
    "--no-deps",
    package
])
```

The `--target` flag installs to local `deps/` folder.

---

## Manual Bundling (For Distribution)

If you want to pre-bundle dependencies for release:

### Option A: Direct pip install

```bash
cd shapekey_transfer/robust
mkdir deps
python -m pip install --target deps --no-deps scipy robust-laplacian
```

### Option B: Platform-specific wheels

For cross-platform distribution:

```bash
# Download platform-specific wheels
pip download --platform win_amd64 --python-version 311 --only-binary=:all: --no-deps -d wheels scipy robust-laplacian

# Extract wheels into deps/
cd wheels
for file in *.whl; do
    unzip -o "$file" -d ../deps/
done
```

### Option C: Use the installer in Blender

1. Load addon in Blender
2. Enable robust transfer
3. Click "Install Dependencies"
4. Copy generated `deps/` folder to distribution

---

## Dependencies Overview

### scipy (~30MB)
- **Purpose**: Sparse matrix operations, KD-tree
- **Used in**: `correspondence.py` (BVH tree), `inpainting.py` (sparse solver)
- **License**: BSD-3-Clause ✅ (compatible)

### robust-laplacian (~50KB)
- **Purpose**: Cotangent-weighted Laplacian construction
- **Used in**: `inpainting.py` (geometry-aware weights)
- **License**: MIT ✅ (compatible)

**Total size**: ~30-35MB (acceptable for Blender addon)

---

## License Compliance

### Our Addon
- **License**: GPL-3.0 (or your chosen license)
- **Bundling**: Allowed for GPL/MIT/BSD libraries ✅

### Dependencies
- **scipy**: BSD-3-Clause (permissive, compatible)
- **robust-laplacian**: MIT (permissive, compatible)

**Conclusion**: No license conflicts - free to bundle!

---

## Testing Bundled Dependencies

### 1. Fresh Blender Install
Test on clean Blender without scipy pre-installed:
```python
import sys
print(sys.path)  # Should show our deps/ folder
import scipy  # Should work
```

### 2. Verify Isolation
Ensure bundled version doesn't conflict with system scipy:
```python
import scipy
print(scipy.__file__)  # Should point to our deps/ folder
```

### 3. Functionality Test
Run actual transfer to verify scipy.sparse works correctly.

---

## Distribution Checklist

When packaging addon for release:

- [ ] `deps/` folder included in ZIP
- [ ] Test on fresh Blender install
- [ ] Test on all target platforms (Win/Mac/Linux)
- [ ] Verify installer works if deps/ missing
- [ ] Document in README that first use may require internet

---

## Troubleshooting

### "Import Error" after installation

**Cause**: Blender needs restart to reload Python modules

**Solution**: Tell user to restart Blender (installer already does this)

### "pip not found"

**Cause**: Blender's Python doesn't have pip (rare)

**Solution**: Installer shows manual commands in console

### Different Python versions

**Cause**: scipy wheels are Python-version-specific

**Solution**: Use `--python-version` flag when pre-bundling, or let installer handle it automatically

---

## Alternative: Ship Pre-Bundled

For easiest user experience, pre-bundle dependencies in releases:

1. Run installer once on each platform (Win/Mac/Linux)
2. Copy generated `deps/` folders
3. Include in release ZIP for each platform

Users get zero-setup experience - just install addon and go!

---

## Summary

**User Experience**: One-click install button, 30 seconds, restart Blender
**Developer Experience**: Either pre-bundle or let installer handle it
**License**: All clear, free to bundle
**Size**: ~30-35MB (reasonable for addon)

Same approach as original robust-weight-transfer addon - battle-tested and user-friendly!
