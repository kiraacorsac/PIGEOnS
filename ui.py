import bpy
from .test import OneObjectTest,TwoObjectTest,TEST_REGISTRY,TEST_STATE,resetTests
from .utils import copy2clip
from .testRunner import TestRunnerOperator,showInfos

icons = ["ANTIALIASED","QUESTION","CHECKBOX_HLT","CANCEL","PLUGIN"]



class MyProperties(bpy.types.PropertyGroup):
    def onChange(self,context):
        resetTests()


    my_enum : bpy.props.EnumProperty(
        name="",
        description="Select an option",
        items=[
            ("HW1","Homework 1",""),
            ("HW2","Homework 2",""),
            ("HW3","Homework 3",""),
        ],
        update=onChange
    )

def create_show_details_operator(hw_id,op_id):
    class ShowDetailsOperator(bpy.types.Operator):
        bl_idname = f"object.show_details_operator_{hw_id}_{op_id}"
        bl_label = "Operation Results"
        
        dataBlock: bpy.props.StringProperty()
        dataBlockName: bpy.props.StringProperty()
        message: bpy.props.StringProperty()

        def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=400)
        
        def draw(self, context):
            result = f"{self.dataBlock} {self.dataBlockName} {self.message}."
            self.layout.label(text=result)
        
        def execute(self, context):

            return {'FINISHED'}
    return ShowDetailsOperator

def create_traceback_operator(hw_id,op_id): #TODO: test id should be here
    class TracebackOperator(bpy.types.Operator):
        bl_idname = f"object.traceback_operator_{hw_id}_{op_id}"
        bl_label = f"Copy Traceback {op_id} - Click to copy traceback\n"
        myId = op_id
        hwId = hw_id
        #showInfo=False
        def execute(self, context):
            homework = TEST_REGISTRY[self.hwId]
            copy2clip(homework[self.myId].traceback)
            return {'FINISHED'}
        @classmethod
        def description(self, context, properties):
            homework = TEST_REGISTRY[self.hwId]
            print(f"description {self.hwId} & {self.myId}")
            return homework[self.myId].traceback

    return TracebackOperator

class RunTestsPanel(bpy.types.Panel):
    bl_label = "Run Tests Panel"
    bl_idname = "OBJECT_PT_tests"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TESTS"

    def draw(self, context):
        layout = self.layout 
                
        scene = context.scene
        my_tool = scene.my_tool
        row = layout.row()
        row.prop(my_tool,"my_enum")
        
        hw_id_string = context.scene.my_tool.my_enum
        hw_id = int(hw_id_string[2:])
        print(f"hw_id: {hw_id}")
        #global CURRENT_TESTS
        #CURRENT_TESTS = hw_id
        


        currentTests = TEST_REGISTRY[hw_id]
        print(f"RunTestsPanel: hw_id = {hw_id}")
        for i in range(len(currentTests)):
            test = currentTests[i]
            row = layout.row()

            if(test.state == TEST_STATE.FAILED or test.state == TEST_STATE.BROKEN):
                row.alert = True

            col1 = row.column()
            col1.scale_x = 7
            
            _label = col1.label(text=test.label, icon=icons[test.state.value])
            if(showInfos[i]):
                col1.label(text=test.message)
            col2 = row.column()
            col2.scale_x = 1
            #op = col2.operator(f"object.test_info_message_operator_{i}",text="",icon='TRIA_DOWN' if showInfos[i] else 'TRIA_RIGHT')
            if(test.state == TEST_STATE.BROKEN):
                col2.operator(f"object.traceback_operator_{hw_id}_{i}",text="",icon='COPYDOWN')
            if(test.state == TEST_STATE.FAILED):
                show_detail_operator = col2.operator(f"object.show_details_operator_{hw_id}_{i}",text="",icon='INFO')
                show_detail_operator.dataBlock="dataBlock"
                show_detail_operator.dataBlockName="dataBlock"
                show_detail_operator.message="needs to be OK"

        row = layout.row()   
        testsOp = row.operator(TestRunnerOperator.bl_idname,text="Run Tests")
        testsOp.current_hw=hw_id

        
        
