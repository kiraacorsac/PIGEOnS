import bpy
from . import tests
from . import testRunner
from . import utils
from . import updates
from .testVisualisation import selectPolygon, VIS_TYPE


def remove_trailing_dot(string: str):
    """Blender UI automatically appends dot to details"""
    return string.removesuffix(".")


class PigeonProperties(bpy.types.PropertyGroup):
    def onChange(self, context):
        testRunner.resetTestResults()
        tests.resetTests()

    homework_selector: bpy.props.EnumProperty(
        name="",
        description="Select an option",
        items=[
            (
                battery._id,
                battery._label,
                battery._label,
            )
            for battery in tests.get_all_batteries()
        ],
        update=onChange,
    )

    updater: bpy.props.BoolProperty(default=False)


def create_visualisation_operator(hw_id, op_id):
    class VisualisationOperator(bpy.types.Operator):
        bl_idname = f"pigeons.visualisation_operator_{hw_id}_{op_id}"
        bl_label = "Visual OP"

        methodID: bpy.props.IntProperty()
        objectName: bpy.props.StringProperty()
        dataID: bpy.props.IntProperty()

        def execute(self, context):
            selectPolygon(self.objectName, self.dataID)
            return {"FINISHED"}

    return VisualisationOperator


def create_show_details_operator(hw_id, op_id):
    class ShowDetailsOperator(bpy.types.Operator):
        bl_idname = f"pigeons.show_details_operator_{hw_id}_{op_id}"
        bl_label = ""

        message: bpy.props.StringProperty()

        def execute(self, context):
            return {"FINISHED"}

        @classmethod
        def description(cls, context, properties):
            return remove_trailing_dot(properties.message)

    return ShowDetailsOperator


def create_traceback_operator(hw_id, op_id):  # TODO: test id should be here
    class TracebackOperator(bpy.types.Operator):
        bl_idname = f"pigeons.traceback_operator_{hw_id}_{op_id}"
        bl_label = f"Copy Traceback\n"
        tracback_op_id = op_id
        hw_op_id = hw_id

        def execute(self, context):
            homework = tests.TEST_REGISTRY[self.hw_op_id]
            utils.copy_to_clipboard(homework[self.tracback_op_id].traceback)
            return {"FINISHED"}

        @classmethod
        def description(cls, context, properties):
            homework = tests.TEST_REGISTRY[cls.hw_op_id]
            return remove_trailing_dot(homework[cls.tracback_op_id].traceback)

    return TracebackOperator


class RunTestsPanel(bpy.types.Panel):
    bl_label = "Tests"
    bl_idname = "PIGEONS_PT_tests"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PIGEO'n'S"

    def draw(self, context):
        layout = self.layout
        released_version = updates.check_released_version()
        row = layout.row(align=True)
        if updates.version is None or released_version is None:
            row.alert = True
            row.label(
                text="Unable to check for updates. Check manually using the preferences panel."
            )
        elif released_version > updates.version:
            row.alert = True
            row.label(text="New version of PIGEOnS is available.")
            row = layout.row()
            row.alert = True
            row.label(text=f"Released: {released_version}, yours: {updates.version}")
            row = layout.row()
            row.alert = True
            row.label(text="Update using the preferences panel.")
        else:
            row.label(text=f"PIGEOnS are up to date (v{'.'.join(updates.version)})")
        row = layout.row(align=True)
        scene = context.scene
        pigeons = scene.pigeons
        row = layout.row()
        row.prop(pigeons, "homework_selector")

        hw_id = context.scene.pigeons.homework_selector

        currentTests = tests.TEST_REGISTRY[hw_id]
        icons = [
            "ANTIALIASED",
            "CHECKBOX_HLT",
            "QUESTION",
            "CANCEL",
            "PLUGIN",
            "LOOP_FORWARDS",
        ]

        for i in range(len(currentTests)):
            test = currentTests[i]
            row = layout.row()

            if test.state not in {
                tests.TestState.OK,
                tests.TestState.INIT,
                tests.TestState.SKIPPED,
            }:
                row.alert = True

            col1 = row.column()
            col1.scale_x = 7

            col1.label(text=test.label, icon=icons[test.state.value])
            if testRunner.showInfos[i]:
                col1.label(text=test.message)
            col2 = row.column()
            col2.scale_x = 1

            # No issue
            if test.state == tests.TestState.INIT:
                continue

            if test.state == tests.TestState.OK:
                continue

            if test.state == tests.TestState.SKIPPED:
                continue

            # Our issue
            if test.state == tests.TestState.CRASH:
                col2.operator(
                    f"pigeons.traceback_operator_{hw_id}_{i}", text="", icon="COPYDOWN"
                )
                continue

            # Student issue
            if test.state == tests.TestState.ERROR:
                if test.visType != VIS_TYPE.NONE:
                    visualisation_operator = col2.operator(
                        f"pigeons.visualisation_operator_{hw_id}_{i}",
                        text="",
                        icon="OUTLINER_OB_LIGHT",
                    )
                    visualisation_operator.objectName = test.visData.objectName
                    visualisation_operator.dataID = test.visData.dataID  # test.visData

            col3 = row.column()
            show_detail_operator = col3.operator(
                f"pigeons.show_details_operator_{hw_id}_{i}", text="", icon="INFO"
            )
            show_detail_operator.message = (
                test.failedInfo.message
                if test.failedInfo is not None
                else "Unfortunately, we have no more information to give here."
            )

        row = layout.row()
        testsOp = row.operator(
            testRunner.TestRunnerOperator.bl_idname, text="Run Tests"
        )
        testsOp.current_hw = hw_id

        imgCol = self.layout.box().column()
        pigeon = "HELLO"
        if testRunner.TEST_RESULTS_PROPERTY in bpy.context.scene:
            results = bpy.context.scene[testRunner.TEST_RESULTS_PROPERTY]
            if results[tests.TestState.WARNING.value] > 0:
                pigeon = tests.TestState.WARNING.name
            if results[tests.TestState.ERROR.value] > 0:
                pigeon = tests.TestState.ERROR.name
            if results[tests.TestState.CRASH.value] > 0:
                pigeon = tests.TestState.CRASH.name
            if results[tests.TestState.OK.value] + results[
                tests.TestState.SKIPPED.value
            ] == len(currentTests):
                pigeon = tests.TestState.OK.name

        imgCol.label
        imgCol.template_icon(utils.pigeon_collection[pigeon].icon_id, scale=8)
        context.area.tag_redraw()
