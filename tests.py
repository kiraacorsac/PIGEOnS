import typing
import bpy
import bmesh
import math
import mathutils
from enum import Enum
from . import utils
from .testVisualisation import selectPolygon, VIS_TYPE


def resetTests():
    for _, tests in TEST_REGISTRY.items():
        for test in tests:
            test.reset()


class HomeworkBatteryInfo:
    def __init__(self, homework_battery_label: str, order=math.inf):
        self.order = order
        self._id = homework_battery_label.replace(" ", "").replace("-", "").lower()
        self._label = homework_battery_label


class HomeworkBatteries:
    HW2 = HomeworkBatteryInfo("Homework 2 - Composition", 20)
    HW3chair = HomeworkBatteryInfo("Homework 3 - Chair", 30)
    HW3your = HomeworkBatteryInfo("Homework 3 - Your own model", 31)
    HW4 = HomeworkBatteryInfo("Homework 4 - Retopology", 40)
    HW5 = HomeworkBatteryInfo("Homework 5 - Materials", 50)
    # HW6 = HomeworkBatteryInfo("Homework 6")
    # HW7 = HomeworkBatteryInfo("Homework 7")
    Showcase_OK = HomeworkBatteryInfo("Showcase - OK", 101)
    Showcase_warning = HomeworkBatteryInfo("Showcase - Warning", 102)
    Showcase_error = HomeworkBatteryInfo("Showcase - Error", 103)
    Showcase_crash = HomeworkBatteryInfo("Showcase - Crash", 104)
    Showcase_skip = HomeworkBatteryInfo("Showcase - Skip", 105)


def get_all_batteries():
    return sorted(
        [
            getattr(HomeworkBatteries, hw_key)
            for hw_key in dir(HomeworkBatteries)
            if not hw_key.startswith("_")
        ],
        key=lambda b: b.order,
    )


def get_all_student_work_batteries():
    return filter(lambda bat: not bat._id.startswith("showcase"), get_all_batteries())


TEST_REGISTRY = {}


class FailedInfo:
    dataBlock: bpy.props.StringProperty()
    message: bpy.props.StringProperty()

    def __init__(self) -> None:
        self.dataBlock = ""
        self.message = ""


class VisData:
    method = None
    objectName = ""
    dataID = None


class TestState(Enum):
    INIT = 0
    OK = 1
    WARNING = 2
    ERROR = 3
    CRASH = 4
    SKIPPED = 5


class Test:
    testId = 0
    label = ""
    state = TestState.INIT
    failedMessage = ""
    homeworks = []
    traceback = ""
    visData = None
    visType = VIS_TYPE.NONE
    objects = []

    def __init__(self):
        self.failedInfo = FailedInfo()
        self.testId = Test.testId
        Test.testId += 1

    def is_applicable(self, context):
        return True

    def execute(self, context):
        pass

    def setFailedInfo(self, _dataBlock, _message):
        self.failedInfo = FailedInfo()
        self.failedInfo.dataBlock = _dataBlock
        self.failedInfo.message = _message

    def addObjectNameToMessage(self, objectName):
        self.failedMessage = self.failedMessage + "\n" + objectName

    def reset(self):
        self.state = TestState.INIT
        self.failedMessage = ""
        self.failedInfo: FailedInfo
        self.traceback = ""

    def setVisData(self, objectName, dataID):
        v = VisData()
        v.objectName = objectName
        v.dataID = dataID
        self.visData = v

    def setState(self, state):
        self.state = state


def register_test(test: typing.Type[Test]):
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
            f"Better make sure, unless you have a very good reason, we will make you redo this homework.",
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
            f"We will definitely make you redo your homework if you turn it in with this error.",
        )


@register_test
class Crash_Test(Test):
    label = "This test always ends up as crash"
    homeworks = [HomeworkBatteries.Showcase_crash]

    def execute(self, context):
        raise Exception(
            f"The problem is not on your side!\n"
            f"Something is definitely incorrect, but it's on us. Please safe the file as-is,\n"
            f"copy the traceback with this button, and send both the blend and traceback to your teachers."
        )


@register_test
class Skip_Test(Test):
    label = "This test does not run"
    homeworks = [HomeworkBatteries.Showcase_skip]

    def is_applicable(self, context):
        return False

    def execute(self, context):
        raise Exception(f"You should not ever see this.")


