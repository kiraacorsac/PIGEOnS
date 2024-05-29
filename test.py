import traceback
import bpy
from enum import Enum
from bpy.types import Operator
from .testVisualisation import selectPolygon





def resetTests():
    for hw, tests in TEST_REGISTRY.items():
        for test in tests:
            test.reset()

TEST_REGISTRY = {#{hw_id:[test1,test2,...]}
    1:[],
    2:[],
    3:[],
    4:[],
} 
#TRACEBACKS = []

class FailedInfo:
    dataBlock : bpy.props.StringProperty()
    name : bpy.props.StringProperty()
    message : bpy.props.StringProperty()

class VisData:
    method = None
    data = None

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
    failedInfo : FailedInfo #TODO: initialize implicit
    homeworks = []
    traceback = ""
    visData = None
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

                self.state = TEST_STATE.PASSED

            else:
                self.state = TEST_STATE.FAILED
        except:
            self.traceback = traceback.format_exc()
            self.state = TEST_STATE.BROKEN


@register_test
class TwoObjectTest(Test):
    label = "Two Object Test"
    homeworks = [1,3]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        try:
            if(numberOfObjects==2):
                print(self.state)
                self.state = TEST_STATE.PASSED
                print(self.state)
            else:
                self.state = TEST_STATE.FAILED
        except:
            self.traceback = traceback.format_exc()
            self.state = TEST_STATE.BROKEN
            

@register_test
class NoDefaultNameTest(Test):
    label = "No Default Name Test"
    homeworks = [1,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        try:
            failMessage = "Please remove default names:\n"
            defaultNames = [] 
            for obj in bpy.data.objects:
                if(obj.name[0:4] == "Cube"):
                    defaultNames.append(obj.name)
                

            if(defaultNames == []):
                self.state = TEST_STATE.PASSED
            else:
                for name in defaultNames:
                    failMessage=failMessage+name+"\n"
                self.setFailedInfo("","",failMessage)
                self.state = TEST_STATE.FAILED

        except:
            self.traceback = traceback.format_exc()
            self.state = TEST_STATE.BROKEN

@register_test
class MaterialSetTest(Test):
    label = "Material Set Test"
    homeworks = [1,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        try:
            failMessage = "These objects are missing materials:\n"
            objectsMissingMaterials = [] 
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    current_mode = bpy.context.object.mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    for poly in obj.data.polygons:
                        if poly.material_index >= len(obj.material_slots) or obj.material_slots[poly.material_index].material is None:
                            if obj not in objectsMissingMaterials: 
                                objectsMissingMaterials.append(obj)      
                    bpy.ops.object.mode_set(mode=current_mode)

            if(objectsMissingMaterials == []):
                self.state = TEST_STATE.PASSED
            else:
                for obj in objectsMissingMaterials:
                    failMessage = failMessage+obj.name+"\n"
                self.setFailedInfo("","",failMessage)
                self.state = TEST_STATE.FAILED

        except:
            self.traceback = traceback.format_exc()
            self.state = TEST_STATE.BROKEN

@register_test
class NoTrisTest(Test):
    label = "No Tris Test"
    homeworks = [1,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        scene = context.scene
        cursor = scene.cursor.location
        sceneObjects = scene.objects
        numberOfObjects = len(sceneObjects)
        try:
            failMessage = "These objects have triangles:\n"
            objectsWithTriangles = [] 
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    current_mode = bpy.context.object.mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    for poly in obj.data.polygons:
                        if len(poly.vertices) == 3:
                             
                             if obj not in objectsWithTriangles: 
                                objectsWithTriangles.append(obj)  
                                v = VisData()
                                v.method = 0
                                v.data = poly.index
                                self.visData = v
                    bpy.ops.object.mode_set(mode=current_mode)

            if(objectsWithTriangles == []):
                self.state = TEST_STATE.PASSED
            else:
                for obj in objectsWithTriangles:
                    failMessage = failMessage+obj.name+"\n"
                self.setFailedInfo("","",failMessage)
                self.state = TEST_STATE.FAILED

        except:
            self.traceback = traceback.format_exc()
            self.state = TEST_STATE.BROKEN

@register_test
class BrokenTest(Test):
    label = "Broken Test"
    homeworks = [2,3,4]
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
            self.state = TEST_STATE.BROKEN
            #TRACEBACKS[self.testId] = traceback.format_exc()
            self.traceback = traceback.format_exc()
            


