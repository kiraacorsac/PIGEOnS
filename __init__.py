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


import bpy
from enum import Enum
from random import randint
from bpy.types import Operator

from bpy.utils import register_class, unregister_class

icons = ["ANTIALIASED","QUESTION","CHECKBOX_HLT","CANCEL"]

class TEST_STATE(Enum):
    INIT = 0
    WARNING = 1
    PASSED = 2
    FAILED = 3

class Test:
    label = ""
    state = TEST_STATE.INIT
    def is_applicable(self):
        print("is_applicable")
    def execute(self,context):
        print("execute")
    
        

class OneObjectTest(Test):
    label = "One Object Test"

    def execute(self,context):
       
        print("One Object Test execute")
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        if(numberOfObjects==1):
            print("There is only 1 objects!")
            print(state)
            self.state = TEST_STATE.PASSED
            print(state)
        else:
            print("There is not only 1 objects!")
            self.state = TEST_STATE.FAILED

class TwoObjectTest(Test):
    label = "Two Object Test"

    def execute(self,context):
        state = TEST_STATE.EVALUATING
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        if(numberOfObjects==2):
            self.state = TEST_STATE.PASSED
        else:
            self.state = TEST_STATE.FAILED

tests = []
tests_dict = {}

class TestRunnerOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.test_runner_operator"
    bl_label = "TestRunnder Operator"
    

    def execute(self, context):
        
        print("TestRunner - Running")
        print(len(tests))
        for i in range(len(tests)):
            tests[i].execute(context)
        
        return {'FINISHED'}


    #def initTests():
    #    tests.append(OneObjectTest())


class RunTestsPanel(bpy.types.Panel):
    bl_label = "Run Tests Panel"
    bl_idname = "OBJECT_PT_tests"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TESTS"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        for i in range(len(tests)):
            layout.label(text=tests[i].label, icon=icons[tests[i].state.value])
            
        row = layout.row()    
        row.operator(TestRunnerOperator.bl_idname,text="Run Tests")


_classes = [
    TestRunnerOperator,
    RunTestsPanel
]

def register():
    tests.append(OneObjectTest())
    tests.append(TwoObjectTest())
    print(len(tests))
    for cls in _classes:
        register_class(cls)


def unregister():

    for cls in _classes:
        unregister_class(cls)
    
    #bpy.ops.object.TestRunnerOperator.initTests()

if __name__ == "__main__":
    register()