@register_test
class NoDefaultName(Test):
    label = "No default names"
    homeworks = [HomeworkBatteries.HW3chair, HomeworkBatteries.HW3your]

    def execute(self, context):
        def is_default_name(obj_name: str, default_name: str):
            return obj_name == default_name or obj_name.startswith(default_name + ".")

        self.setState(TestState.OK)

        forbidden_names: list[tuple[typing.Iterable[bpy.types.ID], list[str]]] = [
            (
                bpy.data.objects,
                [
                    "Cube",
                    "Plane",
                    "Cylinder",
                    "Sphere",
                    "Icosphere",
                    "Curve",
                    "BézierCurve",
                    "NurbsCurve",
                    "NurbsPath",
                ],
            ),
            (bpy.data.materials, ["Material"]),
            (bpy.data.images, ["Image"]),
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
                f"The following datablocks - {', '.join([obj.name for obj in wrongly_named_objects])} - use default names.\n\n"
                f"these are not descriptive and may confuse others working on the same scene, "
                f"or others using these objects in their scene. Use descriptive names instead.",
            )


@register_test
class MaterialsSet(Test):
    label = "No objects without materials"
    homeworks = [HomeworkBatteries.HW2, HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)
        objects_missing_materials = []
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            if obj.type != "CURVE" and obj.type != "MESH":
                continue
            if len(obj.material_slots) > 0:
                continue
            objects_missing_materials.append(obj)

        if len(objects_missing_materials) > 0:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"The following datablocks - {', '.join([obj.name for obj in objects_missing_materials])} - don't have any materials assigned.\n\n"
                f"These objects will have default 'grey' material in the render. We would like something better :)",
            )


@register_test
class NoEmptyMaterialSlotsSet(Test):
    label = "No objects with empty material slots"
    homeworks = [HomeworkBatteries.HW2]
    # visType = VIS_TYPE.POLYGON

    def execute(self, context):
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
                f"The following datablocks - {', '.join([obj.name for obj in objects_missing_materials])} - have empty material slots.\n\n"
                f"Parts of the object that are assigned empty material slot will have default 'grey' material in the render. We would like something better :)",
            )


@register_test
class NoTris(Test):
    label = "No triangles"
    homeworks = [
        HomeworkBatteries.HW3chair,
        HomeworkBatteries.HW3your,
        HomeworkBatteries.HW4,
    ]
    # visType = VIS_TYPE.POLYGON

    def execute(self, context):
        context.view_layer.update()
        self.setState(TestState.OK)
        objects_with_triangles = set()
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            if obj.type == "MESH":
                assert isinstance(obj.data, bpy.types.Mesh)
                if (
                    bpy.context.object is not None
                    and bpy.context.object == obj
                    and bpy.context.object.mode == "EDIT"
                ):
                    mesh = bmesh.from_edit_mesh(obj.data)
                else:
                    mesh = bmesh.new()
                    mesh.from_mesh(obj.data)
                for face in mesh.faces:
                    if len(face.verts) == 3:
                        objects_with_triangles.add(obj)
                        # self.setVisData(obj.name,poly.index)

        if len(objects_with_triangles) > 0:
            self.setFailedInfo(
                None,
                f"The following meshes - {', '.join([obj.name for obj in objects_with_triangles])} - have triangles.\n\n"
                f"Triangles are faces with exactly 3 vertices. Triangular faces make it hard to edit the mesh, "
                f"may deform incorrectly during animation, may cause shading issues, and don't play well with subdivision modifier. "
                f"Stay quad!",
            )
            self.setState(TestState.WARNING)


@register_test
class NoNgons(Test):
    label = "No N-gons"
    homeworks = [
        HomeworkBatteries.HW3chair,
        HomeworkBatteries.HW3your,
        HomeworkBatteries.HW4,
    ]
    # visType = VIS_TYPE.POLYGON

    def execute(self, context):
        self.setState(TestState.OK)
        objects_with_ngons = set()
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            if obj.type == "MESH":
                assert isinstance(obj.data, bpy.types.Mesh)
                if (
                    bpy.context.object is not None
                    and bpy.context.object == obj
                    and bpy.context.object.mode == "EDIT"
                ):
                    mesh = bmesh.from_edit_mesh(obj.data)
                else:
                    mesh = bmesh.new()
                    mesh.from_mesh(obj.data)
                for face in mesh.faces:
                    if len(face.verts) > 4:
                        objects_with_ngons.add(obj)
                        # self.setVisData(obj.name,poly.index)

        if len(objects_with_ngons) > 0:
            self.setFailedInfo(
                None,
                f"The following meshes - {', '.join([obj.name for obj in objects_with_ngons])} - have N-gons.\n\n"
                f"N-gons (for N > 4 :)) are faces with more then 4 vertices. N-gon faces make it hard to edit the mesh, "
                f"may deform incorrectly during animation, will cause shading issues unless co-planar, "
                f"and don't play well with subdivision modifier. Stay quad!",
            )
            self.setState(TestState.ERROR)


