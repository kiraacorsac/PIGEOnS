import bpy

from .tests import TEST_REGISTRY
from .ui import (
    RunTestsPanel,
    create_traceback_operator,
    create_show_details_operator,
    create_visualisation_operator,
    PigeonProperties,
)
from .testRunner import TestRunnerOperator, showInfos
from . import utils
from bpy.utils import register_class, unregister_class


_classes = [PigeonProperties, TestRunnerOperator, RunTestsPanel]

_dynamicOperators = []


def register():
    for cls in _classes:
        register_class(cls)

    _dynamicOperators = []
    for hw_id, tests in TEST_REGISTRY.items():
        for i in range(len(tests)):
            dynamic_operator = create_traceback_operator(hw_id, i)
            _dynamicOperators.append(dynamic_operator)
            dynamic_operator = create_show_details_operator(hw_id, i)
            _dynamicOperators.append(dynamic_operator)
            dynamic_operator = create_visualisation_operator(hw_id, i)
            _dynamicOperators.append(dynamic_operator)
            showInfos.append(False)

    for cls in _dynamicOperators:
        register_class(cls)

    bpy.types.Scene.pigeons = bpy.props.PointerProperty(type=PigeonProperties)
    utils.loadImages()


def unregister():
    for cls in reversed([*_classes, *_dynamicOperators]):
        unregister_class(cls)

    del bpy.types.Scene.pigeons
