# Changelog

All notable changes to NYARC VRChat Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



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