@register_test
class NoCrazySubdivision(Test):
    label = "No crazy subdivision level"
    homeworks = get_all_student_work_batteries()

    def execute(self, context):
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
                f"The following objects - {', '.join([obj.name for obj in objects_with_high_subdivision])} - have really high subdivision.\n\n"
                f"It is almost definitely unnecessary to have this high subdivision level. Are you trying to make something look smooth? "
                f"Have you tried right click -> shade smooth? That might do what you are trying to do.",
            )
            self.setState(TestState.WARNING)


@register_test
class RenderSubdivisionNotLessThenViewport(Test):
    label = "Render subdivision not less then viewport"
    homeworks = get_all_student_work_batteries()

    def execute(self, context):
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
                f"The following objects - {', '.join([obj.name for obj in objects_with_incorrect_subdivision])} - have viewport subdivision level higher then render subdivision level.\n\n"
                f"This does not make sense. It will take more resources during working in the viewport, and look lower quality in the render.",
            )
            self.setState(TestState.ERROR)


@register_test
class NoMaterialsWithoutNodes(Test):
    label = "Materials use nodes"
    homeworks = get_all_student_work_batteries()

    def execute(self, context):
        self.setState(TestState.OK)
        nodeless_materials = []
        for mat in utils.filter_used_datablocks(bpy.data.materials):
            if not mat.use_nodes:
                if mat.name == "Dots Stroke":  # ignore weird inbuild material
                    continue
                nodeless_materials.append(mat)
        if len(nodeless_materials) > 0:
            self.setFailedInfo(
                None,
                f"The following materials - {', '.join([obj.name for obj in nodeless_materials])} - don't use nodes. Such materials are basically deprecated Blender.\n\n"
                f"Please use only materials with nodes.",
            )
            self.setState(TestState.ERROR)


@register_test
class NoUnreallisticMetallness(Test):
    label = "No unreallistic metallness"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)
        hausler_alloys = []
        for material in utils.filter_used_datablocks(bpy.data.materials):
            if material.use_nodes:
                assert material.node_tree is not None
                for node in material.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        metallic_value = node.inputs["Metallic"].default_value
                        if not (metallic_value < 0.01 or metallic_value > 0.99):
                            hausler_alloys.append(material)

        if len(hausler_alloys) > 0:
            self.setFailedInfo(
                None,
                f"The following materials - {', '.join([obj.name for obj in hausler_alloys])} - use metalness values between 0 and 1.\n\n"
                f"Such materials are not based on realistic properties - there are not many 'half-metals' in this world. "
                f"Please, set up reallistic materials - either metals or non-metals.",
            )
            self.setState(TestState.ERROR)


@register_test
class NoFlatShading(Test):
    label = "No Flat Shading"
    homeworks = [HomeworkBatteries.HW3chair, HomeworkBatteries.HW4]

    def execute(self, context):
        self.setState(TestState.OK)
        flat_shaded_objects = []
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            if obj.type == "MESH":
                assert isinstance(obj.data, bpy.types.Mesh)
                flat_shaded = all(not poly.use_smooth for poly in obj.data.polygons)
                if flat_shaded:
                    flat_shaded_objects.append(obj)

        if len(flat_shaded_objects) > 0:
            self.setFailedInfo(
                None,
                f"The following objects - {', '.join([obj.name for obj in flat_shaded_objects])} - use flat shading on one or more faces.\n\n"
                f"The style of modelling requested in the homework calls for using smooth shading only. Flat shading will be visible in render. "
                f"If you are trying to use flat shading on purpose, you can probably achieve the same results using weighted normals modifier.",
            )
            self.setState(TestState.WARNING)


@register_test
class NoSingleMeshObject(Test):
    label = "No Single Mesh Object"
    homeworks = [
        HomeworkBatteries.HW3chair,
    ]

    def execute(self, context):
        self.setState(TestState.OK)
        if (
            len(
                utils.filter_used_datablocks(
                    obj for obj in bpy.data.objects if obj.type == "MESH"
                )
            )
            <= 1
        ):
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"This style of modelling calls for assembling the mesh from smaller parts. "
                f"Do not build you model as a singular mesh, instead, model each part as a separate object. ",
            )


