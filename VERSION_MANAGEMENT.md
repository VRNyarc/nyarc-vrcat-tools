# Version Management System - NYARC VRChat Tools

**📂 Location**: `Y:\ClaudeWINDOWS\projects\blender_tools_project\VERSION_MANAGEMENT.md`  
**🎯 Purpose**: Complete documentation of automated version management for `/clear` recovery

---

## 🚨 CRITICAL SYSTEM OVERVIEW

### **Intelligent GitHub Tag-Based Versioning**
- **System**: Automated release script that reads GitHub releases (NOT file versions)
- **Location**: `Y:\ClaudeWINDOWS\projects\blender_tools_project\github_repo\scripts\release.py`
- **Current Version**: 0.0.1 (ready for first release)
- **Repository**: https://github.com/VRNyarc/nyarc-vrcat-tools

---

## 🏷️ VERSION FILES TRACKING

### **Primary Version Locations**
1. **`nyarc_vrcat_tools/__init__.py`**:
   ```python
   "version": (0, 0, 1),  # Tuple format for Blender
   ```

2. **`blender_manifest.toml`**:
   ```toml
   version = "0.0.1"  # String format for Blender 4.2+
   ```

3. **UI Display** (in `__init__.py`):
   ```python
   header_row.label(text="Nyarc VRCat Tools v0.0.1", icon='TOOL_SETTINGS')
   ```

### **🚨 IMPORTANT**: Script Updates ALL Files Automatically

---

## 🤖 AUTOMATED RELEASE SCRIPT

### **Script Logic Flow**
```bash
cd Y:\ClaudeWINDOWS\projects\blender_tools_project\github_repo
python scripts/release.py [patch|minor|major]
```

1. **Check GitHub Tags**: `git tag -l --sort=-version:refname`
2. **Find Latest Release**: e.g., `v0.0.1` (NOT file versions)
3. **Calculate Next Version**: Based on increment type
4. **Update Files**: `__init__.py`, `blender_manifest.toml`, UI text
5. **Generate Changelog**: From git commits since last release
6. **Create Commit**: `"release: v0.0.2"`
7. **Create Tag**: `v0.0.2`

### **Version Increment Examples**
```bash
# Starting from v0.0.1 on GitHub:
python scripts/release.py patch  # → v0.0.2 (bug fixes)
python scripts/release.py minor  # → v0.1.0 (new features)
python scripts/release.py major  # → v1.0.0 (breaking changes)

# First release (no tags exist):
python scripts/release.py patch  # → v0.0.1
```

---

## 🚀 GITHUB ACTIONS INTEGRATION

### **Trigger**: Version Tag Push
```bash
git push origin main v0.0.1  # Triggers automated build
```

### **Workflow File**: `.github/workflows/release.yml`
- **Builds**: `nyarc-vrcat-tools-v0.0.1.zip` 
- **Creates**: GitHub release with download
- **Includes**: Changelog and installation instructions

---

## 📋 CLAUDE CODE RECOVERY COMMANDS

### **Check Current State**
```bash
cd Y:\ClaudeWINDOWS\projects\blender_tools_project\github_repo

# Check current file version
grep '"version":' nyarc_vrcat_tools/__init__.py

# Check latest GitHub releases  
git tag -l --sort=-version:refname

# Check git status
git status
```

### **Test Release Script**
```bash
# Dry run (shows what would happen)
python scripts/release.py patch --dry-run
```

### **Create Release**
```bash
# Prepare release (auto-creates commit + tag)
python scripts/release.py patch

# Push to GitHub (triggers build)
git push origin main v0.0.2  # Use actual version from script
```

### **Export for Local Testing**
```bash
cd Y:\ClaudeWINDOWS\projects\blender_tools_project
python export_addon.py --name "test_v001"
```

---

## 🔄 VERSION HISTORY TRACKING

### **Current Status** (as of December 2024)
- **File Version**: 0.0.1 (set for first release)
- **GitHub Releases**: None yet (first release pending)
- **Next Release**: Will be v0.0.1 (first release)

### **Release Progression Logic**
```
No GitHub tags → v0.0.1 (first release)
v0.0.1 → v0.0.2 (patch)
v0.0.1 → v0.1.0 (minor)
v0.0.1 → v1.0.0 (major)
```

---

## 🛠️ COMPANION MODULE STATUS

### **GitHub URLs Updated** ✅
- Documentation: `https://github.com/VRNyarc/nyarc-vrcat-tools#readme`
- Support: `https://github.com/VRNyarc/nyarc-vrcat-tools/issues`
- Repository: `https://github.com/VRNyarc/nyarc-vrcat-tools`

### **Tool Categories Verified** ✅
- Mesh Tools: Shape key transfer, deformation mapping
- Armature Tools: Bone transforms, presets, diff export
- Workflow Tools: Integration helpers, companion tool support
- Quality Tools: Precision correction, compatibility checking

---

## 🚨 TROUBLESHOOTING

### **Common Issues**
1. **"No tags found"**: Normal for first release
2. **Unicode errors**: Script handles Windows console encoding
3. **Git errors**: Ensure in `github_repo` directory
4. **Version mismatch**: Script ignores file versions, uses GitHub tags

### **Recovery After `/clear`**
1. **Read this file**: `Read "Y:\ClaudeWINDOWS\projects\blender_tools_project\github_repo\VERSION_MANAGEMENT.md"`
2. **Check git status**: See if commits need pushing
3. **Verify version files**: Should be 0.0.1 for first release
4. **Test release script**: `python scripts/release.py patch --dry-run`

---

## 📦 FIRST RELEASE READINESS

### **✅ READY FOR FIRST RELEASE**
- [x] Version files set to 0.0.1
- [x] Release script created and tested
- [x] GitHub Actions workflow configured
- [x] Companion module GitHub URLs fixed
- [x] Tool categories verified and accurate
- [x] Bone mapping system completed and tested
- [x] Export system working (63 Python files)

### **🚀 FIRST RELEASE COMMAND**
```bash
cd Y:\ClaudeWINDOWS\projects\blender_tools_project\github_repo
python scripts/release.py patch  # Creates v0.0.1
git push origin main v0.0.1      # Triggers GitHub release
```

---

**🔗 This document ensures complete `/clear` recovery capability for version management and release processes.**