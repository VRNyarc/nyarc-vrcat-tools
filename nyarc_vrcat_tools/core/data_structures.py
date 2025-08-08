# Core Data Structures
# Shared PropertyGroup classes and data structures used across modules

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty


class BoneTransformData(bpy.types.PropertyGroup):
    """Individual bone transform data"""
    bone_name: StringProperty(name="Bone Name")
    location_x: bpy.props.FloatProperty(name="Location X")
    location_y: bpy.props.FloatProperty(name="Location Y") 
    location_z: bpy.props.FloatProperty(name="Location Z")
    rotation_w: bpy.props.FloatProperty(name="Rotation W")
    rotation_x: bpy.props.FloatProperty(name="Rotation X")
    rotation_y: bpy.props.FloatProperty(name="Rotation Y")
    rotation_z: bpy.props.FloatProperty(name="Rotation Z")
    scale_x: bpy.props.FloatProperty(name="Scale X")
    scale_y: bpy.props.FloatProperty(name="Scale Y")
    scale_z: bpy.props.FloatProperty(name="Scale Z")


class BoneTransformPreset(bpy.types.PropertyGroup):
    """Bone transform preset containing multiple bone transforms"""
    name: StringProperty(name="Preset Name", default="New Preset")
    source_armature: StringProperty(name="Source Armature")
    bone_count: IntProperty(name="Bone Count", default=0)


def armature_poll(self, obj):
    """Poll function to filter armature objects"""
    return obj and obj.type == 'ARMATURE'


# Core data structures to be registered
CORE_CLASSES = (
    BoneTransformData,
    BoneTransformPreset,
)