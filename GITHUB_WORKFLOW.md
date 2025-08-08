# GitHub Release Workflow - NYARC VRChat Tools

**📂 Location**: `Y:\ClaudeWINDOWS\projects\blender_tools_project\GITHUB_WORKFLOW.md`  
**🎯 Purpose**: Complete GitHub release process documentation for Claude Code sessions

---

## 🚀 Quick Release Commands

### **One-Command Release Process**
```bash
# Development complete → Release
cd Y:\ClaudeWINDOWS\projects\blender_tools_project
python scripts/release.py minor
git push origin main $(git describe --tags --abbrev=0)
```

### **Release Types**
- `python scripts/release.py patch` → 1.0.0 → 1.0.1 (bug fixes)
- `python scripts/release.py minor` → 1.0.1 → 1.1.0 (new features)  
- `python scripts/release.py major` → 1.1.0 → 2.0.0 (breaking changes)

---

## 📁 Repository Structure

### **GitHub Repository Layout**
```
nyarc-vrcat-tools/              # GitHub repository root
├── nyarc_vrcat_tools/          # Addon folder (from local project)
│   ├── __init__.py             # Contains version info
│   ├── bone_transform_saver.py
│   └── [all addon modules...]
├── .github/workflows/
│   └── release.yml             # Auto-build on version tags
├── scripts/
│   └── release.py              # Local release automation
├── docs/
│   ├── installation.md
│   └── user-guide.md
├── README.md
├── CHANGELOG.md                # Auto-generated from commits
├── LICENSE
├── blender_manifest.toml       # Blender 4.2+ requirement
└── .gitignore
```

### **Files to Copy from Local Project**
- **INCLUDE**: `nyarc_vrcat_tools/` folder (entire addon)
- **EXCLUDE**: `exported_zips/`, local development files, `Y:\ClaudeWINDOWS\` workspace

---

## 🔄 Complete Release Workflow

### **1. Local Development** (Current Process)
```bash
cd Y:\ClaudeWINDOWS\projects\blender_tools_project
# Make changes to nyarc_vrcat_tools/
python export_addon.py --name "test_build"  # Local testing
```

### **2. Prepare GitHub Release**
```bash
# Automated version bump + changelog
python scripts/release.py minor

# What this script does:
# ✅ Updates version in __init__.py: "version": (1, 1, 0)
# ✅ Updates blender_manifest.toml: version = "1.1.0"  
# ✅ Generates changelog from git commits since last tag
# ✅ Updates CHANGELOG.md with new version entry
# ✅ Creates git commit: "release: v1.1.0"
# ✅ Creates git tag: v1.1.0
```

### **3. Trigger GitHub Release**
```bash
git push origin main v1.1.0

# GitHub CI/CD automatically:
# ✅ Runs export process (builds nyarc_vrcat_tools ZIP)
# ✅ Creates GitHub release with version tag
# ✅ Attaches ZIP file as downloadable asset
# ✅ Generates release notes from CHANGELOG.md
```

---

## 🤖 GitHub Actions Configuration

### **`.github/workflows/release.yml`**
```yaml
name: Build and Release Addon
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Build Addon ZIP
      run: |
        python -c "
        import zipfile, os
        with zipfile.ZipFile('nyarc-vrcat-tools-${{ github.ref_name }}.zip', 'w') as z:
            for root, dirs, files in os.walk('nyarc_vrcat_tools'):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                for file in files:
                    if file.endswith('.py'):
                        path = os.path.join(root, file)
                        z.write(path, path)
        "
        
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: nyarc-vrcat-tools-${{ github.ref_name }}.zip
        generate_release_notes: true
        body_path: CHANGELOG.md
```

---

## 📝 Changelog Generation

### **Conventional Commits** (for better changelogs)
```bash
git commit -m "feat: add intelligent bone mapping with fuzzy matching"
git commit -m "fix: resolve armature export precision issues"
git commit -m "docs: update installation instructions"
git commit -m "refactor: modularize shape key transfer system"
```

### **Generated Changelog Example**
```markdown
## v1.1.0

### ✨ New Features
- add intelligent bone mapping with fuzzy matching
- implement pose history rollback system

### 🐛 Bug Fixes  
- resolve armature export precision issues
- fix UI panel refresh on preset load

### 🔧 Other Changes
- update installation instructions
- modularize shape key transfer system
```

---

## 🗂️ Version Management

### **Version Locations**
1. **`nyarc_vrcat_tools/__init__.py`**:
   ```python
   bl_info = {
       "name": "NYARC VRChat Tools",
       "version": (1, 1, 0),  # ← Updated by release script
       "blender": (3, 0, 0),
   }
   ```

2. **`blender_manifest.toml`** (Blender 4.2+):
   ```toml
   schema_version = "1.0.0"
   id = "nyarc_vrcat_tools" 
   version = "1.1.0"  # ← Updated by release script
   ```

### **Version Bump Logic**
- **Patch** (1.0.0 → 1.0.1): Bug fixes only
- **Minor** (1.0.1 → 1.1.0): New features, backward compatible
- **Major** (1.1.0 → 2.0.0): Breaking changes, API changes

---

## 🛠️ Release Script Details

### **`scripts/release.py` Functions**
```python
def get_current_version():     # Extract version from __init__.py
def bump_version(current, type): # Calculate new version
def update_version_files(ver): # Update __init__.py + manifest
def generate_changelog():     # Parse git commits since last tag  
```

### **Release Script Output**
```
🚀 Preparing release v1.1.0
📝 Changelog generated:
### ✨ New Features
- add bone mapping system
- implement pose history

✅ Ready to release! Run: git push origin main v1.1.0
```

---

## 🚨 Troubleshooting

### **Common Issues**
1. **"Version not found"**: Check `__init__.py` bl_info format
2. **"No git tags"**: First release - script handles this gracefully
3. **"CI/CD failed"**: Check GitHub Actions tab for build logs
4. **"ZIP missing files"**: Verify nyarc_vrcat_tools/ structure

### **Manual Recovery**
```bash
# If release script fails
git tag -d v1.1.0              # Delete local tag
git reset --hard HEAD~1        # Undo release commit
# Fix issues, then re-run release script
```

---

## 📋 Claude Code Session Workflow

### **When Starting Fresh Session** (`/clear` recovery)
1. **Reference this file**: `Read "Y:\ClaudeWINDOWS\projects\blender_tools_project\GITHUB_WORKFLOW.md"`
2. **Understand current state**: Check git status, last version
3. **Continue development**: Make changes to `nyarc_vrcat_tools/`
4. **Release when ready**: Use automated release script

### **Key Commands for Claude**
```bash
# Check current version
grep '"version":' nyarc_vrcat_tools/__init__.py

# Check git status  
git status
git log --oneline -5

# Prepare release
python scripts/release.py [major|minor|patch]

# Push release
git push origin main $(git describe --tags --abbrev=0)
```

---

## 🎯 Success Indicators

### **Successful Release Checklist**
- ✅ Local testing with `python export_addon.py` works
- ✅ Release script completes without errors  
- ✅ Git tag created: `git tag -l`
- ✅ GitHub Actions build succeeds
- ✅ Release appears on GitHub with downloadable ZIP
- ✅ CHANGELOG.md updated with new version

### **User Experience**
- Users visit: `https://github.com/username/nyarc-vrcat-tools/releases`
- Download: `nyarc-vrcat-tools-v1.1.0.zip`
- Install in Blender: Edit → Preferences → Add-ons → Install...

---

**🔗 This workflow ensures consistent, professional releases with minimal manual effort while maintaining full traceability and documentation.**