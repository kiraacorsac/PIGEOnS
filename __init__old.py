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

import blf
import bpy
import subprocess
import os
from bpy.app.handlers import persistent
from .test import OneObjectTest,TwoObjectTest,TEST_REGISTRY,TRACEBACKS
from bpy.utils import register_class, unregister_class

icons = ["ANTIALIASED","QUESTION","CHECKBOX_HLT","CANCEL","PLUGIN"]


tests = []
tests_dict = {}

font_info = {
    "font_id": 0,
    "handler": None,
}
showInfos = []
testStates = [0,0,0] #[#passed,#failed,#broken]
def create_operator(op_id):
    class TestInfoMessageOperator(bpy.types.Operator):
        bl_idname = f"object.test_info_message_operator_{op_id}"
        bl_label = f"op_label_{op_id}"
        myId = op_id
        #showInfo=False
        def execute(self, context):
            showInfos[self.myId] = not showInfos[self.myId]
            self.disable = True
            return {'FINISHED'}

    return TestInfoMessageOperator

def create_traceback_operator(op_id): #TODO: test id should be here
    class TracebackOperator(bpy.types.Operator):
        bl_idname = f"object.traceback_operator_{op_id}"
        bl_label = f"Copy Traceback {op_id} - Click to copy traceback\n"
        myId = op_id
        #showInfo=False
        def execute(self, context):
            copy2clip(TRACEBACKS[self.myId])
            return {'FINISHED'}
        @classmethod
        def description(self, context, properties):
            return TRACEBACKS[self.myId]

    return TracebackOperator
 
class TestRunnerOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.test_runner_operator"
    bl_label = "TestRunnder Operator"
    bl_description = "TestRunnder Operator"

    def execute(self, context):
        #testStates = [0,0,0]
        print("TestRunner - Running")
        print(len(TEST_REGISTRY))
        for i in range(len(TEST_REGISTRY)):
            TEST_REGISTRY[i].execute(context)
            testStates[TEST_REGISTRY[i].state.value-2] += 1
        print("test exec")
        print(testStates)
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
                
        for i in range(len(TEST_REGISTRY)):
            row = layout.row()
            col1 = row.column()
            col1.scale_x = 7
            _label = col1.label(text=TEST_REGISTRY[i].label, icon=icons[TEST_REGISTRY[i].state.value])
            if(showInfos[i]):
                col1.label(text=TEST_REGISTRY[i].message)
            col2 = row.column()
            col2.scale_x = 1
            #op = col2.operator(f"object.test_info_message_operator_{i}",text="",icon='TRIA_DOWN' if showInfos[i] else 'TRIA_RIGHT')
            col2.operator(f"object.traceback_operator_{i}",text="",icon='COPYDOWN')
        #for i in range(len(TEST_REGISTRY)):
           # icon = 'TRIA_DOWN' if my_props.show_info else 'TRIA_RIGHT'
            #col2.prop(my_props, "show_info", icon=icon, text="")
            #_label.arg = TEST_REGISTRY[i].message
        #icon = 'TRIA_DOWN' if my_props.show_info else 'TRIA_RIGHT'
        #row.prop(my_props, "show_info", icon=icon, text="")
        
        # Additional label shown based on the toggle state
       
        #self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self,context), 'WINDOW', 'POST_PIXEL')

        row = layout.row()   
        row.operator(TestRunnerOperator.bl_idname,text="Run Tests")
        row.label(text=f"Passed:{testStates[0]};Failed:{testStates[1]};Broken:{testStates[2]}")
        print(testStates)
        
        #row = layout.row()   
        #row.operator(MY_OT_PopulateItems.bl_idname,text="Populuate") 


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
        register_class(create_operator(i))
        register_class(create_traceback_operator(i))
        showInfos.append(False)
        
    print("len(showInfos)")
    print(len(showInfos))
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

def copy2clip(_txt):
    txt = str(_txt)

    safe_text = txt.replace("\n", ' ') #traceback má v sobě \n, takže zatím je nrahzeno mezerou, ale lze použít tmp file
    print(safe_text)
    cmd = 'echo ' + safe_text.strip() +' | clip'#+ '|clip'
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy to clipboard: {e}")