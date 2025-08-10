# Changelog

All notable changes to NYARC VRChat Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## v0.1.0 (2025-08-11)

### New Features
* feat: initial project structure and professional Blender addon
* docs: add comprehensive version management documentation for /clear recovery
* feat: improve UI layout and add optional XZ scaling analysis

### Bug Fixes
* docs: improve README feature descriptions and fix typos
* docs: fix Bone Transform Saver description to accurately reflect CATS-like functionality
* fix: resolve inherit scale mixed case overscaling and mode switching errors

### Other Changes
* Initial commit
* docs: update Blender requirement to 4.2+ and remove Discord references
* docs: remove internal GitHub workflow documentation from public repo
* Update README.md
* Update README.md
* Major bone mapping improvements for VRChat compatibility
* Update companion module for first release preparation
* Merge branch 'main' of https://github.com/VRNyarc/nyarc-vrcat-tools
* Setup automated version management and release system
* remove: VERSION_MANAGEMENT.md from repo (belongs in project root)
* release: v0.0.1
* release: v0.1.0
* docs: improve changelog with user-focused content
* release: v0.1.1


## v0.1.1 (2025-08-10)

### 🐛 Critical Bug Fixes
* **Fixed inherit scale mixed case overscaling** - Flattening algorithm now respects individual bone inherit_scale settings
* **Resolved mode switching errors** - Added safe mode switching with retry logic for drawing/rendering states
* **Fixed missing variable error** - Added inherit_scale_settings reading logic to flatten_bone_transforms_for_save
* **Prevented overscaling** - Bones with inherit_scale=NONE now keep their original scale during apply rest pose
* **Eliminated "can't modify blend data" errors** - Safer mode transitions prevent Blender state conflicts

### 🔧 Technical Improvements  
* Enhanced error handling with retry logic and proper fallbacks
* Better debugging output for inheritance flattening operations
* Improved robustness in mixed inherit scale scenarios


## v0.1.0 (2025-08-10)

### 🎨 UI Improvements
* **Always-visible Armature Diff Export** - No longer hidden when no bones selected
* **Improved Quick Start Guide** - Now explains Transform Presets and Armature Diff Export
* **Better UI layout** - Quick Start Guide moved to bottom for consistent placement

### ✨ New Features  
* **Optional X/Z Scaling Analysis** - New checkbox for experimental mesh vertex analysis
* **Y-only Scaling Mode** - Now the recommended default (more reliable than X/Z analysis)
* **Enhanced preset system** - Better inheritance handling and scaling detection

### 🐛 Critical Bug Fixes
* **Fixed elbow bone inheritance** - Bones with inherit_scale=FULL now save correctly in presets
* **Resolved preset saving issues** - Inherited scaling from parent bones properly captured
* **Improved inheritance flattening** - Better detection of bones needing dual processing

### 🔧 Technical Improvements
* Enhanced debug logging for scaling analysis decisions
* Better error handling in armature diff export
* Improved bone mapping compatibility for VRChat avatars


## v0.0.1 (2025-08-08) - Initial Release

### 🚀 Core Features
* **Pose Mode Bone Editor** - CATS-like functionality for bone transform editing
* **Transform Presets** - Save and load bone scaling/positioning across armatures  
* **Shape Key Transfer** - Surface Deform-based shape key transfer with live sync
* **Mirror Flip Tools** - Smart bone and mesh mirroring with auto-detection
* **Armature Diff Export** - Compare armatures and export only the differences
* **VRChat Compatibility** - Full bone mapping and validation system

### 🎯 Key Capabilities
* Intelligent bone name mapping with fuzzy matching
* Pose history tracking with rollback functionality
* Advanced preset management with scrollable UI
* Inheritance flattening for mathematical consistency
* Professional workflow integration
* Modular architecture with graceful fallbacks


---

*This changelog focuses on user-facing changes. For detailed technical changes, see the git commit history.*