@register_test
class ReferencesPresent(Test):
    label = "References Present"
    homeworks = [HomeworkBatteries.HW3your]

    def execute(self, context):
        self.setState(TestState.OK)
        reference_images = utils.filter_used_datablocks(
            obj for obj in bpy.data.objects if "reference" in obj.name.lower()
        )

        if len(reference_images) < 2:
            self.setFailedInfo(
                None,
                f"You need to use at least two references in this scene. We recommend using front and side references. "
                f"Mark your references by including the word 'reference' in the name of the object that houses the image. ",
            )
            self.setState(TestState.ERROR)


@register_test
class PackedImages(Test):
    label = "Packed Images"
    homeworks = get_all_student_work_batteries()

    def execute(self, context):
        self.setState(TestState.OK)
        unpacked_images = utils.filter_used_datablocks(
            img
            for img in bpy.data.images
            if img.packed_file is None and img.filepath != "" and img.filepath != "//"
        )
        if len(unpacked_images) > 0:
            self.setFailedInfo(
                None,
                f"The following images are not packed - {', '.join([obj.name for obj in unpacked_images])} - please pack your resources for easier review process.\n\n"
                f"Go to File -> External Data -> Pack Resources (or Automatically Pack Resources).",
            )
            self.setState(TestState.ERROR)


@register_test
class UseCycles(Test):
    label = "Use Cycles"
    homeworks = [HomeworkBatteries.HW5]  # only the material one

    def execute(self, context):
        self.setState(TestState.OK)
        if context.scene.render.engine != "CYCLES":
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Use Cycles rendering engine. More complex materials don't work in {context.scene.render.engine} out-of-the-box. Renders with EEVEE are acceptable only if you set it up correctly.",
            )


@register_test
class UseGPU(Test):
    label = "Use GPU"
    homeworks = get_all_student_work_batteries()

    def is_applicable(self, context):
        return context.scene.render.engine == "CYCLES"

    def execute(self, context):
        self.setState(TestState.OK)
        cycles = bpy.context.preferences.addons.data.addons["cycles"]
        # assuming that if a computer has more then 1 device, it's a GPU
        has_gpu = len(cycles.preferences.devices) > 1
        render_using_gpu = context.scene.cycles.device == "GPU"
        set_compute_device = cycles.preferences.compute_device_type != "NONE"
        if has_gpu and not (render_using_gpu and set_compute_device):
            self.setState(TestState.WARNING)
            self.setFailedInfo(
                None,
                f"Use your GPU for rendering. It will be probably much faster.\n\n"
                f"In render properties, make sure Device is set to GPU Compute. "
                f"In Preferences -> System -> Cycles Render Devices, make sure you have appropriate device type selected (probably CUDA or OptiX). "
                f"Ignore this warning if you empirically observed that your CPU is faster (e.g. you have no dedicated GPU), "
                f"or if Blender tells you that you have no compatible GPUs found.",
            )


@register_test
class UseModifiers(Test):
    label = "Use modifiers"
    homeworks = [HomeworkBatteries.HW2]

    def execute(self, context):
        self.setState(TestState.OK)
        modifiers = set()
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            for mod in obj.modifiers:
                modifiers.add(mod)
        if len(modifiers) < 2:
            self.setState(TestState.WARNING)
            self.setFailedInfo(
                None,
                f"We would like you to use some (at least 2) modifiers in this homework. For example, 'Array' or 'Simple Deform' are useful!",
            )


@register_test
class UseBevelOrSubdivModifiers(Test):
    label = "Use modifiers"
    homeworks = [
        HomeworkBatteries.HW3chair,
        HomeworkBatteries.HW3your,
        HomeworkBatteries.HW4,
    ]

    def execute(self, context):
        self.setState(TestState.OK)
        modifiers = set()
        for obj in utils.filter_used_datablocks(bpy.data.objects):
            for mod in obj.modifiers:
                if isinstance(mod, bpy.types.SubsurfModifier) or isinstance(
                    mod, bpy.types.BevelModifier
                ):
                    modifiers.add(mod)
        if len(modifiers) < 1:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"We would like you to use modifiers to create holding edges for objects in this homework. 'Subdivision Surface' or 'Bevel' can work!",
            )


