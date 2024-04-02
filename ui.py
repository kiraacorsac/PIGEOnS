import bpy
from .test import OneObjectTest,TwoObjectTest,TEST_REGISTRY,TRACEBACKS
from .utils import copy2clip
from .testRunner import TestRunnerOperator,showInfos, testStates

icons = ["ANTIALIASED","QUESTION","CHECKBOX_HLT","CANCEL","PLUGIN"]

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
        
