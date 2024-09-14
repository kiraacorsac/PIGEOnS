import bpy

from . import tests
showInfos = []
TEST_RESULTS_PROPERTY = "pigeons_test_results"

def resetTestResults():
    possible_state_count = len(tests.TestState._member_names_)
    tests_results = [0 for _ in range(possible_state_count)]
    bpy.context.scene[TEST_RESULTS_PROPERTY] = tests_results
    return tests_results


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
        currentTests = tests.TEST_REGISTRY[self.current_hw]
        tests_results = resetTestResults()

        for i in range(len(currentTests)):
            currentTests[i].execute(context)
            tests_results[currentTests[i].state.value] += 1

        bpy.context.scene[TEST_RESULTS_PROPERTY] = tests_results
        my_props = context.scene.my_tool
        context.scene.my_tool.updater = not my_props.updater
        return {'FINISHED'}
    

