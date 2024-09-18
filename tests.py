import typing
import bpy
from enum import Enum
from .testVisualisation import selectPolygon,VIS_TYPE

def resetTests():
    for _, tests in TEST_REGISTRY.items():
        for test in tests:
            test.reset()

class HomeworkBatteryInfo:
    def __init__(self, homework_battery_label: str):
        self._id = homework_battery_label.replace(" ", "").replace("-", "").lower()
        self._label = homework_battery_label
    

class HomeworkBatteries:
    HW1 = HomeworkBatteryInfo("Homework 1")
    HW2 = HomeworkBatteryInfo("Homework 2")
    HW3 = HomeworkBatteryInfo("Homework 3")
    HW4 = HomeworkBatteryInfo("Homework 4")
    HW5 = HomeworkBatteryInfo("Homework 5")
    HW6 = HomeworkBatteryInfo("Homework 6")
    HW7 = HomeworkBatteryInfo("Homework 7")
    Showcase_OK = HomeworkBatteryInfo("Showcase - OK")
    Showcase_warning = HomeworkBatteryInfo("Showcase - Warning")
    Showcase_error = HomeworkBatteryInfo("Showcase - Error")
    Showcase_crash = HomeworkBatteryInfo("Showcase - Crash")
    
def get_all_batteries():
    return [getattr(HomeworkBatteries, hw_key) for hw_key in dir(HomeworkBatteries) if not hw_key.startswith("_")]

TEST_REGISTRY = {}


class FailedInfo:
    dataBlock : bpy.props.StringProperty()
    message : bpy.props.StringProperty()

class VisData:
    method = None
    objectName = ''
    dataID = None

class TestState(Enum):
    INIT = 0
    OK = 1
    WARNING = 2
    ERROR = 3
    CRASH = 4

class Test:
    testId = 0
    label = ""
    state = TestState.INIT
    failedMessage = ""
    failedInfo : typing.Optional[FailedInfo] = None
    homeworks = []
    traceback = ""
    visData = None
    visType = VIS_TYPE.NONE
    objects = []

    def is_applicable(self,context):
        return True
    
    def execute(self,context):
        pass

    def setFailedInfo(self,_dataBlock,_message):
        self.failedInfo = FailedInfo()
        self.failedInfo.dataBlock = _dataBlock
        self.failedInfo.message = _message

    def addObjectNameToMessage(self,objectName):
        self.failedMessage = self.failedMessage+"\n"+objectName

    def reset(self):
        self.state = TestState.INIT
        self.failedMessage = ""
        self.failedInfo : FailedInfo
        self.traceback = ""

    def setVisData(self,objectName,dataID):
        v = VisData()
        v.objectName = objectName
        v.dataID = dataID
        v.method = self.visType
        self.visData = v

    def setState(self,state):
        self.state = state
    
def register_test(test: Test):
    testInst = test()
    for hw_battery in testInst.homeworks:
        global TEST_REGISTRY
        if hw_battery._id not in TEST_REGISTRY:
            TEST_REGISTRY[hw_battery._id] = []
        if testInst in TEST_REGISTRY[hw_battery._id]:
            continue
        TEST_REGISTRY[hw_battery._id].append(testInst)

    return testInst  

@register_test
class OK_Test(Test):
    label = "This test always passes"
    failedMessage = "You shouldn't ever see this message"
    homeworks = [HomeworkBatteries.Showcase_OK]

    def execute(self, context):
        self.setState(TestState.OK)
               

@register_test
class Warning_Test(Test):
    label = "This test always ends up as warning"
    homeworks = [HomeworkBatteries.Showcase_warning]

    def execute(self, context):
        self.setState(TestState.WARNING)
        self.setFailedInfo(
            None, 
            f"Warning!\n\n" 
            f"Something may be incorrect, but we can't really tell with automatic test - maybe it's OK?\n" 
            f"Better make sure, unless you have a very good reason, we will make you redo this homework."
        )

@register_test
class Error_Test(Test):
    label = "This test always ends up as error"
    homeworks = [HomeworkBatteries.Showcase_error]

    def execute(self, context):
        self.setState(TestState.ERROR)
        self.setFailedInfo(
            None, 
            f"Error!\n\n" 
            f"Something is definitely incorrect. Please fix it before turning in your homework.\n"
            f"We will definitely make you redo your homework if you turn it in with this error."
        )

@register_test
class Crash_Test(Test):
    label = "This test always ends up as crash"
    homeworks = [HomeworkBatteries.Showcase_crash]

    def execute(self, context):
        raise Exception(
            f"The issue is not in your mesh!\n"
            f"Something is definitely incorrect, but it's on us. Please safe the file as-is,\n" 
            f"copy the traceback with this button, and send both the blend and traceback to your teachers."
        )
    