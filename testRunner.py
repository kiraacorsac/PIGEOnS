import bpy

from .test import OneObjectTest,TwoObjectTest,TEST_REGISTRY,TRACEBACKS
showInfos = []
testStates = [0,0,0]



@dataclass
class TestsResult:
    passed: int
    failed: int
    broken: int
    
TEST_RESULT = TestsResult()

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