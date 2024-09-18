import bpy
import traceback
from . import tests
showInfos = []
TEST_RESULTS_PROPERTY = "pigeons_test_results"

def resetTestResults():
    possible_state_count = len(tests.TestState._member_names_)
    tests_results = [0 for _ in range(possible_state_count)]
    bpy.context.scene[TEST_RESULTS_PROPERTY] = tests_results
    return tests_results


class TestRunnerOperator(bpy.types.Operator):
    bl_idname = "pigeons.test_runner_operator"
    bl_label = "TestRunnder Operator"
    bl_description = "TestRunnder Operator"

    current_hw : bpy.props.StringProperty(
        name="Homework to run"
    )


    def execute(self, context):
        currentTests = tests.TEST_REGISTRY[self.current_hw]
        tests_results = resetTestResults()

        for i in range(len(currentTests)):
            try:
                currentTests[i].execute(context)
            except Exception as e:
                currentTests[i].state = tests.TestState.CRASH
                currentTests[i].traceback = "\n".join(traceback.format_exception(e))
            tests_results[currentTests[i].state.value] += 1

        bpy.context.scene[TEST_RESULTS_PROPERTY] = tests_results
        pigeons_props = context.scene.pigeons
        context.scene.pigeons.updater = not pigeons_props.updater
        return {'FINISHED'}
    

