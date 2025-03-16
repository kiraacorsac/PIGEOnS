import bpy
import traceback
import json
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

    current_hw: bpy.props.StringProperty(name="Homework to run")
    output_to_console: bpy.props.BoolProperty(
        name="Output results to console", default=False
    )
    output_to_file: bpy.props.StringProperty(name="Path to a output log file")

    def execute(self, context):
        currentTests = tests.TEST_REGISTRY[self.current_hw]
        testsResults = {}
        tests_results_prop = resetTestResults()

        for test in currentTests:
            try:
                if not test.is_applicable(context):
                    test.state = tests.TestState.SKIPPED
                else:
                    test.execute(context)
                if test.state == tests.TestState.INIT:
                    raise Exception(
                        f"Test '{test.label}' did not change state, stayed {tests.TestState.INIT.name} after execution."
                    )
            except Exception as e:
                test.state = tests.TestState.CRASH
                test.traceback = "\n".join(traceback.format_exception(e))
            testsResults[test.testId] = {
                "label": test.label,
                "state": test.state.name,
                "datablock": test.failedInfo.dataBlock,
                "message": test.failedInfo.message,
                "traceback": test.traceback,
            }
            tests_results_prop[test.state.value] += 1
        if self.output_to_file:
            try:
                with open(self.output_to_file, "w") as file:
                    json.dump(testsResults, file)
            except IOError as e:
                self.report({"ERROR"}, f"Failed to write an output file: {e}")

        if self.output_to_console:
            print(json.dumps(testsResults))

        bpy.context.scene[TEST_RESULTS_PROPERTY] = tests_results_prop
        pigeons_props = context.scene.pigeons
        context.scene.pigeons.updater = not pigeons_props.updater
        return {"FINISHED"}
