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

from .test import OneObjectTest,TwoObjectTest,TEST_REGISTRY,TRACEBACKS
from .ui import RunTestsPanel, create_traceback_operator
from .testRunner import TestRunnerOperator,showInfos

from bpy.utils import register_class, unregister_class

_classes = [
    TestRunnerOperator,
    RunTestsPanel
]

def register():
    #tests.append(OneObjectTest())
    #tests.append(TwoObjectTest())
    for cls in _classes:
        register_class(cls)
    for i in range(len(TEST_REGISTRY)):
        register_class(create_traceback_operator(i))
        showInfos.append(False)
        
    #if populate_my_items not in bpy.app.handlers.load_post:
    #populate_my_items()
    


def unregister():

    for cls in _classes:
        unregister_class(cls)
    #for i in range(len(TEST_REGISTRY)):
        #unregister_ope(create_operator(i))
        #register_class(create_traceback_operator(i))
    
    #bpy.ops.object.TestRunnerOperator.initTests()

if __name__ == "__main__":
    register()

