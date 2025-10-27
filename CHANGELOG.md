# Changelog

All notable changes to NYARC VRChat Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## v0.1.6 (2025-10-27) - Advanced Shape Key Transfer & Post-Processing

### ✨ Major New Features
* **Advanced Surface Deform Controls** - Fine-tune transfer quality with strength and falloff parameters
  * Strength slider (0.0-1.0) controls transfer intensity
  * Falloff distance (0.1-16.0) for smoother transitions on clothing edges
* **Boundary Smoothing System** - Professional post-processing workflow for hard cutoff lines
  * Automatic vertex group mask generation for boundary vertices
  * Configurable smoothing iterations and boundary width
  * Auto-blur mask option for softer transitions
  * Weight Paint mode integration for manual mask editing
* **Partial Island Handling (WIP)** - Experimental handling for small mesh details (buttons, patches, belts)
  * EXCLUDE mode: Reset partially moved islands to basis
  * AVERAGE mode: Apply uniform displacement to entire island
  * Configurable island size threshold
  * *Note: This feature is still work-in-progress and may need further refinement*
* **Pre-processing Options** - Modify source mesh before transfer (non-destructive)
  * Subdivision support (simple or Catmull-Clark)
  * Displace modifier with configurable strength and direction
  * All pre-processing works on temporary copy, original mesh unchanged
* **Companion Smoothing Tool** - Dedicated panel for post-transfer smoothing workflow
  * Apply smoothing to existing shape keys using vertex group masks
  * Generate/regenerate smoothing masks after transfer
  * Manual smoothing control for iterative refinement

### 🐛 Critical Bug Fixes
* **Fixed Triangulation Modifier Bug** - Triangulation modifiers are now properly removed instead of being permanently applied
  * Previously, compatibility triangulation was being baked into the mesh
  * Now correctly cleans up temporary modifiers after transfer
* **Viewport Selection Fallback** - Transfer now works with viewport-selected mesh when no target is set in UI
* **Better Modifier Cleanup** - All temporary modifiers (triangulation, edge split) properly removed after transfer

### 🎨 UI/UX Improvements
* **Advanced Options Panel** - Collapsible section for advanced parameters
  * Surface Deform strength and falloff controls
  * Post-processing options (smoothing, island handling)
  * Pre-processing options (subdivision, displace)
* **Expanded Help Documentation** - Detailed tooltips and help text for all new features
* **Skip Existing Option** - Skip transfer if shape key already exists on target

### 🔧 Technical Improvements
* Modular post-processing utilities (`smooth_boundary.py`, `preprocessing.py`)
* Better error handling and recovery for modifier operations
* Improved mesh validation and compatibility preparation
* Enhanced debug output for troubleshooting

## v0.1.5 (2025-08-12) - Surface Deform & Multi-Target Fixes

## v0.1.0 (2025-08-12)

### New Features
* feat: initial project structure and professional Blender addon
* docs: add comprehensive version management documentation for /clear recovery
* feat: improve UI layout and add optional XZ scaling analysis
* docs: clean up changelog - remove duplicates and add v0.1.2 changes

### Bug Fixes
* docs: improve README feature descriptions and fix typos
* docs: fix Bone Transform Saver description to accurately reflect CATS-like functionality
* fix: resolve inherit scale mixed case overscaling and mode switching errors
* fix: remove console spam from poll methods and UI operations
* hotfix: fix apply rest pose context error with inherit_scale settings

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
* release: v0.1.0
* release: v0.0.1
* release: v0.1.2
* release: v0.1.3
* release: v0.0.1


## v0.0.1 (2025-08-12)

### New Features
* feat: initial project structure and professional Blender addon
* docs: add comprehensive version management documentation for /clear recovery
* feat: improve UI layout and add optional XZ scaling analysis
* docs: clean up changelog - remove duplicates and add v0.1.2 changes

### Bug Fixes
* docs: improve README feature descriptions and fix typos
* docs: fix Bone Transform Saver description to accurately reflect CATS-like functionality
* fix: resolve inherit scale mixed case overscaling and mode switching errors
* fix: remove console spam from poll methods and UI operations

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
* release: v0.1.0
* release: v0.0.1
* release: v0.1.2
* release: v0.1.3


## v0.1.3 (2025-08-11) - Console Spam & Mirror Tool Fixes

### 🐛 Bug Fixes
* **Removed Console Spam** - Fixed excessive debug output flooding Blender console
  * Eliminated POLL_CHECK messages appearing every frame  
  * Removed UI LIST debug prints from pose history operations
  * Fixed DETECTION spam from UI panel redraws
* **Mirror Tool Improvements** - Fixed core bone parenting and VRChat bone classification  
  * Core bone chains now preserve original parent relationships (tail → hips stays hips, not spine)
  * Added missing leg category mappings for VRChat bone opposite detection
  * Removed 'root' from VRChat bone list to prevent false positive classifications

### 🔧 Technical
* Poll methods and UI draw functions now properly silent for optimal performance
* Better VRChat standard bone compatibility with improved opposite bone detection

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