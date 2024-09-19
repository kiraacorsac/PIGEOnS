import typing
import bpy
from enum import Enum
from . import utils
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

def get_all_student_work_batteries():
    return filter(lambda bat: not bat._id.startswith("Showcase_"), get_all_batteries())

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
    
@register_test
class NoDefaultName(Test):
    label = "No default names"
    homeworks = get_all_student_work_batteries()

    def execute(self, context):
        def is_default_name(obj_name: str, default_name: str):
            return obj_name == default_name or obj_name.startswith(default_name + ".")
        
        self.setState(TestState.OK)

        forbidden_names = [
            (bpy.data.objects, ["Cube", "Plane", "Cylinder", "Sphere", "Icosphere", "Curve", "BézierCurve", "NurbsCurve", "NurbsPath"]),
            (bpy.data.materials, ["Material"]),
            (bpy.data.images, ["Image"])
        ]

        wrongly_named_objects = []
        for datablocks, names in forbidden_names:
            for datablock in utils.filter_used_datablocks(datablocks):
                for name in names:
                    if is_default_name(datablock.name, name):
                        wrongly_named_objects.append(datablock)

        if len(wrongly_named_objects) > 0:
            self.setState(TestState.WARNING)
            self.setFailedInfo(
                None,
                f"The following datablocks - {', '.join([obj.name for obj in wrongly_named_objects])} - use default names. "
                f"these are not descriptive and may confuse others working on the same scene, "
                f"or others using these objects in their scene. Use descriptive names instead."
            )



@register_test
class MaterialsSet(Test):
    label = "No objects without materials"
    homeworks = get_all_student_work_batteries()
    # visType = VIS_TYPE.POLYGON

    def execute(self,context):
        self.setState(TestState.OK)
        objects_missing_materials = [] 
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            if obj.type != 'CURVE' and obj.type != 'MESH':
                continue
            if len(obj.material_slots) > 0:
                continue
            objects_missing_materials.append(obj)

        if len(objects_missing_materials) > 0:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"The following datablocks - {', '.join([obj.name for obj in objects_missing_materials])} - don't have any materials assigned. "
                f"These objects will have default 'grey' material in the render. We would like something better :)"
            )

@register_test
class NoEmptyMaterialSlotsSet(Test):
    label = "No objects with empty material slots"
    homeworks = get_all_student_work_batteries()
    # visType = VIS_TYPE.POLYGON

    def execute(self,context):
        self.setState(TestState.OK)
        objects_missing_materials = [] 
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            for material_slot in obj.material_slots:
                if material_slot.material is None:
                    objects_missing_materials.append(obj)

        if len(objects_missing_materials) > 0:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"The following datablocks - {', '.join([obj.name for obj in objects_missing_materials])} - have empty material slots. "
                f"Parts of the object that are assigned empty material slot will have default 'grey' material in the render. We would like something better :)"
            )

@register_test
class NoTris(Test):
    label = "No triangles"
    homeworks = get_all_student_work_batteries()
    # visType = VIS_TYPE.POLYGON

    def execute(self,context):
        self.setState(TestState.OK)
        objects_with_triangles = set() 
        current_mode = bpy.context.object.mode
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            if obj.type == 'MESH':
                bpy.ops.object.mode_set(mode='OBJECT')
                for poly in obj.data.polygons:
                    if len(poly.vertices) == 3: 
                        objects_with_triangles.add(obj) 
                        # self.setVisData(obj.name,poly.index) 
                bpy.ops.object.mode_set(mode=current_mode)

        if len(objects_with_triangles) > 0:
            self.setFailedInfo(
                None,
                f"The following meshes - {', '.join([obj.name for obj in objects_with_triangles])} - have triangles. "
                f"Triangles are faces with exactly 3 vertices. Triangular faces make it hard to edit the mesh, "
                f"may deform incorrectly during animation, may cause shading issues, and don't play well with subdivision modifier. "
                f"Stay quad!"
            )
            self.setState(TestState.WARNING)


@register_test
class NoNgons(Test):
    label = "No N-gons"
    homeworks = get_all_student_work_batteries()
    # visType = VIS_TYPE.POLYGON

    def execute(self,context):
        self.setState(TestState.OK)
        objects_with_ngons = set() 
        current_mode = bpy.context.object.mode
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            if obj.type == 'MESH':
                bpy.ops.object.mode_set(mode='OBJECT')
                for poly in obj.data.polygons:
                    if len(poly.vertices) > 4: 
                        objects_with_ngons.add(obj) 
                        # self.setVisData(obj.name,poly.index) 
                bpy.ops.object.mode_set(mode=current_mode)

        if len(objects_with_ngons) > 0:
            self.setFailedInfo(
                None,
                f"The following meshes - {', '.join([obj.name for obj in objects_with_ngons])} - have N-gons. "
                f"N-gons (for N > 4 :)) are faces with more then 4 vertices. N-gon faces make it hard to edit the mesh, "
                f"may deform incorrectly during animation, will cause shading issues unless co-planar, "
                f"and don't play well with subdivision modifier. Stay quad!"
            )
            self.setState(TestState.ERROR)