@register_test
class UnwrapTexturedObjects(Test):
    label = "Unwrap bear and books"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)
        bear_objects = utils.filter_used_datablocks(bpy.data.objects)
        bear_objects = [
            obj
            for obj in bear_objects
            if "bear_" in obj.name.lower() or "book_" in obj.name.lower()
        ]
        # for every bear object, check if it has UV map, then check if all UV vertices are in 0,0
        no_uv_map_objects = set()
        low_quality_uv_map_objects = set()
        for obj in bear_objects:
            if obj.type != "MESH":
                continue
            assert isinstance(obj.data, bpy.types.Mesh)

            if obj.mode == "EDIT":
                bm = bmesh.from_edit_mesh(obj.data)
            else:
                bm = bmesh.new()
                bm.from_mesh(obj.data)
            uv_layer = bm.loops.layers.uv.verify()

            for face in bm.faces:
                for loop in face.loops:
                    if math.isclose(
                        loop[uv_layer].uv.x, -0.1, abs_tol=0.001
                    ) or math.isclose(loop[uv_layer].uv.y, -0.1, abs_tol=0.001):
                        no_uv_map_objects.add(obj)

            for face in bm.faces:
                for loop in face.loops:
                    if math.isclose(
                        loop[uv_layer].uv.x, -0.1, abs_tol=0.001
                    ) and math.isclose(loop[uv_layer].uv.y, -0.1, abs_tol=0.001):
                        no_uv_map_objects.add(obj)

            if obj.mode != "EDIT":
                bm.free()

        no_map_string = f"Objects {', '.join([obj.name for obj in no_uv_map_objects])} are part of the bear, but they don't have any UV map. Please unwrap them."
        low_quality_uv_map_string = f"Objects {', '.join([obj.name for obj in low_quality_uv_map_objects])} are part of the bear, but their UV map has very high stretch. Please unwrap them better."

        if len(no_uv_map_objects) > 0:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                no_map_string
                + (
                    ("\n\n" + low_quality_uv_map_string)
                    if len(low_quality_uv_map_objects) > 0
                    else ""
                ),
            )
            return
        if len(low_quality_uv_map_objects) > 0:
            self.setState(TestState.WARNING)
            self.setFailedInfo(None, low_quality_uv_map_string)
            return


@register_test
class ChristmasTreeLightsEmitLight(Test):
    label = "Christmas tree lights emit light"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)

        lights = bpy.data.objects.get("Xmas tree lights", None)
        if lights is None:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Christmas tree lights should be a separate object named 'Xmas tree lights'.",
            )
            return

        # get materials on lights
        materials = set()
        for slot in lights.material_slots:
            if slot.material is not None:
                materials.add(slot.material)

        emits = False
        for material in materials:
            if material.use_nodes:
                assert material.node_tree is not None
                for node in material.node_tree.nodes:
                    if node.type == "EMISSION":
                        if node.inputs["Strength"].default_value > 1:
                            emits = True
                    if node.type == "BSDF_PRINCIPLED":
                        if node.inputs["Emission Strength"].default_value > 1:
                            emits = True
        if not emits:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Christmas tree lights should emit light. Otherwise, they are just a decoration. "
                f"Use Principled BSDF or dedicated Emission node with Emission Strength > 1.",
            )


@register_test
class GemIsTransparent(Test):
    label = "Gem is transparent"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)

        gem = bpy.data.objects.get("Gem", None)
        if gem is None:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Gem should be a separate object named 'Gem'.",
            )
            return

        materials = set()
        for slot in gem.material_slots:
            if slot.material is not None:
                materials.add(slot.material)

        transparent = False
        for material in materials:
            if material.use_nodes:
                assert material.node_tree is not None
                for node in material.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        if node.inputs["Transmission Weight"].default_value > 0.7 and (
                            node.inputs["Roughness"].default_value < 0.5
                            or node.inputs["Roughness"].is_linked
                        ):
                            transparent = True
                    if node.type == "BSDF_GLASS" or node.type == "BSDF_TRANSPARENT":
                        transparent = True
        if not transparent:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Gem should be transparent. "
                f"Use Principled BSDF with Transmission > 0.7 and Roughness < 0.5 or a texture, or mix Glass and Transparent BSDF node.",
            )


