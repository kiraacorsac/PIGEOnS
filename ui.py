import bpy
from .test import TEST_REGISTRY,TEST_STATE,resetTests,VisData
from .utils import copy2clip, custom_icons,list_raw,loadImages
from .testRunner import TestRunnerOperator,showInfos,NEED_UPDATE
from .testVisualisation import selectPolygon,VIS_TYPE
icons = ["ANTIALIASED","CHECKBOX_HLT","QUESTION","CANCEL","PLUGIN"]



class MyProperties(bpy.types.PropertyGroup):
    def onChange(self,context):
        resetTests()


    my_enum : bpy.props.EnumProperty(
        name="",
        description="Select an option",
        items=[ #TODO: dynamicky vytvořit
            ("HW1","Homework 1",""),
            ("HW2","Homework 2",""),
            ("HW3","Homework 3",""),
            ("HW4","Homework 4",""),
        ],
        update=onChange
    )

    updater: bpy.props.BoolProperty(
        name="My Boolean",
        description="A simple boolean property",
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
            print("visualisation_operator_")
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
            print("show_details_op")
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
            #print(f"description {self.hwId} & {self.myId}")
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
        row.prop(my_tool,"my_enum")
        
        hw_id_string = context.scene.my_tool.my_enum
        hw_id = int(hw_id_string[2:])
        
        #global CURRENT_TESTS
        #CURRENT_TESTS = hw_id
        


        currentTests = TEST_REGISTRY[hw_id]
        
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
                if(test.visType != VIS_TYPE.NONE):
                    #visualisation_operator = col2.operator(f"object.visualisation_operator_{hw_id}_{i}",text="",icon='OUTLINER_OB_LIGHT')
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
        tex = None
        gotResults = False
        #updater = NEED_UPDATE
        #if "updater" in bpy.context.scene:
         #   updater = bpy.context.scene["updater"]
        if "test_results" in bpy.context.scene:
            results = bpy.context.scene["test_results"]
            if(results[1] > 0): #Warning
                tex = bpy.data.textures.get("warnPigeon")#imgCol.template_preview(bpy.data.textures['okPigeon'],show_buttons=False)
            if(results[2] > 0): #Error
                tex = bpy.data.textures.get("errorPigeon")
            if(results[3] > 0): #Crash/Broken
                tex = bpy.data.textures.get("crashPigeon")
            if(results[0] == len(currentTests)):
                tex = bpy.data.textures.get("okPigeon")#imgCol.template_preview(bpy.data.textures['errorPigeon'],show_buttons=False)
            gotResults = True
        else:
            tex = bpy.data.textures.get("helloPigeon")#imgCol.template_preview(bpy.data.textures['helloPigeon'],show_buttons=False)
        if tex:
            slot = getattr(context, "texture_slot", None)
            imgCol.template_preview(tex,slot=slot)
            if gotResults:
                    if context.scene.my_tool.updater:
                        imgCol.scale_y = 1.03
                    else:
                        imgCol.scale_y = 1.00
                        #updater = not updater
                        #print(updater)
        context.area.tag_redraw()



        
        