@register_test
class NoCrazySubdivision(Test):
    label = "No crazy subdivision level"
    homeworks = get_all_student_work_batteries()

    def execute(self,context):
        self.setState(TestState.OK)
        objects_with_high_subdivision = [] 
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            for mod in obj.modifiers:
                if isinstance(mod, bpy.types.SubsurfModifier):
                    if mod.levels > 4 or mod.render_levels > 6:
                        objects_with_high_subdivision.append(obj)

        if len(objects_with_high_subdivision) > 0:
            self.setFailedInfo(
                None,
                f"The following objects - {', '.join([obj.name for obj in objects_with_high_subdivision])} - have really high subdivision. "
                f"It is almost definitely unnecessary to have this high subdivision level. Are you trying to make something look smooth? "
                f"Have you tried right click -> shade smooth? That might do what you are trying to do."
            )
            self.setState(TestState.WARNING)

@register_test
class RenderSubdivisionNotLessThenViewport(Test):
    label = "Render subdivision not less then viewport"
    homeworks = get_all_student_work_batteries()

    def execute(self,context):
        self.setState(TestState.OK)
        objects_with_incorrect_subdivision = [] 
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            for mod in obj.modifiers:
                if isinstance(mod, bpy.types.SubsurfModifier):
                    if mod.render_levels < mod.levels:
                        objects_with_incorrect_subdivision.append(obj)

        if len(objects_with_incorrect_subdivision) > 0:
            self.setFailedInfo(
                None,
                f"The following objects - {', '.join([obj.name for obj in objects_with_incorrect_subdivision])} - have viewport subdivision level higher then render subdivision level. "
                f"This does not make sense. It will take more resources during working in the viewport, and look lower quality in the render."
            )
            self.setState(TestState.ERROR)



# @register_test
# class DiffuseImageMapIsRGB(Test):
#     label = "Diffuse Image Map Is sRGB"
#     failedMessage = "Those textures are not in sRGB space:"
#     homeworks = [2,3,4]
#     def is_applicable(self,context):
#         return True

#     def execute(self,context):
#         try:         
#             objects = [] 
#             for material in bpy.data.materials:
#                 if material.use_nodes:
#                     for node in material.node_tree.nodes:
#                         if node.type == 'TEX_IMAGE':
#                             image = node.image
#                             if image and node.label == "Diffuse":
#                                 color_space = image.colorspace_settings.name
#                                 if color_space != 'sRGB':
#                                     objects.append(material.name)

#             if(objects == []):
#                 self.setState(TestState.OK)
#             else:
#                 for obj in objects:
#                     self.addObjectNameToMessage(obj.name)
#                 self.setState(TestState.ERROR)

#         except:
#             self.traceback = traceback.format_exc()
#             self.setState(TestState.CRASH)

# @register_test
# class NoInappropriateMetallness(Test):
#     label = "No Inappropriate Metallness"
#     failedMessage = "Materials should have 0.0 or 1.0 metallic values. \n Those materials:"
#     homeworks = [2,3,4]
#     def is_applicable(self,context):
#         return True

#     def execute(self,context):
#         try:         
#             objects = [] 
#             for material in bpy.data.materials:
#                 if material.use_nodes:
#                     for node in material.node_tree.nodes:
#                         if node.type == 'BSDF_PRINCIPLED':
#                             metallic_value = node.inputs['Metallic'].default_value
#                             if(metallic_value>0.01 and metallic_value<0.99):
#                                 objects.append(material)

#             if(objects == []):
#                 self.setState(TestState.OK)
#             else:
#                 for obj in objects:
#                     self.addObjectNameToMessage(obj.name)
#                 self.setState(TestState.WARNING)

#         except:
#             self.traceback = traceback.format_exc()
#             self.setState(TestState.CRASH)


# @register_test
# class NoFlatShading(Test):
#     label = "No Flat Shading"
#     failedMessage = "Don't use flat shading.\n Those objects use flat shading:"
#     homeworks = [2,3,4]
#     def is_applicable(self,context):
#         return True

#     def execute(self,context):
#         try:         
#             objects = [] 
#             for obj in bpy.context.scene.objects:
#                 if obj.type == 'MESH':
#                     flat_shaded = all(not poly.use_smooth for poly in obj.data.polygons)
#                     if flat_shaded:
#                         objects.append(obj)

#             if(objects == []):
#                 self.setState(TestState.OK)
#             else:
#                 for obj in objects:
#                     self.addObjectNameToMessage(obj.name)
#                 self.setState(TestState.ERROR)

#         except:
#             self.traceback = traceback.format_exc()
#             self.setState(TestState.CRASH)

# @register_test
# class NoSingleObject(Test): #object or mesh???
#     label = "No Single Object"
#     failedMessage = "There should not be single object.\n"
#     homeworks = [2,3,4]
#     def is_applicable(self,context):
#         return True

#     def execute(self,context):
#         try:         
#             objects = [] 
#             nObjects = len(bpy.context.scene.objects)

#             if(nObjects > 1):
#                 self.setState(TestState.OK)
#             else:
#                 #for obj in objects:
#                 #    self.addObjectNameToMessage(obj.name)
#                 self.setState(TestState.ERROR)

#         except:
#             self.traceback = traceback.format_exc()
#             self.setState(TestState.CRASH)


# @register_test
# class ReferencesPresentTest(Test): #object or mesh???
#     label = "References Present"
#     failedMessage = "There should be atleast two reference images.\n"
#     homeworks = [2,3,4]
#     def is_applicable(self,context):
#         return True

#     def execute(self,context):
#         try:         
#             objects = [] 
#             nObjects = len(bpy.context.scene.objects)

#             if(nObjects > 1):
#                 self.setState(TestState.OK)
#             else:
#                 self.setState(TestState.ERROR)

#         except:
#             self.traceback = traceback.format_exc()
#             self.setState(TestState.CRASH)