# Changelog

All notable changes to NYARC VRChat Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.1.2 (2025-08-10) - Shape Key Transfer UX Improvements

### ✨ New Features
* **Native Drag & Drop Target Fields** - Target meshes now work like source mesh selector with real drag & drop
* **Always-Visible Empty Drop Field** - Persistent empty field at bottom for adding new targets
* **Multi-Selection Support** - Select multiple meshes + click plus button to add all at once

### 🎨 UI/UX Improvements  
* **Red Text Indicators** - Non-transferred shape keys show in red text
* **Grayed Sliders When Sync Disabled** - Clear visual feedback when live sync is off
* **Compact Layout** - Reduced spacing between sections by 50-70%
* **Help Section Moved** - Now appears below Live Preview section for better flow

### 🐛 Bug Fixes
* Fixed manual sync button not working when live sync disabled
* Fixed empty drop area not showing properly 
* Fixed multi-selection only adding last selected object

## v0.1.1 (2025-08-10) - Critical Bug Fixes

### 🐛 Critical Fixes
* **Fixed inherit scale overscaling** - Bones with inherit_scale=NONE now keep original scale
* **Resolved mode switching errors** - Added safe mode transitions to prevent Blender conflicts
* **Fixed "can't modify blend data" errors** - Better handling of drawing/rendering states

### 🔧 Improvements
* Enhanced error handling with retry logic
* Better debugging output for inheritance operations

## v0.1.0 (2025-08-10) - UI & Feature Enhancements

### ✨ New Features
* **Always-Visible Armature Diff Export** - No longer hidden when no bones selected
* **Optional X/Z Scaling Analysis** - Experimental mesh vertex analysis (Y-only recommended)
* **Enhanced Preset System** - Better inheritance handling and scaling detection

### 🎨 UI Improvements
* Improved Quick Start Guide explaining Transform Presets and Diff Export
* Better UI layout with consistent placement

### 🐛 Bug Fixes
* Fixed elbow bone inheritance in preset saving
* Improved bone mapping compatibility for VRChat

## v0.0.1 (2025-08-08) - Initial Release

### 🚀 Core Features
* **Bone Transform Saver** - CATS-like bone editing with pose mode
* **Shape Key Transfer** - Surface Deform-based transfer with live sync
* **Mirror Flip Tools** - Smart bone and mesh mirroring with auto-detection
* **Armature Diff Export** - Export only differences between armatures
* **Transform Presets** - Save and load bone transforms across armatures

### 🎯 Key Capabilities
* Intelligent bone name mapping with fuzzy matching
* VRChat compatibility with full bone validation
* Pose history tracking with rollback functionality
* Professional modular architecture with graceful fallbacks

---

*This changelog focuses on user-facing changes. For detailed technical changes, see the git commit history.*