@register_test
class RubiksCubeHas6Colors(Test):
    label = "Rubik's cube has 6 colors"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)

        rubiks_cube = bpy.data.objects.get("Rubik's Cube", None)
        if rubiks_cube is None:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Rubik's Cube should be a separate object named 'Rubik's Cube'.",
            )
            return

        materials = set()
        for slot in rubiks_cube.material_slots:
            materials.add(slot.material)

        if len(materials) < 6:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Rubik's Cube should have 6 different colors. "
                f"Each color of the cube should have a different material assigned. "
                f"Solutions with textures (both procedural and bitmaps) are also acceptable, in that case you can ignore this pigeon.",
            )


@register_test
class PigBankIsPorcelain(Test):
    label = "Pig Bank is porcelain"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)

        pig = bpy.data.objects.get("Pig_bank", None)
        if pig is None:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Pig Bank should be a separate object named 'Pig_bank'.",
            )
            return

        materials = set()
        for slot in pig.material_slots:
            if slot.material is not None:
                materials.add(slot.material)

        porcelain = False
        for material in materials:
            if material.use_nodes:
                assert material.node_tree is not None
                for node in material.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        if node.inputs["Subsurface Weight"].default_value > 0.1 and (
                            node.inputs["Roughness"].default_value < 0.5
                            or node.inputs["Roughness"].is_linked
                        ):
                            porcelain = True
        if not porcelain:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Pig should be made of porcelain. "
                f"Use Principled BSDF with Subsurface > 0.1 and Roughness < 0.5 or a texture."
                f"Alternative solutions using SSS are also acceptable, in that case you can ignore this pigeon.",
            )


@register_test
class CoinsAreMetal(Test):
    label = "Coins are metal"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)

        coins = set()
        for obj in bpy.data.objects:
            if obj.name.startswith("Coin"):
                coins.add(obj)
        if len(coins) == 0:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Coins should be separate objects with 'Coin' prefix.",
            )
            return

        materials = set()
        for coin in coins:
            for slot in coin.material_slots:
                if slot.material is not None:
                    materials.add(slot.material)

        metal = False
        for material in materials:
            if material.use_nodes:
                assert material.node_tree is not None
                for node in material.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        if (
                            node.inputs["Metallic"].default_value > 0.99
                            or node.inputs["Metallic"].is_linked
                        ):
                            metal = True
        if not metal:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"Coins should be made of metal. "
                f"Use Principled BSDF with Metallic > 0.99 or an appropriate texture."
                f"Alternative solutions using glossy shaders are also acceptable, in that case you can ignore this pigeon.",
            )


class UseHWFile:
    error_message = "Please use the provided starting file. It's available for download in the IS study materials and the interactive syllaby."


@register_test
class UseHW2File(Test, UseHWFile):
    label = "Use starting file"
    homeworks = [HomeworkBatteries.HW2]

    def execute(self, context):
        self.setState(TestState.OK)
        if not context.scene.get("pigeons_hw2_flagpost", False):
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                self.error_message,
            )


@register_test
class UseHW3ChairFile(Test, UseHWFile):
    label = "Use starting file"
    homeworks = [HomeworkBatteries.HW3chair]

    def execute(self, context):
        self.setState(TestState.OK)
        if not context.scene.get("pigeons_hw3chair_flagpost", False):
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                self.error_message,
            )


@register_test
class UseHW4File(Test, UseHWFile):
    label = "Use starting file"
    homeworks = [HomeworkBatteries.HW4]

    def execute(self, context):
        self.setState(TestState.OK)
        if not context.scene.get("pigeons_hw4_flagpost", False):
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                self.error_message,
            )


@register_test
class UseHW5File(Test, UseHWFile):
    label = "Use starting file"
    homeworks = [HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)
        if not context.scene.get("pigeons_hw5_flagpost", False):
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                self.error_message,
            )


@register_test
class UseLights(Test):
    label = "Use lights"
    homeworks = [HomeworkBatteries.HW2, HomeworkBatteries.HW5]

    def execute(self, context):
        self.setState(TestState.OK)
        lights = set()
        for light in utils.filter_used_datablocks(bpy.data.lights):
            lights.add(light)

        if len(lights) < 1:
            self.setState(TestState.ERROR)
            self.setFailedInfo(
                None,
                f"You need to have lights in your scene, otherwise nothing will be visible on the final renders.",
            )


@register_test
class SaveYourWork(Test):
    label = "Save your work"
    homeworks = get_all_student_work_batteries()

    def execute(self, context):
        self.setState(TestState.OK)
        if bpy.data.filepath == "":  # Not saved
            self.setState(TestState.ERROR)
            self.setFailedInfo(None, f"Please save your work to avoid loss of data.")
