import traceback
import bpy
from enum import Enum
from bpy.types import Operator






def resetTests():
    for hw, tests in TEST_REGISTRY.items():
        for test in tests:
            test.reset()

TEST_REGISTRY = {#{hw_id:[test1,test2,...]}
    1:[],
    2:[],
    3:[],
} 
#TRACEBACKS = []

class FailedInfo:
    dataBlock : bpy.props.StringProperty()
    name : bpy.props.StringProperty()
    message : bpy.props.StringProperty()

class TEST_STATE(Enum):
    INIT = 0
    WARNING = 1
    PASSED = 2
    FAILED = 3
    BROKEN = 4

class Test:
    testId = 0
    label = ""
    state = TEST_STATE.INIT
    message = ""
    failedInfo : FailedInfo
    homeworks = []
    traceback = ""
    def is_applicable(self,context):
        print("is_applicable")
    def execute(self,context):
        print("execute")
    def setMessage(self,_message):
        self.message = _message
    def setFailedInfo(self,_dataBlock,_name,_message):
        self.failedInfo = FailedInfo()
        self.failedInfo.dataBlock = _dataBlock
        self.failedInfo.name = _name
        self.failedInfo.message = _message

    def reset(self):
        self.state = TEST_STATE.INIT
        self.message = ""
        self.failedInfo : FailedInfo
        self.traceback = ""
    
def register_test(test: Test):
    #global TRACEBACKS
    testInst = test()
    #testInst.testId = len(TRACEBACKS)
    for hw_id in testInst.homeworks:
        global TEST_REGISTRY
        #TEST_REGISTRY.append(testInst)
        if hw_id in TEST_REGISTRY:
            TEST_REGISTRY[hw_id].append(testInst)
        else:
            TEST_REGISTRY[hw_id] = []
            TEST_REGISTRY[hw_id].append(testInst)

    #TRACEBACKS.append("")
    return testInst  

@register_test
class OneObjectTest(Test):
    label = "One Object Test"
    homeworks = [1,2]
    def is_applicable(self,context):
        return True

    def execute(self,context):
       
        print("One Object Test - execute")
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        try:
            if(numberOfObjects==1):
                self.setMessage("There is only 1 object!")

                print(self.state)
                self.state = TEST_STATE.PASSED
                print(self.state)
            else:
                self.setMessage("There is not only 1 object!")
                self.state = TEST_STATE.FAILED
        except:
            self.setMessage("Something is wrong! Test skipped!")
            self.state = TEST_STATE.BROKEN


@register_test
class TwoObjectTest(Test):
    label = "Two Object Test"
    homeworks = [1,3]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        print("TwoObject Test - execute")
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        try:
            if(numberOfObjects==2):
                self.setMessage("There are only 2 objects!")
                print(self.state)
                self.state = TEST_STATE.PASSED
                print(self.state)
            else:
                self.setMessage("There is not only 2 objects!")
                self.state = TEST_STATE.FAILED
        except:
            self.setMessage("Something is wrong! Test skipped!")
            self.state = TEST_STATE.BROKEN
            

@register_test
class BrokenTest(Test):
    label = "Broken Test"
    homeworks = [2,3]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        print("Broken Test - execute")
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        try:
            scene.objects["NonExistingCube"].active = True
            self.state = TEST_STATE.PASSED

        except:
            self.setMessage("Something is wrong! Test skipped!")
            self.state = TEST_STATE.BROKEN
            #TRACEBACKS[self.testId] = traceback.format_exc()
            self.traceback = traceback.format_exc()
            


