import bpy

from .test import OneObjectTest,TwoObjectTest,TEST_REGISTRY
showInfos = []

TEST_RESULT = [0,0,0] #passed, failed, broken

class TestsResult:
    results = [0,0,0]


class ShowResultsOperator(bpy.types.Operator):
    bl_idname = "myaddon.show_results"
    bl_label = "Details"
    
    message: bpy.props.StringProperty()
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
    
    def draw(self, context):
        self.layout.label(text=self.message)
    
    def execute(self, context):

        return {'FINISHED'}

class TestRunnerOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.test_runner_operator"
    bl_label = "TestRunnder Operator"
    bl_description = "TestRunnder Operator"

    current_hw : bpy.props.IntProperty(default=1)
    
    def execute(self, context):
        #TEST_RESULT = [0,0,0]
        testsResult = TestsResult()
        testsResult.results = [0,0,0]
        print("TestRunner - Running")
        #print(len(TEST_REGISTRY))
        currentTests = TEST_REGISTRY[self.current_hw]

        for i in range(len(currentTests)):
            currentTests[i].execute(context)
            testsResult.results[currentTests[i].state.value-2] += 1

        result_message = f"Results: Passed:{testsResult.results[0]}\n Failed:{testsResult.results[1]}\n Broken:{testsResult.results[2]}\n"
        
        # Call the results dialog operator
        bpy.ops.myaddon.show_results('INVOKE_DEFAULT',message=result_message)
        return {'FINISHED'}