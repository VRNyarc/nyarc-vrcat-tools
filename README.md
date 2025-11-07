# NYARC VRCat Tools

**"Professional" Blender addon for VRChat avatar creation workflows**

I am new to Github / Dev. Please go easy on me. This Project was Developed with help of Claude Code.

[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-4.2+-orange.svg)](https://www.blender.org/)
[![Release](https://img.shields.io/github/v/release/VRNyarc/nyarc-vrcat-tools)](https://github.com/VRNyarc/nyarc-vrcat-tools/releases)

## ✨ Features

### 🦴 **Bone Transform Saver**
The core module for CATS-like pose mode editing and bone transformation management:
- **Pose Mode Management**: CATS-style start/stop pose mode editing with automatic context switching
- **Intelligent Bone Mapping**: Fuzzy matching for automatic bone name resolution across different armature naming conventions
- **Advanced Preset Management**: Scrollable UI with organized preset categories and easy sharing
- **Pose History Tracking**: Complete rollback system with metadata storage for non-destructive editing
- **VRChat Compatibility**: Full bone validation and VRChat naming standard compliance
- **Inherit Scale Controls**: Smart bone scaling inheritance management with visual indicators

### 🔷 **Shape Key Transfer**
Professional-grade shape key transfer system with real-time synchronization:
- **Robust Harmonic Transfer**: Advanced harmonic inpainting algorithm for seamless transfer across topology mismatches
  - Auto-detects disconnected mesh islands (buttons, patches) and prevents clipping artifacts
  - Visual debug mode showing match quality with color-coded vertex visualization
  - Auto-tune feature for optimal distance threshold calculation
- **Surface Deform Transfer**: High-quality shape key transfer using Blender's Surface Deform modifier
- **Live Synchronization**: Real-time shape key value sync between source and target meshes
- **Batch Operations**: Multi-target, multi-shape key transfer workflows for efficient avatar creation
- **Automatic Mesh Preparation**: Smart mesh compatibility checking and Surface Deform setup
- **Expandable Help System**: Built-in guidance with collapsible instruction panels

### 🔄 **Mirror Flip**
One-click mirroring system for accessories and bone structures:
- **Smart Accessory Flipping**: Intelligent detection and duplication of .L/.R accessories
- **Bone Chain Mirroring**: Advanced bone chain analysis and symmetrical duplication
- **Auto-Detection System**: Automatic identification of flip candidates with safety validation
- **Combined Operations**: Simultaneous mesh and bone flipping for complete workflows

### 📤 **Armature Diff Export** *(Work in Progress)*
Advanced armature difference calculation and export system:
- **Difference Calculation**: Precise mathematical difference detection between armature states
- **Export Integration**: Seamless integration with existing VRChat workflows
- **Coordinate Space Handling**: Proper coordinate space conversion for accurate results

## 🚀 Installation

### **Automatic Installation (Recommended)**
1. Download the latest release ZIP: [Releases](https://github.com/VRNyarc/nyarc-vrcat-tools/releases)
2. In Blender: `Edit` → `Preferences` → `Add-ons` → `Install...`
3. Select the downloaded ZIP file
4. Enable "NYARC VRCat Tools" in the add-ons list

### **Manual Installation**
1. Clone or download this repository
2. Copy the `nyarc_vrcat_tools` folder to your Blender addons directory:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\[VERSION]\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/[VERSION]/scripts/addons/`
   - **Linux**: `~/.config/blender/[VERSION]/scripts/addons/`

## 🔄 Updating the Addon

When installing a new version over an existing installation, you need to reload the addon for changes to take effect:

**Method 1: Disable/Enable (Quick)**
1. Go to `Edit` → `Preferences` → `Add-ons`
2. Find "NYARC VRCat Tools"
3. **Uncheck** the checkbox to disable
4. **Check** it again to enable
5. New version is now active! ✅

**Method 2: Reload Scripts (Alternative)**
- Press `F3` and search for "Reload Scripts"

**Method 3: Restart Blender (Most Thorough)**
- Save your work and restart Blender

> 💡 **Why is this needed?** This is standard for all Blender addons due to Python's module caching system. The addon includes automatic hot-reload support that activates when you disable/enable it. This is the same workflow used by professional addons like Hard Ops, Node Wrangler, and others.

## 🎯 Usage

### **Quick Start**
1. Select your avatar armature
2. Open `3D Viewport` → `N Panel` → `NYARC Tools`
3. Use **Bone Transform Saver** for precise armature modifications
4. Apply **Shape Key Transfer** for facial expression workflows
5. Export differences with **Armature Diff Export**

### **Professional Workflows**
- **Avatar Setup**: Bone transforms → Shape key transfer → Mirror accessories
- **Precision Export**: Diff calculation → VRChat validation → Final export
- **Team Collaboration**: Preset sharing → Version tracking → Rollback support

## 🛠️ System Requirements

- **Blender**: 4.2 LTS or newer (required for full feature support)
- **Platform**: Windows, macOS, Linux
- **Memory**: 4GB RAM minimum, 8GB+ recommended for complex avatars

## 📚 Documentation

- **[Changelog](CHANGELOG.md)**: Version history and updates
- **[Contributing Guidelines](CONTRIBUTING.md)**: Development guidelines and contribution process
- **[License](LICENSE)**: MIT License details

For detailed usage instructions, see the feature descriptions above and the in-addon help panels.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit with descriptive messages: `git commit -m "feat: add amazing feature"`
5. Push to your branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This project incorporates code from [Robust Weight Transfer](https://github.com/sentfromspacevr/robust-weight-transfer) (GPL-3.0)
and takes inspiration from [RinvosBlendshapeTransfer](https://github.com/neongm/RinvosBlendshapeTransfer).

## 🌟 Acknowledgments

- **VRChat Community** for feedback and feature requests
- **Blender Foundation** for the amazing 3D creation platform
- **CATS Blender Plugin** for workflow inspiration
- **Avatar Tools Community** for testing and validation
- **[SENT Robust Weight Transfer](https://github.com/sentfromspacevr/robust-weight-transfer)** for harmonic inpainting-based robust shape key transfer algorithm
- **[RinvosBlendshapeTransfer](https://github.com/neongm/RinvosBlendshapeTransfer)** for ideas and optimizations on standard blendshape transfer

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/VRNyarc/nyarc-vrcat-tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VRNyarc/nyarc-vrcat-tools/discussions)
- **Documentation**: [Wiki](https://github.com/VRNyarc/nyarc-vrcat-tools/wiki)

---

**Made with ❤️ for the VRChat community**
