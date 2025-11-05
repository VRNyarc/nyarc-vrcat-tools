"""
Dependency Installer for Robust Transfer
Bundles scipy and robust-laplacian into local deps folder
"""

import bpy
import subprocess
import sys
import os
from bpy.types import Operator


class MESH_OT_install_robust_dependencies(Operator):
    """Install dependencies for Robust Shape Key Transfer"""
    bl_idname = "mesh.install_robust_dependencies"
    bl_label = "Install Robust Transfer Dependencies"
    bl_options = {'REGISTER'}

    def execute(self, context):
        """Install scipy and robust-laplacian to local deps folder"""

        # Get deps folder path
        robust_dir = os.path.dirname(__file__)
        deps_dir = os.path.join(robust_dir, 'deps')

        # Create deps folder if it doesn't exist
        os.makedirs(deps_dir, exist_ok=True)

        # Packages to install
        packages = ['scipy', 'robust-laplacian']

        self.report({'INFO'}, "Installing dependencies... This may take 30-60 seconds")

        try:
            # Install to local deps folder using pip
            for package in packages:
                self.report({'INFO'}, f"Installing {package}...")

                subprocess.check_call([
                    sys.executable,
                    "-m", "pip", "install",
                    "--target", deps_dir,
                    "--no-deps",  # Don't install sub-dependencies (we handle them)
                    package
                ])

            self.report({'INFO'}, "Dependencies installed successfully!")
            self.report({'INFO'}, "Please restart Blender to use Robust Transfer")

            return {'FINISHED'}

        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Installation failed: {e}")
            self.report({'ERROR'}, "Try manual install: see console for instructions")
            print("\n=== MANUAL INSTALLATION ===")
            print(f"Run in terminal:")
            print(f'  {sys.executable} -m pip install --target "{deps_dir}" scipy robust-laplacian')
            return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {e}")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(MESH_OT_install_robust_dependencies)


def unregister():
    bpy.utils.unregister_class(MESH_OT_install_robust_dependencies)
