bl_info = {
    "name": "Custom addon2",
    "author": "Dusan",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds something",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import os
import bpy

from .test import TEST_REGISTRY
from .ui import RunTestsPanel, create_traceback_operator,create_show_details_operator,create_visualisation_operator, MyProperties
from .testRunner import TestRunnerOperator,ShowResultsOperator,showInfos
from .utils import loadImages
from bpy.utils import register_class, unregister_class
from bpy.props import BoolProperty, PointerProperty
from bpy.app.handlers import persistent



_classes = [
    MyProperties,
    ShowResultsOperator,
    TestRunnerOperator,
    RunTestsPanel
]

_dynamicOperators = []

from os import listdir
from os.path import isfile, join
custom_icons = None
list_raw = []
img = None

@persistent
def load_images_handler(dummy):
    loadImages()

def register():
    #tests.append(OneObjectTest())
    #tests.append(TwoObjectTest())
    

    for cls in _classes:
        register_class(cls)

    for hw_id,tests in TEST_REGISTRY.items():
        print(f"Looping through hw_id:{hw_id} and tests: {tests}")
        for i in range(len(tests)):
            dymOp = create_traceback_operator(hw_id,i)
            register_class(dymOp)
            _dynamicOperators.append(dymOp)
            dymOp = create_show_details_operator(hw_id,i)
            register_class(dymOp)
            _dynamicOperators.append(dymOp)
            dymOp = create_visualisation_operator(hw_id,i)
            register_class(dymOp)
            _dynamicOperators.append(dymOp)
            showInfos.append(False)
    print(TEST_REGISTRY)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyProperties)
    bpy.app.handlers.load_post.append(load_images_handler)
    #bpy.types.Scene.my_properties = PointerProperty(type=MyProperties)
    #bpy.types.Scene.my_prop = bpy.props.IntProperty(update=update_func)


def unregister():

    for cls in _classes:
        unregister_class(cls)
    #for dymOp in _dynamicOperators:
    #    unregister_class(dymOp)    
    #for i in range(len(TEST_REGISTRY)):
        #unregister_ope(create_operator(i))
        #register_class(create_traceback_operator(i))
    del bpy.types.Scene.my_tool
    #bpy.ops.object.TestRunnerOperator.initTests()

if __name__ == "__main__":
    register()

