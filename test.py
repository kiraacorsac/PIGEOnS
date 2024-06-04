import traceback
import bpy
from enum import Enum
from bpy.types import Operator
from .testVisualisation import selectPolygon,VIS_TYPE





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
    objectName = ''
    dataID = None

class TEST_STATE(Enum):
    INIT = 0
    PASSED = 1
    WARNING = 2
    FAILED = 3
    BROKEN = 4

class Test:
    testId = 0
    label = ""
    state = TEST_STATE.INIT
    failedMessage = ""
    failedInfo : FailedInfo #TODO: initialize implicit
    homeworks = []
    traceback = ""
    visData = None
    visType = VIS_TYPE.NONE
    objects = []
    def is_applicable(self,context):
        print("is_applicable")
    def execute(self,context):
        print("execute")

    def setFailedInfo(self,_dataBlock,_name,_message):
        self.failedInfo = FailedInfo()
        self.failedInfo.dataBlock = _dataBlock
        self.failedInfo.name = _name
        self.failedInfo.message = _message

    def addObjectNameToMessage(self,objectName):
        self.failedMessage = self.failedMessage+"\n"+objectName

    def reset(self):
        self.state = TEST_STATE.INIT
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
class NoDefaultNameTest(Test):
    label = "No Default Name Test"
    homeworks = [1,3,4]
    failedMessage = "Please remove default names:"
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:
            defaultNames = [] 
            for obj in bpy.data.objects:
                if(obj.name[0:4] == "Cube"): #TODO: add Plane, Circle etc.
                    defaultNames.append(obj.name)
                

            if(defaultNames == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for name in defaultNames:
                    self.addObjectNameToMessage(name)
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)

@register_test
class MaterialSetTest(Test):
    label = "Material Set Test"
    failedMessage = "These objects are missing materials:"
    homeworks = [1,3,4]
    visType = VIS_TYPE.POLYGON
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:
            objectsMissingMaterials = [] 
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    current_mode = bpy.context.object.mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    for poly in obj.data.polygons:
                        if poly.material_index >= len(obj.material_slots) or obj.material_slots[poly.material_index].material is None:
                            if obj not in objectsMissingMaterials: 
                                objectsMissingMaterials.append(obj)  
                                self.setVisData(obj.name,poly.index)     
                    bpy.ops.object.mode_set(mode=current_mode)

            if(objectsMissingMaterials == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for obj in objectsMissingMaterials:
                    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)

@register_test
class NoTrisTest(Test):
    label = "No Tris Test"
    failedMessage = "These objects have triangles:"
    homeworks = [1,3,4]
    visType = VIS_TYPE.POLYGON
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objectsWithTriangles = [] 
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    current_mode = bpy.context.object.mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    for poly in obj.data.polygons:
                        if len(poly.vertices) == 3: 
                             if obj not in objectsWithTriangles: 
                                objectsWithTriangles.append(obj) 
                                self.setVisData(obj.name,poly.index) 
                    bpy.ops.object.mode_set(mode=current_mode)

            if(objectsWithTriangles == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for obj in objectsWithTriangles:
                    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)

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
            self.setState(TEST_STATE.PASSED)

        except:          
            self.setState(TEST_STATE.BROKEN)
            #TRACEBACKS[self.testId] = traceback.format_exc()
            self.traceback = traceback.format_exc()
            

@register_test
class NoCrazySubdivision(Test):
    label = "No Crazy Subdivision"
    failedMessage = "These objects have high subdivision:"
    homeworks = []
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objectsWithHighSubdivision = [] 
            for obj in bpy.data.objects:
                subsurf_modifier = obj.modifiers.get('Subdivision')
                if subsurf_modifier:
                    if subsurf_modifier.levels > 5:
                        objectsWithHighSubdivision.append(obj)

            if(objectsWithHighSubdivision == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for obj in objectsWithHighSubdivision:
                    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.WARNING)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)

@register_test
class RenderSubdivisionNotLessThenViewport(Test):
    label = "RenderSubdivisionNotLessThenViewport"
    failedMessage = "These objects have render subdivision less than viewport subdivision:"
    homeworks = [2,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objects = [] 
            for obj in bpy.data.objects:
                subsurf_modifier = obj.modifiers.get('Subdivision')
                if subsurf_modifier:
                    if subsurf_modifier.render_levels < subsurf_modifier.levels:
                        objects.append(obj)

            if(objects == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for obj in objects:
                    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)

@register_test
class DiffuseImageMapIsRGB(Test):
    label = "Diffuse Image Map Is sRGB"
    failedMessage = "Those textures are not in sRGB space:"
    homeworks = [2,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objects = [] 
            for material in bpy.data.materials:
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            if image and node.label == "Diffuse":
                                color_space = image.colorspace_settings.name
                                if color_space != 'sRGB':
                                    objects.append(material.name)

            if(objects == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for obj in objects:
                    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)

@register_test
class NoInappropriateMetallness(Test):
    label = "No Inappropriate Metallness"
    failedMessage = "Materials should have 0.0 or 1.0 metallic values. \n Those materials:"
    homeworks = [2,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objects = [] 
            for material in bpy.data.materials:
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            metallic_value = node.inputs['Metallic'].default_value
                            if(metallic_value>0.01 and metallic_value<0.99):
                                objects.append(material)

            if(objects == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for obj in objects:
                    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.WARNING)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)


@register_test
class NoFlatShading(Test):
    label = "No Flat Shading"
    failedMessage = "Don't use flat shading.\n Those objects use flat shading:"
    homeworks = [2,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objects = [] 
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                    flat_shaded = all(not poly.use_smooth for poly in obj.data.polygons)
                    if flat_shaded:
                        objects.append(obj)

            if(objects == []):
                self.setState(TEST_STATE.PASSED)
            else:
                for obj in objects:
                    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)

@register_test
class NoSingleObject(Test): #object or mesh???
    label = "No Single Object"
    failedMessage = "There should not be single object.\n"
    homeworks = [2,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objects = [] 
            nObjects = len(bpy.context.scene.objects)

            if(nObjects > 1):
                self.setState(TEST_STATE.PASSED)
            else:
                #for obj in objects:
                #    self.addObjectNameToMessage(obj.name)
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)


@register_test
class ReferencesPresentTest(Test): #object or mesh???
    label = "References Present"
    failedMessage = "There should be atleast two reference images.\n"
    homeworks = [2,3,4]
    def is_applicable(self,context):
        return True

    def execute(self,context):
        try:         
            objects = [] 
            nObjects = len(bpy.context.scene.objects)

            if(nObjects > 1):
                self.setState(TEST_STATE.PASSED)
            else:
                self.setState(TEST_STATE.FAILED)

        except:
            self.traceback = traceback.format_exc()
            self.setState(TEST_STATE.BROKEN)