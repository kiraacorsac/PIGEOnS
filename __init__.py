bl_info = {
    "name": "Custom addon2",
    "author": "KiraaCorsac, Dusan, @CCArtStuff",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds something",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy

from .tests import TEST_REGISTRY
from .ui import RunTestsPanel, create_traceback_operator,create_show_details_operator,create_visualisation_operator, PigeonProperties
from .testRunner import TestRunnerOperator,showInfos
from . import utils
from bpy.utils import register_class, unregister_class


_classes = [
    PigeonProperties,
    TestRunnerOperator,
    RunTestsPanel
]

_dynamicOperators = []

def register():
    for cls in _classes:
        register_class(cls)

    for hw_id,tests in TEST_REGISTRY.items():
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
    bpy.types.Scene.pigeons = bpy.props.PointerProperty(type=PigeonProperties)
    utils.loadImages()


def unregister():
    for cls in _classes:
        unregister_class(cls)
    del bpy.types.Scene.pigeons
