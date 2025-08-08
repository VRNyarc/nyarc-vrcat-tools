# NYARC VRChat Tools

**Professional Blender addon for VRChat avatar creation workflows**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
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
4. Enable "NYARC VRChat Tools" in the add-ons list

### **Manual Installation** 
1. Clone or download this repository
2. Copy the `nyarc_vrcat_tools` folder to your Blender addons directory:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\[VERSION]\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/[VERSION]/scripts/addons/`
   - **Linux**: `~/.config/blender/[VERSION]/scripts/addons/`

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

- **Blender**: 4.2 or newer (required for full feature support)
- **Platform**: Windows, macOS, Linux
- **Memory**: 4GB RAM minimum, 8GB+ recommended for complex avatars
- **VRChat SDK**: Compatible with VRChat Creator Companion workflow

## 📚 Documentation

- **[User Guide](docs/user-guide.md)**: Complete feature documentation
- **[Installation Guide](docs/installation.md)**: Detailed setup instructions  
- **[Developer Documentation](docs/development.md)**: Architecture and contribution guide
- **[Changelog](CHANGELOG.md)**: Version history and updates

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **VRChat Community** for feedback and feature requests
- **Blender Foundation** for the amazing 3D creation platform
- **CATS Blender Plugin** for workflow inspiration
- **Avatar Tools Community** for testing and validation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/VRNyarc/nyarc-vrcat-tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VRNyarc/nyarc-vrcat-tools/discussions)
- **Documentation**: [Wiki](https://github.com/VRNyarc/nyarc-vrcat-tools/wiki)

---

**Made with ❤️ for the VRChat community**