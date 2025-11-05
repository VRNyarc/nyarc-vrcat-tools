"""
Robust Shape Key Transfer Operator
Blender operator wrapper for harmonic inpainting-based transfer
"""

import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty
from bpy.types import Operator


class MESH_OT_transfer_shape_key_robust(Operator):
    """Transfer shape key using robust harmonic inpainting"""
    bl_idname = "mesh.transfer_shape_key_robust"
    bl_label = "Robust Transfer Shape Key"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties
    distance_threshold: FloatProperty(
        name="Distance Threshold",
        description="Maximum spatial distance for valid match (meters)",
        default=0.01,
        min=0.0001,
        max=0.1,
        precision=4
    )

    normal_threshold: FloatProperty(
        name="Normal Threshold",
        description="Minimum normal alignment (cosine, 0=opposite, 1=parallel)",
        default=0.5,
        min=0.0,
        max=1.0,
        precision=3
    )

    use_pointcloud: BoolProperty(
        name="Point Cloud Laplacian",
        description="Use distance-based smoothing (more robust, slower)",
        default=False
    )

    smooth_iterations: IntProperty(
        name="Post-Smooth Iterations",
        description="Additional smoothing passes (0 recommended)",
        default=0,
        min=0,
        max=10
    )

    show_debug: BoolProperty(
        name="Show Match Quality Debug",
        description="Create vertex colors showing match quality",
        default=False
    )

    handle_islands: BoolProperty(
        name="Handle Unmatched Islands",
        description="Automatically handle disconnected mesh parts with poor matches (buttons, patches, etc.)",
        default=True
    )

    def execute(self, context):
        # Check if dependencies are available
        from ..robust import DEPENDENCIES_AVAILABLE, get_missing_dependencies

        if not DEPENDENCIES_AVAILABLE:
            missing = get_missing_dependencies()
            self.report({'ERROR'}, f"Missing dependencies: {', '.join(missing)}")
            self.report({'ERROR'}, "Click 'Install Robust Dependencies' button to install")
            return {'CANCELLED'}

        props = context.scene.nyarc_tools_props

        # Get objects
        source_obj = props.shapekey_source_object
        target_obj = props.shapekey_target_object

        # Fallback to viewport selection
        if not target_obj and context.selected_objects:
            for obj in context.selected_objects:
                if obj.type == 'MESH' and obj != source_obj:
                    target_obj = obj
                    break

        # Validate
        if not source_obj:
            self.report({'ERROR'}, "No source object selected")
            return {'CANCELLED'}

        if not target_obj:
            self.report({'ERROR'}, "No target object selected")
            return {'CANCELLED'}

        if not props.shapekey_shape_key or props.shapekey_shape_key == "NONE":
            self.report({'ERROR'}, "No shape key selected")
            return {'CANCELLED'}

        shape_key_name = props.shapekey_shape_key

        # Import robust transfer module
        try:
            from ..robust.core import transfer_shape_key_robust

            # Run robust transfer
            success = transfer_shape_key_robust(
                source_obj=source_obj,
                target_obj=target_obj,
                shape_key_name=shape_key_name,
                distance_threshold=self.distance_threshold,
                normal_threshold=self.normal_threshold,
                use_pointcloud=self.use_pointcloud,
                smooth_iterations=self.smooth_iterations,
                show_debug=self.show_debug,
                handle_islands=self.handle_islands,
                operator=self
            )

            if success:
                self.report({'INFO'}, f"Robust transfer complete: '{shape_key_name}'")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Robust transfer failed")
                return {'CANCELLED'}

        except ImportError as e:
            self.report({'ERROR'}, f"Missing dependencies: {e}")
            self.report({'ERROR'}, "Install: numpy, scipy, scikit-learn, robust-laplacian")
            return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Robust transfer error: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


class MESH_OT_auto_tune_distance_threshold(Operator):
    """Automatically determine optimal distance threshold based on mesh spacing"""
    bl_idname = "mesh.auto_tune_distance_threshold"
    bl_label = "Auto-Tune Distance"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.nyarc_tools_props

        source_obj = props.shapekey_source_object
        target_obj = props.shapekey_target_object

        # Fallback to viewport selection
        if not target_obj and context.selected_objects:
            for obj in context.selected_objects:
                if obj.type == 'MESH' and obj != source_obj:
                    target_obj = obj
                    break

        if not source_obj or not target_obj:
            self.report({'WARNING'}, "Select source and target objects first")
            return {'CANCELLED'}

        try:
            import numpy as np
            from ..robust.mesh_data import get_mesh_data_world_space
            import scipy.spatial

            # Get mesh data
            source_verts, _, _ = get_mesh_data_world_space(source_obj)
            target_verts, _, _ = get_mesh_data_world_space(target_obj)

            # Build KD-tree
            tree = scipy.spatial.cKDTree(source_verts)

            # Query distances
            distances, _ = tree.query(target_verts)

            # Compute median and recommended threshold
            median_dist = float(np.median(distances))
            recommended = median_dist * 2.0  # 2× median for safety

            # Update property
            props.robust_distance_threshold = recommended

            self.report({'INFO'}, f"Distance threshold set to {recommended:.4f}m (2× median)")
            return {'FINISHED'}

        except ImportError as e:
            self.report({'ERROR'}, f"Missing dependencies: {e}")
            return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Auto-tune failed: {e}")
            return {'CANCELLED'}


# Registration
classes = (
    MESH_OT_transfer_shape_key_robust,
    MESH_OT_auto_tune_distance_threshold,
)

# Import installer if it exists
try:
    from ..robust.installer import MESH_OT_install_robust_dependencies
    classes = classes + (MESH_OT_install_robust_dependencies,)
except ImportError:
    pass  # Installer not yet created


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
