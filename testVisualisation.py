import bpy
from enum import Enum

class VIS_TYPE(Enum):
    NONE = -1
    POLYGON = 0

def selectPolygon(objectName,polyIndex):
    mesh = bpy.data.objects[objectName].data#bpy.data.meshes['Cube'] 
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh.polygons[polyIndex].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    