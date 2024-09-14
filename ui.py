import bpy
from .test import TEST_REGISTRY,TEST_STATE,resetTests,VisData
from . import utils
from .testRunner import TestRunnerOperator,showInfos,NEED_UPDATE
from .testVisualisation import selectPolygon,VIS_TYPE
icons = ["ANTIALIASED","CHECKBOX_HLT","QUESTION","CANCEL","PLUGIN"]



class MyProperties(bpy.types.PropertyGroup):
    def onChange(self,context):
        resetTests()


    homework_selector : bpy.props.EnumProperty(
        name="",
        description="Select an option",
        items=[
            ("HW1","Homework 1",""),
            ("HW2","Homework 2",""),
            ("HW3","Homework 3",""),
            ("HW4","Homework 4",""),
            ("showcase-ok", "Showcase - OK", ""),
            ("showcase-warn", "Showcase - Warning", ""),
            ("showcase-error", "Showcase - Error", ""),
            ("showcase-crash", "Showcase - Crash", ""),
        ],
        update=onChange
    )

    updater: bpy.props.BoolProperty(
        default=False
    )


def create_visualisation_operator(hw_id,op_id):
    class VisualisationOperator(bpy.types.Operator):
        bl_idname = f"object.visualisation_operator_{hw_id}_{op_id}"
        bl_label = "Visual OP"
        
        methodID: bpy.props.IntProperty()
        #dataID: bpy.props.IntProperty()
        objectName: bpy.props.StringProperty()
        dataID: bpy.props.IntProperty()
        
        
        def execute(self, context):
            selectPolygon(self.objectName,self.dataID)
            return {'FINISHED'}
    return VisualisationOperator

def create_show_details_operator(hw_id,op_id):
    class ShowDetailsOperator(bpy.types.Operator):
        bl_idname = f"object.show_details_operator_{hw_id}_{op_id}"
        bl_label = "Details"
        
        dataBlock: bpy.props.StringProperty()
        dataBlockName: bpy.props.StringProperty()
        message: bpy.props.StringProperty()

        def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=200)
        
        def draw(self, context):
            labels = self.message.split("\n")
            for _label in labels:
                row = self.layout.row()
                row.label(text=_label)
       
        def execute(self, context):
            return {'FINISHED'}
    return ShowDetailsOperator

def create_traceback_operator(hw_id,op_id): #TODO: test id should be here
    class TracebackOperator(bpy.types.Operator):
        bl_idname = f"object.traceback_operator_{hw_id}_{op_id}"
        bl_label = f"Copy Traceback {op_id} - Click to copy traceback\n"
        myId = op_id
        hwId = hw_id
        def execute(self, context):
            homework = TEST_REGISTRY[self.hwId]
            utils.copy_to_clipboard(homework[self.myId].traceback)
            return {'FINISHED'}
        @classmethod
        def description(self, context, properties):
            homework = TEST_REGISTRY[self.hwId]
            return homework[self.myId].traceback

    return TracebackOperator


updater = True
class RunTestsPanel(bpy.types.Panel):
    bl_label = "Run Tests Panel"
    bl_idname = "OBJECT_PT_tests"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TESTS"
    areImagesLoaded = True
    
  
    

        
    def draw(self, context):
        layout = self.layout 
                
        scene = context.scene
        my_tool = scene.my_tool
        row = layout.row()
        row.prop(my_tool,"homework_selector")
        
        hw_id_string = context.scene.my_tool.homework_selector
        hw_id = int(hw_id_string[2:])
        
        currentTests = TEST_REGISTRY[hw_id]
        
        for i in range(len(currentTests)):
            test = currentTests[i]
            row = layout.row()

            if(test.state == TEST_STATE.FAILED or test.state == TEST_STATE.BROKEN):
                row.alert = True

            col1 = row.column()
            col1.scale_x = 7
            
            col1.label(text=test.label, icon=icons[test.state.value])
            if(showInfos[i]):
                col1.label(text=test.message)
            col2 = row.column()
            col2.scale_x = 1
            if(test.state == TEST_STATE.BROKEN):
                col2.operator(f"object.traceback_operator_{hw_id}_{i}",text="",icon='COPYDOWN')
            if(test.state == TEST_STATE.FAILED):
                if(test.visType != VIS_TYPE.NONE):
                    visualisation_operator = col2.operator(f"object.visualisation_operator_{hw_id}_{i}",text="",icon='OUTLINER_OB_LIGHT')
                    visualisation_operator.objectName = test.visData.objectName
                    visualisation_operator.dataID = test.visData.dataID# test.visData
                
                col3 = row.column()
                show_detail_operator = col3.operator(f"object.show_details_operator_{hw_id}_{i}",text="",icon='INFO')           
                show_detail_operator.dataBlock="dataBlock"
                show_detail_operator.dataBlockName="dataBlock"
                show_detail_operator.message=test.failedMessage
                

        row = layout.row()   
        testsOp = row.operator(TestRunnerOperator.bl_idname,text="Run Tests")
        testsOp.current_hw=hw_id

        imgCol = self.layout.box().column()
        pigeon = "hello"
        if "test_results" in bpy.context.scene:
            # TODO: Replace results array with dictionary or make it into multiple props or something that does not requirte knowing what array num is what
            results = bpy.context.scene["test_results"]
            if(results[1] > 0): #Warning
                pigeon = "warn" #imgCol.template_preview(bpy.data.textures['okPigeon'],show_buttons=False)
            if(results[2] > 0): #Error
                pigeon = "error"
            if(results[3] > 0): #Crash/Broken
                pigeon = "crash"
            if(results[0] == len(currentTests)):
                pigeon = "ok" #imgCol.template_preview(bpy.data.textures['errorPigeon'],show_buttons=False)
        imgCol.label
        imgCol.template_icon(utils.pigeon_collection[pigeon].icon_id,scale=8)
        context.area.tag_redraw()